from __future__ import annotations

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from models.professor import Professor


class ProfessorRepository:
    async def create(self, session: AsyncSession, professor: Professor) -> Professor:
        session.add(professor)
        await session.flush()
        return professor

    async def get_by_id(self, session: AsyncSession, id_professor: int) -> Professor | None:
        return await session.get(Professor, id_professor)

    async def get_by_email(self, session: AsyncSession, email: str) -> Professor | None:
        statement = select(Professor).where(Professor.email == email)
        result = await session.exec(statement)
        return result.first()

    async def list(
        self,
        session: AsyncSession,
        limit: int = 100,
        offset: int = 0,
    ) -> list[Professor]:
        statement = select(Professor).offset(offset).limit(limit)
        result = await session.exec(statement)
        return list(result.all())

    async def exists_by_email(self, session: AsyncSession, email: str) -> bool:
        statement = select(Professor.id).where(Professor.email == email).limit(1)
        result = await session.exec(statement)
        return result.first() is not None

    async def exists_by_cpf(self, session: AsyncSession, cpf: str) -> bool:
        # O model Professor atual não possui CPF. Mantido para compatibilidade
        # com a interface esperada da fase, sempre retornando False.
        return False
