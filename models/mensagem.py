from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Any

from sqlalchemy import Column, DateTime, Text
from sqlalchemy import Enum as SQLAlchemyEnum
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from models.conversa import Conversa


class RemetenteMensagem(str, Enum):
    ALUNO = "aluno"
    ASSISTENTE = "assistente"
    SISTEMA = "sistema"
    FERRAMENTA = "ferramenta"


class TipoMensagem(str, Enum):
    TEXTO = "texto"
    AUDIO_TRANSCRITO = "audio_transcrito"
    SISTEMA = "sistema"
    ERRO = "erro"


class Mensagem(SQLModel, table=True):
    __tablename__ = "mensagem"

    id: int | None = Field(default=None, primary_key=True)

    id_conversa: int = Field(
        foreign_key="conversa.id",
        nullable=False,
        index=True,
    )

    remetente: RemetenteMensagem = Field(
        sa_column=Column(
            SQLAlchemyEnum(
                RemetenteMensagem,
                name="remetente_mensagem_enum",
                values_callable=lambda enum: [item.value for item in enum],
            ),
            nullable=False,
        ),
    )

    conteudo: str = Field(
        sa_column=Column(Text, nullable=False)
    )

    tipo: TipoMensagem = Field(
        default=TipoMensagem.TEXTO,
        sa_column=Column(
            SQLAlchemyEnum(
                TipoMensagem,
                name="tipo_mensagem_enum",
                values_callable=lambda enum: [item.value for item in enum],
            ),
            nullable=False,
        ),
    )

    metadata_json: dict[str, Any] | None = Field(
        default=None,
        sa_column=Column(JSONB, nullable=True),
    )

    criado_em: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime, nullable=False),
    )

    conversa: "Conversa | None" = Relationship(back_populates="mensagens")
