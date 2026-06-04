from dtos.usuario_register_dto import UsuarioRegisterRequest, UsuarioRegisterResponse
from services.usuario_service import UsuarioService
from sqlmodel.ext.asyncio.session import AsyncSession


class UsuarioRegisterService:
    """Compatibilidade com o import antigo services/usuario/usuario_register_service.py.

    A implementação oficial da FASE 4 está em services/usuario_service.py.
    """

    def __init__(self) -> None:
        self.usuario_service = UsuarioService()

    async def register(
        self,
        session: AsyncSession,
        data: UsuarioRegisterRequest,
    ) -> UsuarioRegisterResponse:
        return await self.usuario_service.register_usuario(session=session, data=data)
