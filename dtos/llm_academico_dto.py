from sqlmodel import Field, SQLModel

from models.matricula_curso import PeriodoMatriculaCurso, StatusMatriculaCurso


class TransferirHorarioRequest(SQLModel):
    id_curso_unidade_destino: int
    # Campo opcional para permitir troca real de horário/turno no schema atual.
    # O payload antigo {"id_curso_unidade_destino": 1} continua válido.
    periodo_destino: PeriodoMatriculaCurso | None = None


class AlunoTransferenciaRead(SQLModel):
    id: int
    nome: str


class MatriculaAtualTransferenciaRead(SQLModel):
    id: int
    id_aluno: int
    id_curso_unidade: int
    ra: str
    semestre_curso: int
    periodo: PeriodoMatriculaCurso
    status: StatusMatriculaCurso


class OpcaoTransferenciaHorarioRead(SQLModel):
    option_id: int
    id_curso_unidade: int
    curso: str
    sigla: str
    unidade: str
    periodo: PeriodoMatriculaCurso
    label: str


class OpcoesTransferenciaHorarioRead(SQLModel):
    aluno: AlunoTransferenciaRead
    matricula_atual: MatriculaAtualTransferenciaRead
    options: list[OpcaoTransferenciaHorarioRead] = Field(default_factory=list)


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
