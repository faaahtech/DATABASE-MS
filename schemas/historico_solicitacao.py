from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import Column, DateTime, Text
from sqlalchemy import Enum as SQLAlchemyEnum
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from schemas.solicitacao_academica import SolicitacaoAcademica


class StatusHistoricoSolicitacao(str, Enum):
    ABERTA = "aberta"
    AGUARDANDO_SOLICITANTE = "aguardando_solicitante"
    EM_PROCESSAMENTO = "em_processamento"
    CONCLUIDO = "concluido"


class HistoricoSolicitacao(SQLModel, table=True):
    __tablename__ = "historico_solicitacao"

    id: int | None = Field(default=None, primary_key=True)

    id_solicitacao_academica: int = Field(
        foreign_key="solicitacao_academica.id",
        nullable=False,
        index=True,
    )

    status_anterior: StatusHistoricoSolicitacao | None = Field(
        default=None,
        sa_column=Column(
            SQLAlchemyEnum(
                StatusHistoricoSolicitacao,
                name="status_historico_solicitacao_enum",
                values_callable=lambda enum: [item.value for item in enum],
            ),
            nullable=True,
        ),
    )

    status_novo: StatusHistoricoSolicitacao = Field(
        sa_column=Column(
            SQLAlchemyEnum(
                StatusHistoricoSolicitacao,
                name="status_historico_solicitacao_enum",
                values_callable=lambda enum: [item.value for item in enum],
            ),
            nullable=False,
        ),
    )

    observacao: str | None = Field(
        default=None,
        sa_column=Column(Text, nullable=True),
    )

    criado_em: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime, nullable=False),
    )

    solicitacao_academica: "SolicitacaoAcademica | None" = Relationship(back_populates="historicos")
