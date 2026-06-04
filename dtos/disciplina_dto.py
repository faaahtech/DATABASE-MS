from sqlmodel import SQLModel

from models.disciplina import StatusDisciplina


class DisciplinaCreate(SQLModel):
    nome: str
    codigo: str
    carga_horaria: int
    status: StatusDisciplina = StatusDisciplina.ATIVO


class DisciplinaRead(SQLModel):
    id: int
    nome: str
    codigo: str
    carga_horaria: int
    status: StatusDisciplina


class DisciplinaUpdate(SQLModel):
    nome: str | None = None
    codigo: str | None = None
    carga_horaria: int | None = None
    status: StatusDisciplina | None = None
