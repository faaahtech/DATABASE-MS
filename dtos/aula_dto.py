from datetime import date

from sqlmodel import SQLModel


class AulaCreate(SQLModel):
    id_oferta_disciplina: int
    data: date
    assunto: str
    descricao: str | None = None


class AulaRead(SQLModel):
    id: int
    id_oferta_disciplina: int
    data: date
    assunto: str
    descricao: str | None = None


class AulaUpdate(SQLModel):
    id_oferta_disciplina: int | None = None
    data: date | None = None
    assunto: str | None = None
    descricao: str | None = None
