from __future__ import annotations

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from models.calendario_academico import CalendarioAcademico, TipoCalendarioAcademico


class CalendarioAcademicoRepository:
    async def create(
        self,
        session: AsyncSession,
        calendario: CalendarioAcademico,
    ) -> CalendarioAcademico:
        session.add(calendario)
        await session.flush()
        return calendario

    async def get_by_id(
        self,
        session: AsyncSession,
        id_calendario_academico: int,
    ) -> CalendarioAcademico | None:
        return await session.get(CalendarioAcademico, id_calendario_academico)

    async def list(
        self,
        session: AsyncSession,
        limit: int = 100,
        offset: int = 0,
    ) -> list[CalendarioAcademico]:
        statement = (
            select(CalendarioAcademico)
            .order_by(CalendarioAcademico.data_inicio, CalendarioAcademico.id)
            .offset(offset)
            .limit(limit)
        )
        result = await session.exec(statement)
        return list(result.all())

    async def list_by_unidade(
        self,
        session: AsyncSession,
        id_unidade: int,
        limit: int = 100,
        offset: int = 0,
    ) -> list[CalendarioAcademico]:
        statement = (
            select(CalendarioAcademico)
            .where(CalendarioAcademico.id_unidade == id_unidade)
            .order_by(CalendarioAcademico.data_inicio, CalendarioAcademico.id)
            .offset(offset)
            .limit(limit)
        )
        result = await session.exec(statement)
        return list(result.all())

    async def list_by_tipo(
        self,
        session: AsyncSession,
        tipo: TipoCalendarioAcademico,
        limit: int = 100,
        offset: int = 0,
    ) -> list[CalendarioAcademico]:
        statement = (
            select(CalendarioAcademico)
            .where(CalendarioAcademico.tipo == tipo)
            .order_by(CalendarioAcademico.data_inicio, CalendarioAcademico.id)
            .offset(offset)
            .limit(limit)
        )
        result = await session.exec(statement)
        return list(result.all())

    async def update(
        self,
        session: AsyncSession,
        calendario: CalendarioAcademico,
    ) -> CalendarioAcademico:
        session.add(calendario)
        await session.flush()
        return calendario
