from datetime import date

from sqlmodel import SQLModel


class PresencaCreate(SQLModel):
    id_matricula_disciplina: int
    id_aula: int
    presente: bool
    justificativa: str | None = None


class PresencaUpdate(SQLModel):
    id_matricula_disciplina: int | None = None
    id_aula: int | None = None
    presente: bool | None = None
    justificativa: str | None = None


class PresencaRead(SQLModel):
    id: int
    id_matricula_disciplina: int
    id_aula: int
    presente: bool
    justificativa: str | None = None


class PresencaPorAlunoRead(SQLModel):
    id: int
    id_aluno: int
    id_matricula_disciplina: int
    id_aula: int
    presente: bool
    justificativa: str | None = None
    data_aula: date | None = None
    assunto_aula: str | None = None
    id_oferta_disciplina: int | None = None
    disciplina_nome: str | None = None
    disciplina_codigo: str | None = None
