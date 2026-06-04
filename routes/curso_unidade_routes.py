from fastapi import APIRouter, Depends, Query, status
from sqlmodel.ext.asyncio.session import AsyncSession

from controller.curso_unidade_controller import CursoUnidadeController
from dtos.curso_unidade_dto import CursoUnidadeCreate, CursoUnidadeListItem, CursoUnidadeRead
from repositories.postgres_conn import get_session

router = APIRouter(prefix="/curso-unidade", tags=["Curso Unidade"])
controller = CursoUnidadeController()


@router.post("", response_model=CursoUnidadeRead, status_code=status.HTTP_201_CREATED)
async def create_curso_unidade(
    data: CursoUnidadeCreate,
    session: AsyncSession = Depends(get_session),
) -> CursoUnidadeRead:
    return await controller.create_curso_unidade(session=session, data=data)


@router.get("", response_model=list[CursoUnidadeListItem], status_code=status.HTTP_200_OK)
async def list_curso_unidade(
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    session: AsyncSession = Depends(get_session),
) -> list[CursoUnidadeListItem]:
    return await controller.list_curso_unidade(session=session, limit=limit, offset=offset)


@router.get("/{id_curso_unidade}", response_model=CursoUnidadeRead, status_code=status.HTTP_200_OK)
async def get_curso_unidade_by_id(
    id_curso_unidade: int,
    session: AsyncSession = Depends(get_session),
) -> CursoUnidadeRead:
    return await controller.get_curso_unidade_by_id(
        session=session,
        id_curso_unidade=id_curso_unidade,
    )
