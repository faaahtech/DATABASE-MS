from datetime import datetime
from enum import Enum

from sqlalchemy import Column, DateTime, String, Text
from sqlalchemy import Enum as SQLAlchemyEnum
from sqlalchemy.dialects.postgresql import ARRAY
from sqlmodel import Field, SQLModel


class CategoriaBaseConhecimento(str, Enum):
    ESTAGIO = "estagio"
    MATRICULA = "matricula"
    DOCUMENTOS = "documentos"
    CALENDARIO = "calendario"
    DISCIPLINA = "disciplina"
    GERAL = "geral"


class StatusBaseConhecimento(str, Enum):
    ATIVO = "ativo"
    INATIVO = "inativo"


class BaseConhecimento(SQLModel, table=True):
    __tablename__ = "base_conhecimento"

    id: int | None = Field(default=None, primary_key=True)

    titulo: str = Field(
        sa_column=Column(String(255), nullable=False, index=True)
    )

    categoria: CategoriaBaseConhecimento = Field(
        sa_column=Column(
            SQLAlchemyEnum(
                CategoriaBaseConhecimento,
                name="categoria_base_conhecimento_enum",
                values_callable=lambda enum: [item.value for item in enum],
            ),
            nullable=False,
        ),
    )

    pergunta_base: str | None = Field(
        default=None,
        sa_column=Column(Text, nullable=True),
    )

    resposta: str = Field(
        sa_column=Column(Text, nullable=False)
    )

    tags: list[str] | None = Field(
        default=None,
        sa_column=Column(ARRAY(String), nullable=True),
    )

    status: StatusBaseConhecimento = Field(
        default=StatusBaseConhecimento.ATIVO,
        sa_column=Column(
            SQLAlchemyEnum(
                StatusBaseConhecimento,
                name="status_base_conhecimento_enum",
                values_callable=lambda enum: [item.value for item in enum],
            ),
            nullable=False,
        ),
    )

    atualizado_em: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime, nullable=False),
    )
