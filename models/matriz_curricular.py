from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import Column, Integer, CheckConstraint
from sqlalchemy import Enum as SQLAlchemyEnum
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from schemas.curso_unidade import CursoUnidade
    from schemas.disciplina import Disciplina
    from schemas.oferta_disciplina import OfertaDisciplina


class StatusMatrizCurricular(str, Enum):
    ATIVO = "ativo"
    INATIVO = "inativo"


class MatrizCurricular(SQLModel, table=True):
    __tablename__ = "matriz_curricular"

    __table_args__ = (
        CheckConstraint(
            "semestre_recomendado > 0",
            name="ck_matriz_curricular_semestre_recomendado",
        ),
    )

    id: int | None = Field(default=None, primary_key=True)

    id_curso_unidade: int = Field(
        foreign_key="curso_unidade.id",
        nullable=False,
        index=True,
    )

    id_disciplina: int = Field(
        foreign_key="disciplina.id",
        nullable=False,
        index=True,
    )

    semestre_recomendado: int = Field(
        sa_column=Column(Integer, nullable=False)
    )

    obrigatoria: bool = Field(default=True, nullable=False)

    status: StatusMatrizCurricular = Field(
        default=StatusMatrizCurricular.ATIVO,
        sa_column=Column(
            SQLAlchemyEnum(
                StatusMatrizCurricular,
                name="status_matriz_curricular_enum",
                values_callable=lambda enum: [item.value for item in enum],
            ),
            nullable=False,
        ),
    )

    curso_unidade: "CursoUnidade | None" = Relationship(back_populates="matrizes_curriculares")
    disciplina: "Disciplina | None" = Relationship(back_populates="matrizes_curriculares")
    ofertas_disciplina: list["OfertaDisciplina"] = Relationship(back_populates="matriz_curricular")
