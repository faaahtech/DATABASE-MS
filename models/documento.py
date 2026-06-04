from datetime import datetime
from enum import Enum
from typing import Optional, TYPE_CHECKING

from sqlalchemy import Column, DateTime, String
from sqlalchemy import Enum as SQLAlchemyEnum
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from models.aluno import Aluno
    from models.solicitacao_academica import SolicitacaoAcademica


class TipoDocumento(str, Enum):
    DECLARACAO_MATRICULA = "declaracao_matricula"
    HISTORICO = "historico"
    COMPROVANTE = "comprovante"
    OUTRO = "outro"


class StatusDocumento(str, Enum):
    PENDENTE = "pendente"
    GERADO = "gerado"
    ENVIADO = "enviado"
    REJEITADO = "rejeitado"


class Documento(SQLModel, table=True):
    __tablename__ = "documento"

    id: int | None = Field(default=None, primary_key=True)

    id_solicitacao_academica: int = Field(
        foreign_key="solicitacao_academica.id",
        nullable=False,
        index=True,
    )

    id_aluno: int = Field(
        foreign_key="aluno.id",
        nullable=False,
        index=True,
    )

    tipo: TipoDocumento = Field(
        sa_column=Column(
            SQLAlchemyEnum(
                TipoDocumento,
                name="tipo_documento_enum",
                values_callable=lambda enum: [item.value for item in enum],
            ),
            nullable=False,
        ),
    )

    status: StatusDocumento = Field(
        default=StatusDocumento.PENDENTE,
        sa_column=Column(
            SQLAlchemyEnum(
                StatusDocumento,
                name="status_documento_enum",
                values_callable=lambda enum: [item.value for item in enum],
            ),
            nullable=False,
        ),
    )

    storage_id: str = Field(
        sa_column=Column(String(255), nullable=False, index=True)
    )

    nome_original: str = Field(
        sa_column=Column(String(255), nullable=False)
    )

    mime_type: str = Field(
        sa_column=Column(String(120), nullable=False)
    )

    criado_em: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime, nullable=False),
    )

    solicitacao_academica: Optional["SolicitacaoAcademica"] = Relationship(back_populates="documentos")
    aluno: Optional["Aluno"] = Relationship(back_populates="documentos")
