from __future__ import annotations

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from models.base_conhecimento import BaseConhecimento, CategoriaBaseConhecimento


class BaseConhecimentoRepository:
    async def create(
        self,
        session: AsyncSession,
        base_conhecimento: BaseConhecimento,
    ) -> BaseConhecimento:
        session.add(base_conhecimento)
        await session.flush()
        return base_conhecimento

    async def get_by_id(
        self,
        session: AsyncSession,
        id_base_conhecimento: int,
    ) -> BaseConhecimento | None:
        return await session.get(BaseConhecimento, id_base_conhecimento)

    async def list(
        self,
        session: AsyncSession,
        limit: int = 100,
        offset: int = 0,
    ) -> list[BaseConhecimento]:
        statement = (
            select(BaseConhecimento)
            .order_by(BaseConhecimento.id)
            .offset(offset)
            .limit(limit)
        )
        result = await session.exec(statement)
        return list(result.all())

    async def list_by_categoria(
        self,
        session: AsyncSession,
        categoria: CategoriaBaseConhecimento,
        limit: int = 100,
        offset: int = 0,
    ) -> list[BaseConhecimento]:
        statement = (
            select(BaseConhecimento)
            .where(BaseConhecimento.categoria == categoria)
            .order_by(BaseConhecimento.id)
            .offset(offset)
            .limit(limit)
        )
        result = await session.exec(statement)
        return list(result.all())

    async def update(
        self,
        session: AsyncSession,
        base_conhecimento: BaseConhecimento,
    ) -> BaseConhecimento:
        session.add(base_conhecimento)
        await session.flush()
        return base_conhecimento
