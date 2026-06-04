from sqlmodel import SQLModel

from models.curso_unidade import (
    ModalidadeCursoUnidade,
    NivelCursoUnidade,
    StatusCursoUnidade,
)


class CursoUnidadeCreate(SQLModel):
    id_curso: int
    id_unidade: int
    nivel: NivelCursoUnidade
    modalidade: ModalidadeCursoUnidade
    status: StatusCursoUnidade = StatusCursoUnidade.ATIVO


class CursoUnidadeRead(SQLModel):
    id: int
    id_curso: int
    id_unidade: int
    nivel: NivelCursoUnidade
    modalidade: ModalidadeCursoUnidade
    status: StatusCursoUnidade


class CursoUnidadeListItem(SQLModel):
    id: int
    id_curso: int
    id_unidade: int
    nivel: NivelCursoUnidade
    modalidade: ModalidadeCursoUnidade
    status: StatusCursoUnidade
    curso_nome: str | None = None
    unidade_nome: str | None = None
