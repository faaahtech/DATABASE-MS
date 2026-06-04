from datetime import datetime
from enum import Enum
from typing import Optional, TYPE_CHECKING

from sqlalchemy import Column, DateTime, String, Text
from sqlalchemy import Enum as SQLAlchemyEnum
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from models.aluno import Aluno
    from models.documento import Documento
    from models.historico_solicitacao import HistoricoSolicitacao
    from models.matricula_curso import MatriculaCurso


class TipoSolicitacaoAcademica(str, Enum):
    DECLARACAO = "declaracao"
    TRANCAMENTO = "trancamento"
    TRANSFERENCIA_HORARIO = "transferencia_horario"
    HISTORICO = "historico"
    ESTAGIO = "estagio"
    OUTROS = "outros"


class StatusSolicitacaoAcademica(str, Enum):
    ABERTA = "aberta"
    AGUARDANDO_SOLICITANTE = "aguardando_solicitante"
    EM_PROCESSAMENTO = "em_processamento"
    CONCLUIDO = "concluido"


class OrigemSolicitacaoAcademica(str, Enum):
    CHATBOT = "chatbot"
    SECRETARIA = "secretaria"
    SISTEMA = "sistema"


class SolicitacaoAcademica(SQLModel, table=True):
    __tablename__ = "solicitacao_academica"

    id: int | None = Field(default=None, primary_key=True)

    id_aluno: int = Field(
        foreign_key="aluno.id",
        nullable=False,
        index=True,
    )

    id_matricula_curso: int | None = Field(
        default=None,
        foreign_key="matricula_curso.id",
        index=True,
    )

    tipo: TipoSolicitacaoAcademica = Field(
        sa_column=Column(
            SQLAlchemyEnum(
                TipoSolicitacaoAcademica,
                name="tipo_solicitacao_academica_enum",
                values_callable=lambda enum: [item.value for item in enum],
            ),
            nullable=False,
        ),
    )

    protocolo: str = Field(
        sa_column=Column(String(50), unique=True, nullable=False, index=True)
    )

    status: StatusSolicitacaoAcademica = Field(
        default=StatusSolicitacaoAcademica.ABERTA,
        sa_column=Column(
            SQLAlchemyEnum(
                StatusSolicitacaoAcademica,
                name="status_solicitacao_academica_enum",
                values_callable=lambda enum: [item.value for item in enum],
            ),
            nullable=False,
        ),
    )

    origem: OrigemSolicitacaoAcademica = Field(
        default=OrigemSolicitacaoAcademica.CHATBOT,
        sa_column=Column(
            SQLAlchemyEnum(
                OrigemSolicitacaoAcademica,
                name="origem_solicitacao_academica_enum",
                values_callable=lambda enum: [item.value for item in enum],
            ),
            nullable=False,
        ),
    )

    criado_em: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime, nullable=False),
    )

    atualizado_em: datetime | None = Field(
        default=None,
        sa_column=Column(DateTime, nullable=True),
    )

    observacao: str | None = Field(
        default=None,
        sa_column=Column(Text, nullable=True),
    )

    aluno: Optional["Aluno"] = Relationship(back_populates="solicitacoes_academicas")
    matricula_curso: Optional["MatriculaCurso"] = Relationship(back_populates="solicitacoes_academicas")
    historicos: list["HistoricoSolicitacao"] = Relationship(back_populates="solicitacao_academica")
    documentos: list["Documento"] = Relationship(back_populates="solicitacao_academica")
