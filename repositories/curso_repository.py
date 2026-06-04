from __future__ import annotations

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from models.curso import Curso


class CursoRepository:
    async def create(self, session: AsyncSession, curso: Curso) -> Curso:
        session.add(curso)
        await session.flush()
        return curso

    async def get_by_id(self, session: AsyncSession, id_curso: int) -> Curso | None:
        return await session.get(Curso, id_curso)

    async def get_by_sigla(self, session: AsyncSession, sigla: str) -> Curso | None:
        statement = select(Curso).where(Curso.sigla == sigla.upper().strip())
        result = await session.exec(statement)
        return result.first()

    async def exists_by_sigla(self, session: AsyncSession, sigla: str) -> bool:
        statement = select(Curso.id).where(Curso.sigla == sigla.upper().strip()).limit(1)
        result = await session.exec(statement)
        return result.first() is not None

    async def list(
        self,
        session: AsyncSession,
        limit: int = 100,
        offset: int = 0,
    ) -> list[Curso]:
        statement = select(Curso).offset(offset).limit(limit)
        result = await session.exec(statement)
        return list(result.all())

    async def update(self, session: AsyncSession, curso: Curso) -> Curso:
        session.add(curso)
        await session.flush()
        return curso
