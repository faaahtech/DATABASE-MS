from fastapi import APIRouter, Depends, status
from sqlmodel.ext.asyncio.session import AsyncSession

from controller.usuario_controller import UsuarioController
from dtos.usuario_dto import UsuarioRead, UsuarioRegisterRequest, UsuarioRegisterResponse
from repositories.postgres_conn import get_session

router = APIRouter(prefix="/usuarios", tags=["Usuários"])
controller = UsuarioController()


@router.post("/register", response_model=UsuarioRegisterResponse, status_code=status.HTTP_201_CREATED)
async def register_usuario(
    data: UsuarioRegisterRequest,
    session: AsyncSession = Depends(get_session),
) -> UsuarioRegisterResponse:
    return await controller.register_usuario(session=session, data=data)


@router.get("/by-email/{email}", response_model=UsuarioRead, status_code=status.HTTP_200_OK)
async def get_usuario_by_email(
    email: str,
    session: AsyncSession = Depends(get_session),
) -> UsuarioRead:
    return await controller.get_usuario_by_email(session=session, email=email)


@router.get("/{id_usuario}", response_model=UsuarioRead, status_code=status.HTTP_200_OK)
async def get_usuario_by_id(
    id_usuario: int,
    session: AsyncSession = Depends(get_session),
) -> UsuarioRead:
    return await controller.get_usuario_by_id(session=session, id_usuario=id_usuario)
