from fastapi import APIRouter, Depends, status
from sqlmodel.ext.asyncio.session import AsyncSession

from controller.auth_controller import AuthController
from dtos.auth_dto import LoginRequest, LoginResponse, RecuperarSenhaRequest, ResetarSenhaRequest
from repositories.postgres_conn import get_session

router = APIRouter(prefix="/auth", tags=["Auth"])
controller = AuthController()


@router.post("/login", response_model=LoginResponse, status_code=status.HTTP_200_OK)
async def login(
    data: LoginRequest,
    session: AsyncSession = Depends(get_session),
) -> LoginResponse:
    return await controller.login(session=session, data=data)


@router.post("/recuperar-senha", response_model=dict[str, str], status_code=status.HTTP_200_OK)
async def recuperar_senha(
    data: RecuperarSenhaRequest,
    session: AsyncSession = Depends(get_session),
) -> dict[str, str]:
    return await controller.request_password_recovery(session=session, data=data)


@router.post("/resetar-senha", response_model=dict[str, str], status_code=status.HTTP_200_OK)
async def resetar_senha(
    data: ResetarSenhaRequest,
    session: AsyncSession = Depends(get_session),
) -> dict[str, str]:
    return await controller.reset_password(session=session, data=data)
