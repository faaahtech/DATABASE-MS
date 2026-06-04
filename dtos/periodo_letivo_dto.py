from datetime import date

from sqlmodel import SQLModel

from models.periodo_letivo import StatusPeriodoLetivo


class PeriodoLetivoCreate(SQLModel):
    ano: int
    semestre: int
    data_inicio: date
    data_fim: date
    status: StatusPeriodoLetivo = StatusPeriodoLetivo.PLANEJADO


class PeriodoLetivoRead(SQLModel):
    id: int
    ano: int
    semestre: int
    data_inicio: date
    data_fim: date
    status: StatusPeriodoLetivo


class PeriodoLetivoUpdate(SQLModel):
    ano: int | None = None
    semestre: int | None = None
    data_inicio: date | None = None
    data_fim: date | None = None
    status: StatusPeriodoLetivo | None = None


class PeriodoLetivoStatusUpdate(SQLModel):
    status: StatusPeriodoLetivo
