from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import Column, DateTime
from sqlalchemy import Enum as SQLAlchemyEnum
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from schemas.aluno import Aluno
    from schemas.mensagem import Mensagem


class StatusConversa(str, Enum):
    ATIVO = "ativo"
    ENCERRADO = "encerrado"
    REABERTO = "reaberto"


class Conversa(SQLModel, table=True):
    __tablename__ = "conversa"

    id: int | None = Field(default=None, primary_key=True)

    id_aluno: int = Field(
        foreign_key="aluno.id",
        nullable=False,
        index=True,
    )

    status: StatusConversa = Field(
        default=StatusConversa.ATIVO,
        sa_column=Column(
            SQLAlchemyEnum(
                StatusConversa,
                name="status_conversa_enum",
                values_callable=lambda enum: [item.value for item in enum],
            ),
            nullable=False,
        ),
    )

    criado_em: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime, nullable=False),
    )

    finalizado_em: datetime | None = Field(
        default=None,
        sa_column=Column(DateTime, nullable=True),
    )

    aluno: "Aluno | None" = Relationship(back_populates="conversas")
    mensagens: list["Mensagem"] = Relationship(back_populates="conversa")
