from __future__ import annotations

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from models.periodo_letivo import PeriodoLetivo, StatusPeriodoLetivo


class PeriodoLetivoRepository:
    async def create(self, session: AsyncSession, periodo_letivo: PeriodoLetivo) -> PeriodoLetivo:
        session.add(periodo_letivo)
        await session.flush()
        return periodo_letivo

    async def get_by_id(
        self,
        session: AsyncSession,
        id_periodo_letivo: int,
    ) -> PeriodoLetivo | None:
        return await session.get(PeriodoLetivo, id_periodo_letivo)

    async def get_ativo(self, session: AsyncSession) -> PeriodoLetivo | None:
        statement = select(PeriodoLetivo).where(
            PeriodoLetivo.status == StatusPeriodoLetivo.ATIVO
        )
        result = await session.exec(statement)
        return result.first()

    async def list_ativos(self, session: AsyncSession) -> list[PeriodoLetivo]:
        statement = select(PeriodoLetivo).where(
            PeriodoLetivo.status == StatusPeriodoLetivo.ATIVO
        )
        result = await session.exec(statement)
        return list(result.all())

    async def get_by_ano_semestre(
        self,
        session: AsyncSession,
        ano: int,
        semestre: int,
    ) -> PeriodoLetivo | None:
        statement = select(PeriodoLetivo).where(
            PeriodoLetivo.ano == ano,
            PeriodoLetivo.semestre == semestre,
        )
        result = await session.exec(statement)
        return result.first()

    async def list(
        self,
        session: AsyncSession,
        limit: int = 100,
        offset: int = 0,
    ) -> list[PeriodoLetivo]:
        statement = select(PeriodoLetivo).offset(offset).limit(limit)
        result = await session.exec(statement)
        return list(result.all())

    async def update(self, session: AsyncSession, periodo_letivo: PeriodoLetivo) -> PeriodoLetivo:
        session.add(periodo_letivo)
        await session.flush()
        return periodo_letivo
