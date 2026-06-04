from sqlmodel import SQLModel

from models.professor import StatusProfessor


class ProfessorCreate(SQLModel):
    nome: str
    email: str
    telefone: str | None = None
    status: StatusProfessor = StatusProfessor.ATIVO


class ProfessorRead(SQLModel):
    id: int
    nome: str
    email: str
    telefone: str | None = None
    status: StatusProfessor


class ProfessorUpdate(SQLModel):
    nome: str | None = None
    email: str | None = None
    telefone: str | None = None
    status: StatusProfessor | None = None
