from sqlmodel import SQLModel

from models.oferta_disciplina import PeriodoOfertaDisciplina, StatusOfertaDisciplina


class OfertaDisciplinaCreate(SQLModel):
    id_matriz_curricular: int
    id_professor: int
    id_periodo_letivo: int
    codigo_oferta: str
    vagas_total: int
    vagas_disponiveis: int
    periodo: PeriodoOfertaDisciplina
    status: StatusOfertaDisciplina = StatusOfertaDisciplina.PLANEJADA


class OfertaDisciplinaRead(SQLModel):
    id: int
    id_matriz_curricular: int
    id_professor: int
    id_periodo_letivo: int
    codigo_oferta: str
    vagas_total: int
    vagas_disponiveis: int
    periodo: PeriodoOfertaDisciplina
    status: StatusOfertaDisciplina


class OfertaDisciplinaUpdate(SQLModel):
    id_matriz_curricular: int | None = None
    id_professor: int | None = None
    id_periodo_letivo: int | None = None
    codigo_oferta: str | None = None
    vagas_total: int | None = None
    vagas_disponiveis: int | None = None
    periodo: PeriodoOfertaDisciplina | None = None
    status: StatusOfertaDisciplina | None = None
