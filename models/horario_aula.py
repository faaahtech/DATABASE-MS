from datetime import time
from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import Column, String, Time, UniqueConstraint
from sqlalchemy import Enum as SQLAlchemyEnum
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from schemas.oferta_disciplina import OfertaDisciplina


class DiaSemana(str, Enum):
    SEGUNDA = "segunda"
    TERCA = "terca"
    QUARTA = "quarta"
    QUINTA = "quinta"
    SEXTA = "sexta"
    SABADO = "sabado"
    DOMINGO = "domingo"


class HorarioAula(SQLModel, table=True):
    __tablename__ = "horario_aula"

    __table_args__ = (
        UniqueConstraint(
            "dia_semana",
            "hora_inicio",
            "hora_fim",
            "sala",
            name="uq_horario_aula_dia_horario_sala",
        ),
    )

    id: int | None = Field(default=None, primary_key=True)

    id_oferta_disciplina: int = Field(
        foreign_key="oferta_disciplina.id",
        nullable=False,
        index=True,
    )

    dia_semana: DiaSemana = Field(
        sa_column=Column(
            SQLAlchemyEnum(
                DiaSemana,
                name="dia_semana_enum",
                values_callable=lambda enum: [item.value for item in enum],
            ),
            nullable=False,
        ),
    )

    hora_inicio: time = Field(
        sa_column=Column(Time, nullable=False)
    )

    hora_fim: time = Field(
        sa_column=Column(Time, nullable=False)
    )

    sala: str = Field(
        sa_column=Column(String(50), nullable=False)
    )

    oferta_disciplina: "OfertaDisciplina | None" = Relationship(back_populates="horarios_aula")
