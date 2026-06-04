from typing import Optional, TYPE_CHECKING

from sqlalchemy import Column, Text, UniqueConstraint
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from models.aula import Aula
    from models.matricula_disciplina import MatriculaDisciplina


class Presenca(SQLModel, table=True):
    __tablename__ = "presenca"

    __table_args__ = (
        UniqueConstraint(
            "id_matricula_disciplina",
            "id_aula",
            name="uq_presenca_matricula_aula",
        ),
    )

    id: int | None = Field(default=None, primary_key=True)

    id_matricula_disciplina: int = Field(
        foreign_key="matricula_disciplina.id",
        nullable=False,
        index=True,
    )

    id_aula: int = Field(
        foreign_key="aula.id",
        nullable=False,
        index=True,
    )

    presente: bool = Field(default=False, nullable=False)

    justificativa: str | None = Field(
        default=None,
        sa_column=Column(Text, nullable=True),
    )

    matricula_disciplina: Optional["MatriculaDisciplina"] = Relationship(back_populates="presencas")
    aula: Optional["Aula"] = Relationship(back_populates="presencas")
