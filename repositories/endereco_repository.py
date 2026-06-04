from __future__ import annotations

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from models.endereco import Endereco


class EnderecoRepository:
    async def create(self, session: AsyncSession, endereco: Endereco) -> Endereco:
        session.add(endereco)
        await session.flush()
        return endereco

    async def get_by_id(self, session: AsyncSession, id_endereco: int) -> Endereco | None:
        return await session.get(Endereco, id_endereco)

    async def list(
        self,
        session: AsyncSession,
        limit: int = 100,
        offset: int = 0,
    ) -> list[Endereco]:
        statement = select(Endereco).offset(offset).limit(limit)
        result = await session.exec(statement)
        return list(result.all())

    async def update(self, session: AsyncSession, endereco: Endereco) -> Endereco:
        session.add(endereco)
        await session.flush()
        return endereco
