from datetime import date

from sqlmodel import SQLModel

from models.calendario_academico import (
    StatusCalendarioAcademico,
    TipoCalendarioAcademico,
)


class CalendarioAcademicoCreate(SQLModel):
    id_unidade: int
    titulo: str
    descricao: str | None = None
    tipo: TipoCalendarioAcademico
    data_inicio: date
    data_fim: date | None = None
    periodo: int | None = None
    status: StatusCalendarioAcademico = StatusCalendarioAcademico.ATIVO


class CalendarioAcademicoRead(SQLModel):
    id: int
    id_unidade: int
    titulo: str
    descricao: str | None = None
    tipo: TipoCalendarioAcademico
    data_inicio: date
    data_fim: date | None = None
    periodo: int | None = None
    status: StatusCalendarioAcademico


class CalendarioAcademicoUpdate(SQLModel):
    id_unidade: int | None = None
    titulo: str | None = None
    descricao: str | None = None
    tipo: TipoCalendarioAcademico | None = None
    data_inicio: date | None = None
    data_fim: date | None = None
    periodo: int | None = None
    status: StatusCalendarioAcademico | None = None
