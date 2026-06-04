from sqlmodel import SQLModel

from models.matriz_curricular import StatusMatrizCurricular


class MatrizCurricularCreate(SQLModel):
    id_curso_unidade: int
    id_disciplina: int
    semestre_recomendado: int
    obrigatoria: bool = True
    status: StatusMatrizCurricular = StatusMatrizCurricular.ATIVO


class MatrizCurricularRead(SQLModel):
    id: int
    id_curso_unidade: int
    id_disciplina: int
    semestre_recomendado: int
    obrigatoria: bool
    status: StatusMatrizCurricular


class MatrizCurricularUpdate(SQLModel):
    id_curso_unidade: int | None = None
    id_disciplina: int | None = None
    semestre_recomendado: int | None = None
    obrigatoria: bool | None = None
    status: StatusMatrizCurricular | None = None
