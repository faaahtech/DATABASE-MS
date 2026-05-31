from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import Column, Integer, String
from sqlalchemy import Enum as SQLAlchemyEnum
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from models.matriz_curricular import MatrizCurricular


class StatusDisciplina(str, Enum):
    ATIVO = "ativo"
    INATIVO = "inativo"


class Disciplina(SQLModel, table=True):
    __tablename__ = "disciplina"

    id: int | None = Field(default=None, primary_key=True)

    nome: str = Field(
        sa_column=Column(String(255), nullable=False)
    )

    codigo: str = Field(
        sa_column=Column(String(20), unique=True, nullable=False, index=True)
    )

    carga_horaria: int = Field(
        sa_column=Column(
            Integer,
            nullable=False,
            comment="Carga horária em horas",
        )
    )

    status: StatusDisciplina = Field(
        default=StatusDisciplina.ATIVO,
        sa_column=Column(
            SQLAlchemyEnum(
                StatusDisciplina,
                name="status_disciplina_enum",
                values_callable=lambda enum: [item.value for item in enum],
            ),
            nullable=False,
        ),
    )

    matrizes_curriculares: list["MatrizCurricular"] = Relationship(
        back_populates="disciplina"
    )