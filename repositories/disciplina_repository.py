from __future__ import annotations

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from models.disciplina import Disciplina
from models.matriz_curricular import MatrizCurricular


class DisciplinaRepository:
    async def create(self, session: AsyncSession, disciplina: Disciplina) -> Disciplina:
        session.add(disciplina)
        await session.flush()
        return disciplina

    async def get_by_id(self, session: AsyncSession, id_disciplina: int) -> Disciplina | None:
        return await session.get(Disciplina, id_disciplina)

    async def get_by_codigo(self, session: AsyncSession, codigo: str) -> Disciplina | None:
        statement = select(Disciplina).where(Disciplina.codigo == codigo.upper().strip())
        result = await session.exec(statement)
        return result.first()

    async def exists_by_codigo(self, session: AsyncSession, codigo: str) -> bool:
        statement = select(Disciplina.id).where(Disciplina.codigo == codigo.upper().strip()).limit(1)
        result = await session.exec(statement)
        return result.first() is not None

    async def list(
        self,
        session: AsyncSession,
        limit: int = 100,
        offset: int = 0,
    ) -> list[Disciplina]:
        statement = select(Disciplina).offset(offset).limit(limit)
        result = await session.exec(statement)
        return list(result.all())

    async def list_by_curso_unidade(
        self,
        session: AsyncSession,
        id_curso_unidade: int,
        limit: int = 100,
        offset: int = 0,
    ) -> list[Disciplina]:
        statement = (
            select(Disciplina)
            .join(MatrizCurricular, MatrizCurricular.id_disciplina == Disciplina.id)
            .where(MatrizCurricular.id_curso_unidade == id_curso_unidade)
            .distinct()
            .offset(offset)
            .limit(limit)
        )
        result = await session.exec(statement)
        return list(result.all())

    async def list_by_curso_unidade_enriched(
        self,
        session: AsyncSession,
        id_curso_unidade: int,
        limit: int = 100,
        offset: int = 0,
    ):
        statement = (
            select(
                Disciplina.id,
                Disciplina.nome,
                Disciplina.codigo,
                Disciplina.carga_horaria,
                Disciplina.status,
                MatrizCurricular.id,
                MatrizCurricular.semestre_recomendado,
                MatrizCurricular.obrigatoria,
            )
            .join(MatrizCurricular, MatrizCurricular.id_disciplina == Disciplina.id)
            .where(MatrizCurricular.id_curso_unidade == id_curso_unidade)
            .offset(offset)
            .limit(limit)
        )
        result = await session.exec(statement)
        return list(result.all())

    async def update(self, session: AsyncSession, disciplina: Disciplina) -> Disciplina:
        session.add(disciplina)
        await session.flush()
        return disciplina
