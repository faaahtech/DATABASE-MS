from sqlmodel import SQLModel
from models.matricula_curso import PeriodoMatriculaCurso, StatusMatriculaCurso

class MatriculaCursoCreate(SQLModel):
    id_aluno:int; id_curso_unidade:int; ra:str; semestre_curso:int; periodo:PeriodoMatriculaCurso; status:StatusMatriculaCurso=StatusMatriculaCurso.CURSANDO; ano_ingresso:int; semestre_ingresso:int
class MatriculaCursoRead(MatriculaCursoCreate):
    id:int
class MatriculaCursoUpdateStatus(SQLModel):
    status:StatusMatriculaCurso
