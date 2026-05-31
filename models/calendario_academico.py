from datetime import date
from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import Column, Date, Text, String, CheckConstraint, Integer
from sqlalchemy import Enum as SQLAlchemyEnum
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from models.unidade import Unidade


class TipoCalendarioAcademico(str, Enum):
    PRAZO = "prazo"
    FERIADO = "feriado"
    PROVA = "prova"
    REMATRICULA = "rematricula"
    TRANCAMENTO = "trancamento"
    EVENTO = "evento"


class StatusCalendarioAcademico(str, Enum):
    ATIVO = "ativo"
    CANCELADO = "cancelado"
    ENCERRADO = "encerrado"


class CalendarioAcademico(SQLModel, table=True):
    __tablename__ = "calendario_academico"

    __table_args__ = (
        CheckConstraint(
            "periodo IS NULL OR periodo IN (1, 2)",
            name="ck_calendario_academico_periodo",
        ),
    )

    id: int | None = Field(default=None, primary_key=True)

    id_unidade: int = Field(
        foreign_key="unidade.id",
        nullable=False,
        index=True,
    )

    titulo: str = Field(
        sa_column=Column(String(255), nullable=False)
    )

    descricao: str | None = Field(
        default=None,
        sa_column=Column(Text, nullable=True),
    )

    tipo: TipoCalendarioAcademico = Field(
        sa_column=Column(
            SQLAlchemyEnum(
                TipoCalendarioAcademico,
                name="tipo_calendario_academico_enum",
                values_callable=lambda enum: [item.value for item in enum],
            ),
            nullable=False,
        ),
    )

    data_inicio: date = Field(
        sa_column=Column(Date, nullable=False)
    )

    data_fim: date | None = Field(
        default=None,
        sa_column=Column(Date, nullable=True),
    )

    periodo: int | None = Field(
        default=None,
        sa_column=Column(Integer, nullable=True),
    )

    status: StatusCalendarioAcademico = Field(
        default=StatusCalendarioAcademico.ATIVO,
        sa_column=Column(
            SQLAlchemyEnum(
                StatusCalendarioAcademico,
                name="status_calendario_academico_enum",
                values_callable=lambda enum: [item.value for item in enum],
            ),
            nullable=False,
        ),
    )

    unidade: "Unidade | None" = Relationship(back_populates="calendarios_academicos")
