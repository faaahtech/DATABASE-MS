from datetime import date

from sqlmodel import Field, SQLModel

from models.curso import StatusCurso
from models.curso_unidade import (
    ModalidadeCursoUnidade,
    NivelCursoUnidade,
    StatusCursoUnidade,
)
from models.disciplina import StatusDisciplina
from models.matricula_curso import PeriodoMatriculaCurso, StatusMatriculaCurso
from models.oferta_disciplina import PeriodoOfertaDisciplina, StatusOfertaDisciplina
from models.periodo_letivo import StatusPeriodoLetivo
from models.professor import StatusProfessor
from models.unidade import StatusUnidade


class CursoRead(SQLModel):
    id: int
    nome: str
    sigla: str
    duracao_semestres: int
    status: StatusCurso


class UnidadeRead(SQLModel):
    id: int
    nome: str
    id_endereco: int
    status: StatusUnidade


class DisciplinaCursoUnidadeRead(SQLModel):
    id_disciplina: int
    nome: str
    codigo: str
    carga_horaria: int
    status: StatusDisciplina
    id_matriz_curricular: int | None = None
    semestre_recomendado: int | None = None
    obrigatoria: bool | None = None


class PeriodoLetivoAtivoRead(SQLModel):
    id: int
    ano: int
    semestre: int
    data_inicio: date
    data_fim: date
    status: StatusPeriodoLetivo


class OfertaDisciplinaRead(SQLModel):
    id: int
    id_matriz_curricular: int
    id_professor: int
    id_periodo_letivo: int
    codigo_oferta: str
    vagas_total: int
    vagas_disponiveis: int
    periodo: PeriodoOfertaDisciplina
    status: StatusOfertaDisciplina
    disciplina_nome: str | None = None
    disciplina_codigo: str | None = None
    professor_nome: str | None = None


class CursoUnidadeDetalheRead(SQLModel):
    id: int
    id_curso: int
    id_unidade: int
    nivel: NivelCursoUnidade
    modalidade: ModalidadeCursoUnidade
    status: StatusCursoUnidade
    curso_nome: str | None = None
    curso_sigla: str | None = None
    unidade_nome: str | None = None


class ProfessorConsultaRead(SQLModel):
    id: int
    nome: str
    email: str
    telefone: str | None = None
    status: StatusProfessor


class MatriculaCursoRead(SQLModel):
    id: int
    id_aluno: int
    id_curso_unidade: int
    ra: str
    semestre_curso: int
    periodo: PeriodoMatriculaCurso
    status: StatusMatriculaCurso
    ano_ingresso: int
    semestre_ingresso: int


class ResumoAlunoRead(SQLModel):
    id_aluno: int
    nome: str
    email: str
    cpf: str
    matriculas: list[MatriculaCursoRead] = Field(default_factory=list)


class GradeResumoSemestreItemRead(SQLModel):
    disciplina: str
    professor: str | None = None
    horario: str | None = None
    dia_semana: str | None = None
    sala: str | None = None


class ResumoSemestreAtualRead(SQLModel):
    id_aluno: int
    aluno_nome: str
    semestre_curso: int
    periodo_letivo: str
    grade: list[GradeResumoSemestreItemRead] = Field(default_factory=list)
