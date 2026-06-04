from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from models.usuario import Usuario


class UsuarioRepository:
    async def create(self, session: AsyncSession, usuario: Usuario) -> Usuario:
        session.add(usuario)
        await session.flush()
        return usuario

    async def get_by_id(self, session: AsyncSession, id_usuario: int) -> Usuario | None:
        return await session.get(Usuario, id_usuario)

    async def get_by_email(self, session: AsyncSession, email: str) -> Usuario | None:
        statement = select(Usuario).where(Usuario.email == email)
        result = await session.exec(statement)
        return result.first()

    async def exists_by_email(self, session: AsyncSession, email: str) -> bool:
        statement = select(Usuario.id).where(Usuario.email == email).limit(1)
        result = await session.exec(statement)
        return result.first() is not None

    async def update_recovery_token(
        self,
        session: AsyncSession,
        usuario: Usuario,
        token_recuperacao: str,
    ) -> Usuario:
        usuario.token_recuperacao = token_recuperacao
        session.add(usuario)
        await session.flush()
        return usuario

    async def clear_recovery_token(self, session: AsyncSession, usuario: Usuario) -> Usuario:
        usuario.token_recuperacao = None
        session.add(usuario)
        await session.flush()
        return usuario
