from datetime import date
from decimal import Decimal
from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import Column, Date, Numeric, String, UniqueConstraint
from sqlalchemy import Enum as SQLAlchemyEnum
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from models.nota import Nota
    from models.oferta_disciplina import OfertaDisciplina


class TipoAvaliacao(str, Enum):
    PROVA = "prova"
    TRABALHO = "trabalho"
    SEMINARIO = "seminario"
    ATIVIDADE = "atividade"
    PROJETO = "projeto"


class Avaliacao(SQLModel, table=True):
    __tablename__ = "avaliacao"

    __table_args__ = (
        UniqueConstraint(
            "id_oferta_disciplina",
            "nome",
            name="uq_avaliacao_oferta_nome",
        ),
    )

    id: int | None = Field(default=None, primary_key=True)

    id_oferta_disciplina: int = Field(
        foreign_key="oferta_disciplina.id",
        nullable=False,
        index=True,
    )

    nome: str = Field(
        sa_column=Column(String(120), nullable=False)
    )

    tipo: TipoAvaliacao = Field(
        sa_column=Column(
            SQLAlchemyEnum(
                TipoAvaliacao,
                name="tipo_avaliacao_enum",
                values_callable=lambda enum: [item.value for item in enum],
            ),
            nullable=False,
        ),
    )

    peso: Decimal = Field(
        sa_column=Column(Numeric(5, 2), nullable=False)
    )

    data: date = Field(
        sa_column=Column(Date, nullable=False)
    )

    oferta_disciplina: "OfertaDisciplina | None" = Relationship(back_populates="avaliacoes")
    notas: list["Nota"] = Relationship(back_populates="avaliacao")
