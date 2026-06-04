from datetime import date

from sqlmodel import SQLModel

from models.aluno import StatusAluno


class AlunoCreate(SQLModel):
    id_endereco: int
    nome: str
    cpf: str
    data_nascimento: date
    email: str
    telefone: str | None = None
    status: StatusAluno = StatusAluno.ATIVO


class AlunoRead(SQLModel):
    id: int
    id_endereco: int
    nome: str
    cpf: str
    data_nascimento: date
    email: str
    telefone: str | None = None
    status: StatusAluno


class AlunoUpdate(SQLModel):
    nome: str | None = None
    cpf: str | None = None
    data_nascimento: date | None = None
    email: str | None = None
    telefone: str | None = None
    status: StatusAluno | None = None
    id_endereco: int | None = None


class AlunoListItem(SQLModel):
    id: int
    nome: str
    cpf: str
    email: str
    telefone: str | None = None
    status: StatusAluno
