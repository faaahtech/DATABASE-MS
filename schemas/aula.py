from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import Column, Date, String, Text, UniqueConstraint
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from schemas.oferta_disciplina import OfertaDisciplina
    from schemas.presenca import Presenca


class Aula(SQLModel, table=True):
    __tablename__ = "aula"

    __table_args__ = (
        UniqueConstraint(
            "id_oferta_disciplina",
            "data",
            "assunto",
            name="uq_aula_oferta_data_assunto",
        ),
    )

    id: int | None = Field(default=None, primary_key=True)

    id_oferta_disciplina: int = Field(
        foreign_key="oferta_disciplina.id",
        nullable=False,
        index=True,
    )

    data: date = Field(
        sa_column=Column(Date, nullable=False)
    )

    assunto: str = Field(
        sa_column=Column(String(255), nullable=False)
    )

    descricao: str | None = Field(
        default=None,
        sa_column=Column(Text, nullable=True),
    )

    oferta_disciplina: "OfertaDisciplina | None" = Relationship(back_populates="aulas")
    presencas: list["Presenca"] = Relationship(back_populates="aula")
