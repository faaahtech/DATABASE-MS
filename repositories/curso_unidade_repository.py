from __future__ import annotations

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from models.curso_unidade import CursoUnidade, ModalidadeCursoUnidade, NivelCursoUnidade


class CursoUnidadeRepository:
    async def create(self, session: AsyncSession, curso_unidade: CursoUnidade) -> CursoUnidade:
        session.add(curso_unidade)
        await session.flush()
        return curso_unidade

    async def get_by_id(
        self,
        session: AsyncSession,
        id_curso_unidade: int,
    ) -> CursoUnidade | None:
        return await session.get(CursoUnidade, id_curso_unidade)

    async def list(
        self,
        session: AsyncSession,
        limit: int = 100,
        offset: int = 0,
    ) -> list[CursoUnidade]:
        statement = select(CursoUnidade).offset(offset).limit(limit)
        result = await session.exec(statement)
        return list(result.all())

    async def get_by_curso_and_unidade(
        self,
        session: AsyncSession,
        id_curso: int,
        id_unidade: int,
        nivel: NivelCursoUnidade | None = None,
        modalidade: ModalidadeCursoUnidade | None = None,
    ) -> CursoUnidade | None:
        statement = select(CursoUnidade).where(
            CursoUnidade.id_curso == id_curso,
            CursoUnidade.id_unidade == id_unidade,
        )

        if nivel is not None:
            statement = statement.where(CursoUnidade.nivel == nivel)

        if modalidade is not None:
            statement = statement.where(CursoUnidade.modalidade == modalidade)

        result = await session.exec(statement)
        return result.first()

    async def exists_by_curso_and_unidade(
        self,
        session: AsyncSession,
        id_curso: int,
        id_unidade: int,
        nivel: NivelCursoUnidade | None = None,
        modalidade: ModalidadeCursoUnidade | None = None,
    ) -> bool:
        statement = select(CursoUnidade.id).where(
            CursoUnidade.id_curso == id_curso,
            CursoUnidade.id_unidade == id_unidade,
        )

        if nivel is not None:
            statement = statement.where(CursoUnidade.nivel == nivel)

        if modalidade is not None:
            statement = statement.where(CursoUnidade.modalidade == modalidade)

        statement = statement.limit(1)
        result = await session.exec(statement)
        return result.first() is not None
