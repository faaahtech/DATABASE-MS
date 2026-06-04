from datetime import datetime

from sqlmodel import SQLModel

from models.matricula_disciplina import StatusMatriculaDisciplina


class MatriculaDisciplinaCreate(SQLModel):
    id_matricula_curso: int
    id_oferta_disciplina: int
    status: StatusMatriculaDisciplina = StatusMatriculaDisciplina.CURSANDO


class MatriculaDisciplinaRead(SQLModel):
    id: int
    id_matricula_curso: int
    id_oferta_disciplina: int
    status: StatusMatriculaDisciplina
    data_matricula: datetime


class MatriculaDisciplinaUpdateStatus(SQLModel):
    status: StatusMatriculaDisciplina
