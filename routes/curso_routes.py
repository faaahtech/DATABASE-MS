from fastapi import APIRouter, Depends, Query, status
from sqlmodel.ext.asyncio.session import AsyncSession

from controller.curso_controller import CursoController
from dtos.curso_dto import CursoCreate, CursoRead, CursoUpdate
from repositories.postgres_conn import get_session

router = APIRouter(prefix="/cursos", tags=["Cursos"])
controller = CursoController()


@router.post("", response_model=CursoRead, status_code=status.HTTP_201_CREATED)
async def create_curso(
    data: CursoCreate,
    session: AsyncSession = Depends(get_session),
) -> CursoRead:
    return await controller.create_curso(session=session, data=data)


@router.get("", response_model=list[CursoRead], status_code=status.HTTP_200_OK)
async def list_cursos(
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    session: AsyncSession = Depends(get_session),
) -> list[CursoRead]:
    return await controller.list_cursos(session=session, limit=limit, offset=offset)


@router.get("/sigla/{sigla}", response_model=CursoRead, status_code=status.HTTP_200_OK)
async def get_curso_by_sigla(
    sigla: str,
    session: AsyncSession = Depends(get_session),
) -> CursoRead:
    return await controller.get_curso_by_sigla(session=session, sigla=sigla)


@router.get("/{id_curso}", response_model=CursoRead, status_code=status.HTTP_200_OK)
async def get_curso_by_id(
    id_curso: int,
    session: AsyncSession = Depends(get_session),
) -> CursoRead:
    return await controller.get_curso_by_id(session=session, id_curso=id_curso)


@router.patch("/{id_curso}", response_model=CursoRead, status_code=status.HTTP_200_OK)
async def update_curso(
    id_curso: int,
    data: CursoUpdate,
    session: AsyncSession = Depends(get_session),
) -> CursoRead:
    return await controller.update_curso(session=session, id_curso=id_curso, data=data)
