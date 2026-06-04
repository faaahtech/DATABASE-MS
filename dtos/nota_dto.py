from datetime import date
from decimal import Decimal

from sqlmodel import SQLModel


class NotaCreate(SQLModel):
    id_avaliacao: int
    id_matricula_disciplina: int
    valor: Decimal


class NotaUpdate(SQLModel):
    id_avaliacao: int | None = None
    id_matricula_disciplina: int | None = None
    valor: Decimal | None = None


class NotaRead(SQLModel):
    id: int
    id_avaliacao: int
    id_matricula_disciplina: int
    valor: Decimal


class NotaPorAlunoRead(SQLModel):
    id: int
    id_aluno: int
    id_avaliacao: int
    id_matricula_disciplina: int
    valor: Decimal
    avaliacao_nome: str | None = None
    avaliacao_data: date | None = None
    id_oferta_disciplina: int | None = None
    disciplina_nome: str | None = None
    disciplina_codigo: str | None = None
