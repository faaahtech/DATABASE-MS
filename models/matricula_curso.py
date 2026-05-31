from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import Column, CheckConstraint, Integer, String
from sqlalchemy import Enum as SQLAlchemyEnum
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from schemas.aluno import Aluno
    from schemas.curso_unidade import CursoUnidade
    from schemas.matricula_disciplina import MatriculaDisciplina
    from schemas.solicitacao_academica import SolicitacaoAcademica


class PeriodoMatriculaCurso(str, Enum):
    MATUTINO = "matutino"
    VESPERTINO = "vespertino"
    NOTURNO = "noturno"


class StatusMatriculaCurso(str, Enum):
    CURSANDO = "cursando"
    TRANCADO = "trancado"
    CONCLUIDO = "concluido"
    CANCELADO = "cancelado"


class MatriculaCurso(SQLModel, table=True):
    __tablename__ = "matricula_curso"

    __table_args__ = (
        CheckConstraint(
            "semestre_curso > 0",
            name="ck_matricula_curso_semestre_curso",
        ),
        CheckConstraint(
            "semestre_ingresso IN (1, 2)",
            name="ck_matricula_curso_semestre_ingresso",
        ),
    )

    id: int | None = Field(default=None, primary_key=True)

    id_aluno: int = Field(
        foreign_key="aluno.id",
        nullable=False,
        index=True,
    )

    id_curso_unidade: int = Field(
        foreign_key="curso_unidade.id",
        nullable=False,
        index=True,
    )

    ra: str = Field(
        sa_column=Column(String(30), unique=True, nullable=False, index=True)
    )

    semestre_curso: int = Field(
        sa_column=Column(Integer, nullable=False)
    )

    periodo: PeriodoMatriculaCurso = Field(
        sa_column=Column(
            SQLAlchemyEnum(
                PeriodoMatriculaCurso,
                name="periodo_matricula_curso_enum",
                values_callable=lambda enum: [item.value for item in enum],
            ),
            nullable=False,
        ),
    )

    status: StatusMatriculaCurso = Field(
        default=StatusMatriculaCurso.CURSANDO,
        sa_column=Column(
            SQLAlchemyEnum(
                StatusMatriculaCurso,
                name="status_matricula_curso_enum",
                values_callable=lambda enum: [item.value for item in enum],
            ),
            nullable=False,
        ),
    )

    ano_ingresso: int = Field(
        sa_column=Column(Integer, nullable=False)
    )

    semestre_ingresso: int = Field(
        sa_column=Column(Integer, nullable=False)
    )

    aluno: "Aluno | None" = Relationship(back_populates="matriculas_curso")
    curso_unidade: "CursoUnidade | None" = Relationship(back_populates="matriculas_curso")
    matriculas_disciplina: list["MatriculaDisciplina"] = Relationship(back_populates="matricula_curso")
    solicitacoes_academicas: list["SolicitacaoAcademica"] = Relationship(back_populates="matricula_curso")
