from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import Column, String
from sqlalchemy import Enum as SQLAlchemyEnum
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from schemas.calendario_academico import CalendarioAcademico
    from schemas.curso_unidade import CursoUnidade
    from schemas.endereco import Endereco


class StatusUnidade(str, Enum):
    ATIVA = "ativa"
    INATIVA = "inativa"


class Unidade(SQLModel, table=True):
    __tablename__ = "unidade"

    id: int | None = Field(default=None, primary_key=True)

    nome: str = Field(
        sa_column=Column(String(255), nullable=False, index=True)
    )

    id_endereco: int = Field(
        foreign_key="endereco.id",
        nullable=False,
        index=True,
    )

    status: StatusUnidade = Field(
        default=StatusUnidade.ATIVA,
        sa_column=Column(
            SQLAlchemyEnum(
                StatusUnidade,
                name="status_unidade_enum",
                values_callable=lambda enum: [item.value for item in enum],
            ),
            nullable=False,
        ),
    )

    endereco: "Endereco | None" = Relationship(back_populates="unidades")
    cursos_unidade: list["CursoUnidade"] = Relationship(back_populates="unidade")
    calendarios_academicos: list["CalendarioAcademico"] = Relationship(back_populates="unidade")
