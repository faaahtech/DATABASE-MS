from datetime import date
from enum import Enum

from sqlalchemy import Column, Date, Integer, CheckConstraint, UniqueConstraint
from sqlalchemy import Enum as SQLAlchemyEnum
from sqlmodel import Field, Relationship, SQLModel
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from schemas.oferta_disciplina import OfertaDisciplina


class StatusPeriodoLetivo(str, Enum):
    PLANEJADO = "planejado"
    ATIVO = "ativo"
    ENCERRADO = "encerrado"


class PeriodoLetivo(SQLModel, table=True):
    __tablename__ = "periodo_letivo"

    __table_args__ = (
        UniqueConstraint(
            "ano",
            "semestre",
            name="uq_periodo_letivo_ano_semestre",
        ),
        CheckConstraint(
            "semestre IN (1, 2)",
            name="ck_periodo_letivo_semestre",
        ),
        CheckConstraint(
            "data_fim > data_inicio",
            name="ck_periodo_letivo_datas",
        ),
    )

    id: int | None = Field(default=None, primary_key=True)

    ano: int = Field(
        sa_column=Column(Integer, nullable=False)
    )

    semestre: int = Field(
        sa_column=Column(Integer, nullable=False)
    )

    data_inicio: date = Field(
        sa_column=Column(Date, nullable=False)
    )

    data_fim: date = Field(
        sa_column=Column(Date, nullable=False)
    )

    status: StatusPeriodoLetivo = Field(
        default=StatusPeriodoLetivo.PLANEJADO,
        sa_column=Column(
            SQLAlchemyEnum(
                StatusPeriodoLetivo,
                name="status_periodo_letivo_enum",
                values_callable=lambda enum: [item.value for item in enum],
            ),
            nullable=False,
        ),
    )

    ofertas_disciplina: list["OfertaDisciplina"] = Relationship(back_populates="periodo_letivo")
