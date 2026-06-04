from fastapi import APIRouter, Depends, Query, status
from sqlmodel.ext.asyncio.session import AsyncSession

from controller.solicitacao_academica_controller import SolicitacaoAcademicaController
from dtos.solicitacao_academica_dto import (
    SolicitacaoAcademicaCreate,
    SolicitacaoAcademicaRead,
    SolicitacaoAcademicaStatusUpdate,
)
from repositories.postgres_conn import get_session

router = APIRouter(prefix="/solicitacoes-academicas", tags=["Solicitações Acadêmicas"])
controller = SolicitacaoAcademicaController()


@router.post("", response_model=SolicitacaoAcademicaRead, status_code=status.HTTP_201_CREATED)
async def create_solicitacao_academica(
    data: SolicitacaoAcademicaCreate,
    session: AsyncSession = Depends(get_session),
) -> SolicitacaoAcademicaRead:
    return await controller.create_solicitacao_academica(session=session, data=data)


@router.get("/aluno/{id_aluno}", response_model=list[SolicitacaoAcademicaRead], status_code=status.HTTP_200_OK)
async def list_solicitacoes_by_aluno(
    id_aluno: int,
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    session: AsyncSession = Depends(get_session),
) -> list[SolicitacaoAcademicaRead]:
    return await controller.list_solicitacoes_by_aluno(
        session=session,
        id_aluno=id_aluno,
        limit=limit,
        offset=offset,
    )


@router.get("/{id_solicitacao_academica}", response_model=SolicitacaoAcademicaRead, status_code=status.HTTP_200_OK)
async def get_solicitacao_academica_by_id(
    id_solicitacao_academica: int,
    session: AsyncSession = Depends(get_session),
) -> SolicitacaoAcademicaRead:
    return await controller.get_solicitacao_academica_by_id(
        session=session,
        id_solicitacao_academica=id_solicitacao_academica,
    )


@router.patch("/{id_solicitacao_academica}/status", response_model=SolicitacaoAcademicaRead, status_code=status.HTTP_200_OK)
async def update_solicitacao_status(
    id_solicitacao_academica: int,
    data: SolicitacaoAcademicaStatusUpdate,
    session: AsyncSession = Depends(get_session),
) -> SolicitacaoAcademicaRead:
    return await controller.update_solicitacao_status(
        session=session,
        id_solicitacao_academica=id_solicitacao_academica,
        data=data,
    )
