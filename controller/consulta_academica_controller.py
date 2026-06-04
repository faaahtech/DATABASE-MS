from sqlmodel.ext.asyncio.session import AsyncSession

from dtos.consulta_dto import (
    DisciplinaCursoUnidadeRead,
    OfertaDisciplinaRead,
    PeriodoLetivoAtivoRead,
    ResumoAlunoRead,
)
from dtos.nota_dto import NotaPorAlunoRead
from dtos.presenca_dto import PresencaPorAlunoRead
from services.consulta_academica_service import ConsultaAcademicaService


class ConsultaAcademicaController:
    def __init__(self) -> None:
        self.service = ConsultaAcademicaService()

    async def consultar_disciplinas_por_curso_unidade(
        self,
        session: AsyncSession,
        id_curso_unidade: int,
        limit: int = 100,
        offset: int = 0,
    ) -> list[DisciplinaCursoUnidadeRead]:
        return await self.service.consultar_disciplinas_por_curso_unidade(
            session=session,
            id_curso_unidade=id_curso_unidade,
            limit=limit,
            offset=offset,
        )

    async def consultar_periodo_letivo_ativo(
        self,
        session: AsyncSession,
    ) -> PeriodoLetivoAtivoRead:
        return await self.service.consultar_periodo_letivo_ativo(session=session)

    async def consultar_ofertas_por_periodo(
        self,
        session: AsyncSession,
        id_periodo_letivo: int,
        limit: int = 100,
        offset: int = 0,
    ) -> list[OfertaDisciplinaRead]:
        return await self.service.consultar_ofertas_por_periodo(
            session=session,
            id_periodo_letivo=id_periodo_letivo,
            limit=limit,
            offset=offset,
        )

    async def consultar_resumo_aluno(
        self,
        session: AsyncSession,
        id_aluno: int,
    ) -> ResumoAlunoRead:
        return await self.service.consultar_resumo_aluno(session=session, id_aluno=id_aluno)

    async def consultar_notas_por_aluno(
        self,
        session: AsyncSession,
        id_aluno: int,
        limit: int = 100,
        offset: int = 0,
    ) -> list[NotaPorAlunoRead]:
        return await self.service.consultar_notas_por_aluno(
            session=session,
            id_aluno=id_aluno,
            limit=limit,
            offset=offset,
        )

    async def consultar_presencas_por_aluno(
        self,
        session: AsyncSession,
        id_aluno: int,
        limit: int = 100,
        offset: int = 0,
    ) -> list[PresencaPorAlunoRead]:
        return await self.service.consultar_presencas_por_aluno(
            session=session,
            id_aluno=id_aluno,
            limit=limit,
            offset=offset,
        )
