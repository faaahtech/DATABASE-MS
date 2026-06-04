from __future__ import annotations

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from models.matriz_curricular import MatrizCurricular


class MatrizCurricularRepository:
    async def create(self, session: AsyncSession, matriz_curricular: MatrizCurricular) -> MatrizCurricular:
        session.add(matriz_curricular)
        await session.flush()
        return matriz_curricular

    async def get_by_id(
        self,
        session: AsyncSession,
        id_matriz_curricular: int,
    ) -> MatrizCurricular | None:
        return await session.get(MatrizCurricular, id_matriz_curricular)

    async def list(
        self,
        session: AsyncSession,
        limit: int = 100,
        offset: int = 0,
    ) -> list[MatrizCurricular]:
        statement = select(MatrizCurricular).offset(offset).limit(limit)
        result = await session.exec(statement)
        return list(result.all())

    async def list_by_curso_unidade(
        self,
        session: AsyncSession,
        id_curso_unidade: int,
        limit: int = 100,
        offset: int = 0,
    ) -> list[MatrizCurricular]:
        statement = (
            select(MatrizCurricular)
            .where(MatrizCurricular.id_curso_unidade == id_curso_unidade)
            .offset(offset)
            .limit(limit)
        )
        result = await session.exec(statement)
        return list(result.all())

    async def get_by_curso_unidade_and_disciplina(
        self,
        session: AsyncSession,
        id_curso_unidade: int,
        id_disciplina: int,
    ) -> MatrizCurricular | None:
        statement = select(MatrizCurricular).where(
            MatrizCurricular.id_curso_unidade == id_curso_unidade,
            MatrizCurricular.id_disciplina == id_disciplina,
        )
        result = await session.exec(statement)
        return result.first()

    async def exists_by_curso_unidade_and_disciplina(
        self,
        session: AsyncSession,
        id_curso_unidade: int,
        id_disciplina: int,
    ) -> bool:
        statement = (
            select(MatrizCurricular.id)
            .where(
                MatrizCurricular.id_curso_unidade == id_curso_unidade,
                MatrizCurricular.id_disciplina == id_disciplina,
            )
            .limit(1)
        )
        result = await session.exec(statement)
        return result.first() is not None

    async def update(self, session: AsyncSession, matriz_curricular: MatrizCurricular) -> MatrizCurricular:
        session.add(matriz_curricular)
        await session.flush()
        return matriz_curricular
