from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import Column, UniqueConstraint
from sqlalchemy import Enum as SQLAlchemyEnum
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from models.curso import Curso
    from models.matriz_curricular import MatrizCurricular
    from models.matricula_curso import MatriculaCurso
    from models.unidade import Unidade


class StatusCursoUnidade(str, Enum):
    ATIVO = "ativo"
    INATIVO = "inativo"


class NivelCursoUnidade(str, Enum):
    TECNICO = "tecnico"
    TECNOLOGO = "tecnologo"
    GRADUACAO = "graduacao"


class ModalidadeCursoUnidade(str, Enum):
    PRESENCIAL = "presencial"
    EAD = "ead"
    HIBRIDO = "hibrido"


class CursoUnidade(SQLModel, table=True):
    __tablename__ = "curso_unidade"

    __table_args__ = (
        UniqueConstraint(
            "id_curso",
            "id_unidade",
            "nivel",
            "modalidade",
            name="uq_curso_unidade_curso_unidade_nivel_modalidade",
        ),
    )

    id: int | None = Field(default=None, primary_key=True)

    id_curso: int = Field(
        foreign_key="curso.id",
        nullable=False,
        index=True,
    )

    id_unidade: int = Field(
        foreign_key="unidade.id",
        nullable=False,
        index=True,
    )

    status: StatusCursoUnidade = Field(
        default=StatusCursoUnidade.ATIVO,
        sa_column=Column(
            SQLAlchemyEnum(
                StatusCursoUnidade,
                name="status_curso_unidade_enum",
                values_callable=lambda enum: [item.value for item in enum],
            ),
            nullable=False,
        ),
    )

    nivel: NivelCursoUnidade = Field(
        sa_column=Column(
            SQLAlchemyEnum(
                NivelCursoUnidade,
                name="nivel_curso_unidade_enum",
                values_callable=lambda enum: [item.value for item in enum],
            ),
            nullable=False,
        ),
    )

    modalidade: ModalidadeCursoUnidade = Field(
        sa_column=Column(
            SQLAlchemyEnum(
                ModalidadeCursoUnidade,
                name="modalidade_curso_unidade_enum",
                values_callable=lambda enum: [item.value for item in enum],
            ),
            nullable=False,
        ),
    )

    curso: "Curso | None" = Relationship(back_populates="cursos_unidade")
    unidade: "Unidade | None" = Relationship(back_populates="cursos_unidade")
    matrizes_curriculares: list["MatrizCurricular"] = Relationship(back_populates="curso_unidade")
    matriculas_curso: list["MatriculaCurso"] = Relationship(back_populates="curso_unidade")
