from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import Column, DateTime, UniqueConstraint
from sqlalchemy import Enum as SQLAlchemyEnum
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from models.matricula_curso import MatriculaCurso
    from models.nota import Nota
    from models.oferta_disciplina import OfertaDisciplina
    from models.presenca import Presenca


class StatusMatriculaDisciplina(str, Enum):
    CURSANDO = "cursando"
    APROVADO = "aprovado"
    REPROVADO = "reprovado"
    TRANCADO = "trancado"
    CANCELADO = "cancelado"


class MatriculaDisciplina(SQLModel, table=True):
    __tablename__ = "matricula_disciplina"

    __table_args__ = (
        UniqueConstraint(
            "id_matricula_curso",
            "id_oferta_disciplina",
            name="uq_matricula_disciplina_matricula_oferta",
        ),
    )

    id: int | None = Field(default=None, primary_key=True)

    id_matricula_curso: int = Field(
        foreign_key="matricula_curso.id",
        nullable=False,
        index=True,
    )

    id_oferta_disciplina: int = Field(
        foreign_key="oferta_disciplina.id",
        nullable=False,
        index=True,
    )

    status: StatusMatriculaDisciplina = Field(
        default=StatusMatriculaDisciplina.CURSANDO,
        sa_column=Column(
            SQLAlchemyEnum(
                StatusMatriculaDisciplina,
                name="status_matricula_disciplina_enum",
                values_callable=lambda enum: [item.value for item in enum],
            ),
            nullable=False,
        ),
    )

    data_matricula: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime, nullable=False),
    )

    matricula_curso: "MatriculaCurso | None" = Relationship(back_populates="matriculas_disciplina")
    oferta_disciplina: "OfertaDisciplina | None" = Relationship(back_populates="matriculas_disciplina")
    presencas: list["Presenca"] = Relationship(back_populates="matricula_disciplina")
    notas: list["Nota"] = Relationship(back_populates="matricula_disciplina")
