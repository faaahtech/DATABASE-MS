from fastapi import APIRouter, Depends, Query, status
from sqlmodel.ext.asyncio.session import AsyncSession

from controller.base_conhecimento_controller import BaseConhecimentoController
from dtos.base_conhecimento_dto import (
    BaseConhecimentoCreate,
    BaseConhecimentoRead,
    BaseConhecimentoUpdate,
)
from models.base_conhecimento import CategoriaBaseConhecimento
from repositories.postgres_conn import get_session

router = APIRouter(prefix="/base-conhecimento", tags=["Base de Conhecimento"])
controller = BaseConhecimentoController()


@router.post("", response_model=BaseConhecimentoRead, status_code=status.HTTP_201_CREATED)
async def create_base_conhecimento(
    data: BaseConhecimentoCreate,
    session: AsyncSession = Depends(get_session),
) -> BaseConhecimentoRead:
    return await controller.create_base_conhecimento(session=session, data=data)


@router.get("", response_model=list[BaseConhecimentoRead], status_code=status.HTTP_200_OK)
async def list_bases_conhecimento(
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    session: AsyncSession = Depends(get_session),
) -> list[BaseConhecimentoRead]:
    return await controller.list_bases_conhecimento(session=session, limit=limit, offset=offset)


@router.get("/categoria/{categoria}", response_model=list[BaseConhecimentoRead], status_code=status.HTTP_200_OK)
async def list_bases_by_categoria(
    categoria: CategoriaBaseConhecimento,
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    session: AsyncSession = Depends(get_session),
) -> list[BaseConhecimentoRead]:
    return await controller.list_bases_by_categoria(
        session=session,
        categoria=categoria,
        limit=limit,
        offset=offset,
    )


@router.get("/{id_base_conhecimento}", response_model=BaseConhecimentoRead, status_code=status.HTTP_200_OK)
async def get_base_conhecimento_by_id(
    id_base_conhecimento: int,
    session: AsyncSession = Depends(get_session),
) -> BaseConhecimentoRead:
    return await controller.get_base_conhecimento_by_id(
        session=session,
        id_base_conhecimento=id_base_conhecimento,
    )


@router.patch("/{id_base_conhecimento}", response_model=BaseConhecimentoRead, status_code=status.HTTP_200_OK)
async def update_base_conhecimento(
    id_base_conhecimento: int,
    data: BaseConhecimentoUpdate,
    session: AsyncSession = Depends(get_session),
) -> BaseConhecimentoRead:
    return await controller.update_base_conhecimento(
        session=session,
        id_base_conhecimento=id_base_conhecimento,
        data=data,
    )
