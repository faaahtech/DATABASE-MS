from fastapi import APIRouter, Depends, Query, status
from sqlmodel.ext.asyncio.session import AsyncSession

from controller.endereco_controller import EnderecoController
from dtos.endereco_dto import EnderecoCreate, EnderecoRead
from repositories.postgres_conn import get_session

router = APIRouter(prefix="/enderecos", tags=["Endereços"])
controller = EnderecoController()


@router.post("", response_model=EnderecoRead, status_code=status.HTTP_201_CREATED)
async def create_endereco(
    data: EnderecoCreate,
    session: AsyncSession = Depends(get_session),
) -> EnderecoRead:
    return await controller.create_endereco(session=session, data=data)


@router.get("", response_model=list[EnderecoRead], status_code=status.HTTP_200_OK)
async def list_enderecos(
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    session: AsyncSession = Depends(get_session),
) -> list[EnderecoRead]:
    return await controller.list_enderecos(session=session, limit=limit, offset=offset)


@router.get("/{id_endereco}", response_model=EnderecoRead, status_code=status.HTTP_200_OK)
async def get_endereco_by_id(
    id_endereco: int,
    session: AsyncSession = Depends(get_session),
) -> EnderecoRead:
    return await controller.get_endereco_by_id(session=session, id_endereco=id_endereco)
