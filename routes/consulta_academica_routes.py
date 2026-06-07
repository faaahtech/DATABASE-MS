from fastapi import APIRouter, Depends, Query, status
from sqlmodel.ext.asyncio.session import AsyncSession

from controller.consulta_academica_controller import ConsultaAcademicaController
from dtos.consulta_dto import (
    DisciplinaCursoUnidadeRead,
    OfertaDisciplinaRead,
    PeriodoLetivoAtivoRead,
    ResumoAlunoRead,
    ResumoSemestreAtualRead,
)
from dtos.nota_dto import NotaPorAlunoRead
from dtos.presenca_dto import PresencaPorAlunoRead
from repositories.postgres_conn import get_session

router = APIRouter(prefix="/consultas", tags=["Consultas Acadêmicas"])
controller = ConsultaAcademicaController()


@router.get(
    "/periodo-letivo/ativo",
    response_model=PeriodoLetivoAtivoRead,
    status_code=status.HTTP_200_OK,
)
async def consultar_periodo_letivo_ativo(
    session: AsyncSession = Depends(get_session),
) -> PeriodoLetivoAtivoRead:
    return await controller.consultar_periodo_letivo_ativo(session=session)


@router.get(
    "/curso-unidade/{id_curso_unidade}/disciplinas",
    response_model=list[DisciplinaCursoUnidadeRead],
    status_code=status.HTTP_200_OK,
)
async def consultar_disciplinas_por_curso_unidade(
    id_curso_unidade: int,
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    session: AsyncSession = Depends(get_session),
) -> list[DisciplinaCursoUnidadeRead]:
    return await controller.consultar_disciplinas_por_curso_unidade(
        session=session,
        id_curso_unidade=id_curso_unidade,
        limit=limit,
        offset=offset,
    )


@router.get(
    "/periodo-letivo/{id_periodo_letivo}/ofertas",
    response_model=list[OfertaDisciplinaRead],
    status_code=status.HTTP_200_OK,
)
async def consultar_ofertas_por_periodo(
    id_periodo_letivo: int,
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    session: AsyncSession = Depends(get_session),
) -> list[OfertaDisciplinaRead]:
    return await controller.consultar_ofertas_por_periodo(
        session=session,
        id_periodo_letivo=id_periodo_letivo,
        limit=limit,
        offset=offset,
    )


@router.get(
    "/aluno/{id_aluno}/notas",
    response_model=list[NotaPorAlunoRead],
    status_code=status.HTTP_200_OK,
)
async def consultar_notas_por_aluno(
    id_aluno: int,
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    session: AsyncSession = Depends(get_session),
) -> list[NotaPorAlunoRead]:
    return await controller.consultar_notas_por_aluno(
        session=session,
        id_aluno=id_aluno,
        limit=limit,
        offset=offset,
    )


@router.get(
    "/aluno/{id_aluno}/presencas",
    response_model=list[PresencaPorAlunoRead],
    status_code=status.HTTP_200_OK,
)
async def consultar_presencas_por_aluno(
    id_aluno: int,
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    session: AsyncSession = Depends(get_session),
) -> list[PresencaPorAlunoRead]:
    return await controller.consultar_presencas_por_aluno(
        session=session,
        id_aluno=id_aluno,
        limit=limit,
        offset=offset,
    )


@router.get(
    "/aluno/{id_aluno}/resumo-semestre-atual",
    response_model=ResumoSemestreAtualRead,
    status_code=status.HTTP_200_OK,
)
async def consultar_resumo_semestre_atual(
    id_aluno: int,
    session: AsyncSession = Depends(get_session),
) -> ResumoSemestreAtualRead:
    return await controller.consultar_resumo_semestre_atual(session=session, id_aluno=id_aluno)


@router.get(
    "/aluno/{id_aluno}/resumo",
    response_model=ResumoAlunoRead,
    status_code=status.HTTP_200_OK,
)
async def consultar_resumo_aluno(
    id_aluno: int,
    session: AsyncSession = Depends(get_session),
) -> ResumoAlunoRead:
    return await controller.consultar_resumo_aluno(session=session, id_aluno=id_aluno)
