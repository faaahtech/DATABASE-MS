from __future__ import annotations

from datetime import date

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from models.aula import Aula


class AulaRepository:
    async def create(self, session: AsyncSession, aula: Aula) -> Aula:
        session.add(aula)
        await session.flush()
        return aula

    async def get_by_id(self, session: AsyncSession, id_aula: int) -> Aula | None:
        return await session.get(Aula, id_aula)

    async def get_by_oferta_data_assunto(
        self,
        session: AsyncSession,
        id_oferta_disciplina: int,
        data: date,
        assunto: str,
    ) -> Aula | None:
        statement = select(Aula).where(
            Aula.id_oferta_disciplina == id_oferta_disciplina,
            Aula.data == data,
            Aula.assunto == assunto.strip(),
        )
        result = await session.exec(statement)
        return result.first()

    async def exists_by_oferta_data_assunto(
        self,
        session: AsyncSession,
        id_oferta_disciplina: int,
        data: date,
        assunto: str,
    ) -> bool:
        statement = (
            select(Aula.id)
            .where(
                Aula.id_oferta_disciplina == id_oferta_disciplina,
                Aula.data == data,
                Aula.assunto == assunto.strip(),
            )
            .limit(1)
        )
        result = await session.exec(statement)
        return result.first() is not None

    async def list_by_oferta_disciplina(
        self,
        session: AsyncSession,
        id_oferta_disciplina: int,
        limit: int = 100,
        offset: int = 0,
    ) -> list[Aula]:
        statement = (
            select(Aula)
            .where(Aula.id_oferta_disciplina == id_oferta_disciplina)
            .offset(offset)
            .limit(limit)
        )
        result = await session.exec(statement)
        return list(result.all())

    async def update(self, session: AsyncSession, aula: Aula) -> Aula:
        session.add(aula)
        await session.flush()
        return aula
