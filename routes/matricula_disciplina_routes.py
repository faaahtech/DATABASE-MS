from fastapi import APIRouter, Depends, Query, status
from sqlmodel.ext.asyncio.session import AsyncSession

from controller.matricula_disciplina_controller import MatriculaDisciplinaController
from dtos.matricula_disciplina_dto import (
    MatriculaDisciplinaCreate,
    MatriculaDisciplinaRead,
    MatriculaDisciplinaUpdateStatus,
)
from repositories.postgres_conn import get_session

router = APIRouter(prefix="/matriculas-disciplinas", tags=["Matrículas de Disciplinas"])
controller = MatriculaDisciplinaController()


@router.post("", response_model=MatriculaDisciplinaRead, status_code=status.HTTP_201_CREATED)
async def create_matricula_disciplina(
    data: MatriculaDisciplinaCreate,
    session: AsyncSession = Depends(get_session),
) -> MatriculaDisciplinaRead:
    return await controller.create_matricula_disciplina(session=session, data=data)


@router.get(
    "/matricula-curso/{id_matricula_curso}",
    response_model=list[MatriculaDisciplinaRead],
    status_code=status.HTTP_200_OK,
)
async def list_matriculas_disciplina_by_matricula_curso(
    id_matricula_curso: int,
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    session: AsyncSession = Depends(get_session),
) -> list[MatriculaDisciplinaRead]:
    return await controller.list_matriculas_disciplina_by_matricula_curso(
        session=session,
        id_matricula_curso=id_matricula_curso,
        limit=limit,
        offset=offset,
    )


@router.get(
    "/oferta-disciplina/{id_oferta_disciplina}",
    response_model=list[MatriculaDisciplinaRead],
    status_code=status.HTTP_200_OK,
)
async def list_matriculas_disciplina_by_oferta_disciplina(
    id_oferta_disciplina: int,
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    session: AsyncSession = Depends(get_session),
) -> list[MatriculaDisciplinaRead]:
    return await controller.list_matriculas_disciplina_by_oferta_disciplina(
        session=session,
        id_oferta_disciplina=id_oferta_disciplina,
        limit=limit,
        offset=offset,
    )


@router.get("/{id_matricula_disciplina}", response_model=MatriculaDisciplinaRead, status_code=status.HTTP_200_OK)
async def get_matricula_disciplina_by_id(
    id_matricula_disciplina: int,
    session: AsyncSession = Depends(get_session),
) -> MatriculaDisciplinaRead:
    return await controller.get_matricula_disciplina_by_id(
        session=session,
        id_matricula_disciplina=id_matricula_disciplina,
    )


@router.patch("/{id_matricula_disciplina}/status", response_model=MatriculaDisciplinaRead, status_code=status.HTTP_200_OK)
async def update_matricula_disciplina_status(
    id_matricula_disciplina: int,
    data: MatriculaDisciplinaUpdateStatus,
    session: AsyncSession = Depends(get_session),
) -> MatriculaDisciplinaRead:
    return await controller.update_matricula_disciplina_status(
        session=session,
        id_matricula_disciplina=id_matricula_disciplina,
        data=data,
    )
