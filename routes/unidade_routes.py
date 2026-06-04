from fastapi import APIRouter, Depends, Query, status
from sqlmodel.ext.asyncio.session import AsyncSession

from controller.unidade_controller import UnidadeController
from dtos.unidade_dto import UnidadeCreate, UnidadeRead, UnidadeUpdate
from repositories.postgres_conn import get_session

router = APIRouter(prefix="/unidades", tags=["Unidades"])
controller = UnidadeController()


@router.post("", response_model=UnidadeRead, status_code=status.HTTP_201_CREATED)
async def create_unidade(
    data: UnidadeCreate,
    session: AsyncSession = Depends(get_session),
) -> UnidadeRead:
    return await controller.create_unidade(session=session, data=data)


@router.get("", response_model=list[UnidadeRead], status_code=status.HTTP_200_OK)
async def list_unidades(
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    session: AsyncSession = Depends(get_session),
) -> list[UnidadeRead]:
    return await controller.list_unidades(session=session, limit=limit, offset=offset)


@router.get("/{id_unidade}", response_model=UnidadeRead, status_code=status.HTTP_200_OK)
async def get_unidade_by_id(
    id_unidade: int,
    session: AsyncSession = Depends(get_session),
) -> UnidadeRead:
    return await controller.get_unidade_by_id(session=session, id_unidade=id_unidade)


@router.patch("/{id_unidade}", response_model=UnidadeRead, status_code=status.HTTP_200_OK)
async def update_unidade(
    id_unidade: int,
    data: UnidadeUpdate,
    session: AsyncSession = Depends(get_session),
) -> UnidadeRead:
    return await controller.update_unidade(session=session, id_unidade=id_unidade, data=data)
