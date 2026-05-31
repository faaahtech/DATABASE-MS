from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import Column, Numeric, UniqueConstraint
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from models.avaliacao import Avaliacao
    from models.matricula_disciplina import MatriculaDisciplina


class Nota(SQLModel, table=True):
    __tablename__ = "nota"

    __table_args__ = (
        UniqueConstraint(
            "id_matricula_disciplina",
            "id_avaliacao",
            name="uq_nota_matricula_avaliacao",
        ),
    )

    id: int | None = Field(default=None, primary_key=True)

    id_avaliacao: int = Field(
        foreign_key="avaliacao.id",
        nullable=False,
        index=True,
    )

    id_matricula_disciplina: int = Field(
        foreign_key="matricula_disciplina.id",
        nullable=False,
        index=True,
    )

    valor: Decimal = Field(
        sa_column=Column(Numeric(5, 2), nullable=False)
    )

    avaliacao: "Avaliacao | None" = Relationship(back_populates="notas")
    matricula_disciplina: "MatriculaDisciplina | None" = Relationship(back_populates="notas")
