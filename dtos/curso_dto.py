from sqlmodel import SQLModel

from models.curso import StatusCurso


class CursoCreate(SQLModel):
    nome: str
    sigla: str
    duracao_semestres: int
    status: StatusCurso = StatusCurso.ATIVO


class CursoRead(SQLModel):
    id: int
    nome: str
    sigla: str
    duracao_semestres: int
    status: StatusCurso


class CursoUpdate(SQLModel):
    nome: str | None = None
    sigla: str | None = None
    duracao_semestres: int | None = None
    status: StatusCurso | None = None
