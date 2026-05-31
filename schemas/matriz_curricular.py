from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import Column, Integer
from sqlalchemy import Enum as SQLAlchemyEnum
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from schemas.disciplina import Disciplina


class StatusMatrizCurricular(str, Enum):
    ATIVO = "ativo"
    INATIVO = "inativo"


class MatrizCurricular(SQLModel, table=True):
    __tablename__ = "matriz_curricular"

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

    semestre_recomendado: int = Field(nullable=False)

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

    disciplina: "Disciplina | None" = Relationship(
        back_populates="matrizes_curriculares"
    )