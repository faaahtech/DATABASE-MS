from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import Column, Integer, String
from sqlalchemy import Enum as SQLAlchemyEnum
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from schemas.curso_unidade import CursoUnidade


class StatusCurso(str, Enum):
    ATIVO = "ativo"
    INATIVO = "inativo"


class Curso(SQLModel, table=True):
    __tablename__ = "curso"

    id: int | None = Field(default=None, primary_key=True)

    nome: str = Field(
        sa_column=Column(String(255), nullable=False, index=True)
    )

    sigla: str = Field(
        sa_column=Column(String(20), unique=True, nullable=False, index=True)
    )

    duracao_semestres: int = Field(
        sa_column=Column(Integer, nullable=False)
    )

    status: StatusCurso = Field(
        default=StatusCurso.ATIVO,
        sa_column=Column(
            SQLAlchemyEnum(
                StatusCurso,
                name="status_curso_enum",
                values_callable=lambda enum: [item.value for item in enum],
            ),
            nullable=False,
        ),
    )

    cursos_unidade: list["CursoUnidade"] = Relationship(back_populates="curso")
