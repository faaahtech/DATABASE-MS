from __future__ import annotations

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from models.unidade import Unidade


class UnidadeRepository:
    async def create(self, session: AsyncSession, unidade: Unidade) -> Unidade:
        session.add(unidade)
        await session.flush()
        return unidade

    async def get_by_id(self, session: AsyncSession, id_unidade: int) -> Unidade | None:
        return await session.get(Unidade, id_unidade)

    async def get_by_nome(self, session: AsyncSession, nome: str) -> Unidade | None:
        statement = select(Unidade).where(Unidade.nome == nome.strip())
        result = await session.exec(statement)
        return result.first()

    async def list(
        self,
        session: AsyncSession,
        limit: int = 100,
        offset: int = 0,
    ) -> list[Unidade]:
        statement = select(Unidade).offset(offset).limit(limit)
        result = await session.exec(statement)
        return list(result.all())

    async def update(self, session: AsyncSession, unidade: Unidade) -> Unidade:
        session.add(unidade)
        await session.flush()
        return unidade
