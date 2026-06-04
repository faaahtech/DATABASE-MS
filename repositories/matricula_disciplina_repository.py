from __future__ import annotations

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from models.matricula_disciplina import MatriculaDisciplina


class MatriculaDisciplinaRepository:
    async def create(
        self,
        session: AsyncSession,
        matricula_disciplina: MatriculaDisciplina,
    ) -> MatriculaDisciplina:
        session.add(matricula_disciplina)
        await session.flush()
        return matricula_disciplina

    async def get_by_id(
        self,
        session: AsyncSession,
        id_matricula_disciplina: int,
    ) -> MatriculaDisciplina | None:
        return await session.get(MatriculaDisciplina, id_matricula_disciplina)

    async def get_by_matricula_curso_and_oferta(
        self,
        session: AsyncSession,
        id_matricula_curso: int,
        id_oferta_disciplina: int,
    ) -> MatriculaDisciplina | None:
        statement = select(MatriculaDisciplina).where(
            MatriculaDisciplina.id_matricula_curso == id_matricula_curso,
            MatriculaDisciplina.id_oferta_disciplina == id_oferta_disciplina,
        )
        result = await session.exec(statement)
        return result.first()

    async def exists_by_matricula_curso_and_oferta(
        self,
        session: AsyncSession,
        id_matricula_curso: int,
        id_oferta_disciplina: int,
    ) -> bool:
        statement = (
            select(MatriculaDisciplina.id)
            .where(
                MatriculaDisciplina.id_matricula_curso == id_matricula_curso,
                MatriculaDisciplina.id_oferta_disciplina == id_oferta_disciplina,
            )
            .limit(1)
        )
        result = await session.exec(statement)
        return result.first() is not None

    async def list_by_matricula_curso(
        self,
        session: AsyncSession,
        id_matricula_curso: int,
        limit: int = 100,
        offset: int = 0,
    ) -> list[MatriculaDisciplina]:
        statement = (
            select(MatriculaDisciplina)
            .where(MatriculaDisciplina.id_matricula_curso == id_matricula_curso)
            .offset(offset)
            .limit(limit)
        )
        result = await session.exec(statement)
        return list(result.all())

    async def list_by_oferta_disciplina(
        self,
        session: AsyncSession,
        id_oferta_disciplina: int,
        limit: int = 100,
        offset: int = 0,
    ) -> list[MatriculaDisciplina]:
        statement = (
            select(MatriculaDisciplina)
            .where(MatriculaDisciplina.id_oferta_disciplina == id_oferta_disciplina)
            .offset(offset)
            .limit(limit)
        )
        result = await session.exec(statement)
        return list(result.all())

    async def update(
        self,
        session: AsyncSession,
        matricula_disciplina: MatriculaDisciplina,
    ) -> MatriculaDisciplina:
        session.add(matricula_disciplina)
        await session.flush()
        return matricula_disciplina
