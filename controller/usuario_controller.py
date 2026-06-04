from sqlmodel.ext.asyncio.session import AsyncSession

from dtos.usuario_dto import UsuarioRead, UsuarioRegisterRequest, UsuarioRegisterResponse
from services.usuario_service import UsuarioService


class UsuarioController:
    def __init__(self) -> None:
        self.service = UsuarioService()

    async def register_usuario(
        self,
        session: AsyncSession,
        data: UsuarioRegisterRequest,
    ) -> UsuarioRegisterResponse:
        return await self.service.register_usuario(session=session, data=data)

    async def get_usuario_by_id(self, session: AsyncSession, id_usuario: int) -> UsuarioRead:
        return await self.service.get_usuario_by_id(session=session, id_usuario=id_usuario)

    async def get_usuario_by_email(self, session: AsyncSession, email: str) -> UsuarioRead:
        return await self.service.get_usuario_by_email(session=session, email=email)
