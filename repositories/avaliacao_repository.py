from __future__ import annotations

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from models.avaliacao import Avaliacao


class AvaliacaoRepository:
    async def create(self, session: AsyncSession, avaliacao: Avaliacao) -> Avaliacao:
        session.add(avaliacao)
        await session.flush()
        return avaliacao

    async def get_by_id(self, session: AsyncSession, id_avaliacao: int) -> Avaliacao | None:
        return await session.get(Avaliacao, id_avaliacao)

    async def get_by_oferta_and_nome(
        self,
        session: AsyncSession,
        id_oferta_disciplina: int,
        nome: str,
    ) -> Avaliacao | None:
        statement = select(Avaliacao).where(
            Avaliacao.id_oferta_disciplina == id_oferta_disciplina,
            Avaliacao.nome == nome.strip(),
        )
        result = await session.exec(statement)
        return result.first()

    async def exists_by_oferta_and_nome(
        self,
        session: AsyncSession,
        id_oferta_disciplina: int,
        nome: str,
    ) -> bool:
        statement = (
            select(Avaliacao.id)
            .where(
                Avaliacao.id_oferta_disciplina == id_oferta_disciplina,
                Avaliacao.nome == nome.strip(),
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
    ) -> list[Avaliacao]:
        statement = (
            select(Avaliacao)
            .where(Avaliacao.id_oferta_disciplina == id_oferta_disciplina)
            .offset(offset)
            .limit(limit)
        )
        result = await session.exec(statement)
        return list(result.all())

    async def update(self, session: AsyncSession, avaliacao: Avaliacao) -> Avaliacao:
        session.add(avaliacao)
        await session.flush()
        return avaliacao
