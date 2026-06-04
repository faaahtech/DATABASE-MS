from __future__ import annotations

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from models.disciplina import Disciplina
from models.matriz_curricular import MatrizCurricular
from models.oferta_disciplina import OfertaDisciplina
from models.professor import Professor


class OfertaDisciplinaRepository:
    async def create(self, session: AsyncSession, oferta_disciplina: OfertaDisciplina) -> OfertaDisciplina:
        session.add(oferta_disciplina)
        await session.flush()
        return oferta_disciplina

    async def get_by_id(
        self,
        session: AsyncSession,
        id_oferta_disciplina: int,
    ) -> OfertaDisciplina | None:
        return await session.get(OfertaDisciplina, id_oferta_disciplina)

    async def get_by_codigo_oferta(
        self,
        session: AsyncSession,
        codigo_oferta: str,
    ) -> OfertaDisciplina | None:
        statement = select(OfertaDisciplina).where(OfertaDisciplina.codigo_oferta == codigo_oferta.upper().strip())
        result = await session.exec(statement)
        return result.first()

    async def exists_by_codigo_oferta(self, session: AsyncSession, codigo_oferta: str) -> bool:
        statement = select(OfertaDisciplina.id).where(
            OfertaDisciplina.codigo_oferta == codigo_oferta.upper().strip()
        ).limit(1)
        result = await session.exec(statement)
        return result.first() is not None

    async def list_by_periodo_letivo(
        self,
        session: AsyncSession,
        id_periodo_letivo: int,
        limit: int = 100,
        offset: int = 0,
    ) -> list[OfertaDisciplina]:
        statement = (
            select(OfertaDisciplina)
            .where(OfertaDisciplina.id_periodo_letivo == id_periodo_letivo)
            .offset(offset)
            .limit(limit)
        )
        result = await session.exec(statement)
        return list(result.all())

    async def list_by_periodo_letivo_enriched(
        self,
        session: AsyncSession,
        id_periodo_letivo: int,
        limit: int = 100,
        offset: int = 0,
    ):
        statement = (
            select(
                OfertaDisciplina.id,
                OfertaDisciplina.id_matriz_curricular,
                OfertaDisciplina.id_professor,
                OfertaDisciplina.id_periodo_letivo,
                OfertaDisciplina.codigo_oferta,
                OfertaDisciplina.vagas_total,
                OfertaDisciplina.vagas_disponiveis,
                OfertaDisciplina.periodo,
                OfertaDisciplina.status,
                Disciplina.nome,
                Disciplina.codigo,
                Professor.nome,
            )
            .join(
                MatrizCurricular,
                MatrizCurricular.id == OfertaDisciplina.id_matriz_curricular,
            )
            .join(
                Disciplina,
                Disciplina.id == MatrizCurricular.id_disciplina,
            )
            .join(
                Professor,
                Professor.id == OfertaDisciplina.id_professor,
            )
            .where(OfertaDisciplina.id_periodo_letivo == id_periodo_letivo)
            .offset(offset)
            .limit(limit)
        )
        result = await session.exec(statement)
        return list(result.all())

    async def list_by_curso_unidade(
        self,
        session: AsyncSession,
        id_curso_unidade: int,
        limit: int = 100,
        offset: int = 0,
    ) -> list[OfertaDisciplina]:
        statement = (
            select(OfertaDisciplina)
            .join(
                MatrizCurricular,
                MatrizCurricular.id == OfertaDisciplina.id_matriz_curricular,
            )
            .where(MatrizCurricular.id_curso_unidade == id_curso_unidade)
            .offset(offset)
            .limit(limit)
        )
        result = await session.exec(statement)
        return list(result.all())

    async def list_by_disciplina(
        self,
        session: AsyncSession,
        id_disciplina: int,
        limit: int = 100,
        offset: int = 0,
    ) -> list[OfertaDisciplina]:
        statement = (
            select(OfertaDisciplina)
            .join(
                MatrizCurricular,
                MatrizCurricular.id == OfertaDisciplina.id_matriz_curricular,
            )
            .where(MatrizCurricular.id_disciplina == id_disciplina)
            .offset(offset)
            .limit(limit)
        )
        result = await session.exec(statement)
        return list(result.all())

    async def update(self, session: AsyncSession, oferta_disciplina: OfertaDisciplina) -> OfertaDisciplina:
        session.add(oferta_disciplina)
        await session.flush()
        return oferta_disciplina
