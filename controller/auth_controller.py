from sqlmodel.ext.asyncio.session import AsyncSession

from dtos.auth_dto import LoginRequest, LoginResponse, RecuperarSenhaRequest, ResetarSenhaRequest
from services.auth_service import AuthService


class AuthController:
    def __init__(self) -> None:
        self.service = AuthService()

    async def login(self, session: AsyncSession, data: LoginRequest) -> LoginResponse:
        return await self.service.login(session=session, data=data)

    async def request_password_recovery(
        self,
        session: AsyncSession,
        data: RecuperarSenhaRequest,
    ) -> dict[str, str]:
        return await self.service.request_password_recovery(session=session, data=data)

    async def reset_password(
        self,
        session: AsyncSession,
        data: ResetarSenhaRequest,
    ) -> dict[str, str]:
        return await self.service.reset_password(session=session, data=data)
