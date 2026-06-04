from sqlmodel.ext.asyncio.session import AsyncSession

from dtos.solicitacao_academica_dto import (
    SolicitacaoAcademicaCreate,
    SolicitacaoAcademicaRead,
    SolicitacaoAcademicaStatusUpdate,
)
from services.solicitacao_academica_service import SolicitacaoAcademicaService


class SolicitacaoAcademicaController:
    def __init__(self) -> None:
        self.service = SolicitacaoAcademicaService()

    async def create_solicitacao_academica(
        self,
        session: AsyncSession,
        data: SolicitacaoAcademicaCreate,
    ) -> SolicitacaoAcademicaRead:
        return await self.service.create_solicitacao_academica(session=session, data=data)

    async def get_solicitacao_academica_by_id(
        self,
        session: AsyncSession,
        id_solicitacao_academica: int,
    ) -> SolicitacaoAcademicaRead:
        return await self.service.get_solicitacao_academica_by_id(
            session=session,
            id_solicitacao_academica=id_solicitacao_academica,
        )

    async def list_solicitacoes_by_aluno(
        self,
        session: AsyncSession,
        id_aluno: int,
        limit: int = 100,
        offset: int = 0,
    ) -> list[SolicitacaoAcademicaRead]:
        return await self.service.list_solicitacoes_by_aluno(
            session=session,
            id_aluno=id_aluno,
            limit=limit,
            offset=offset,
        )

    async def update_solicitacao_status(
        self,
        session: AsyncSession,
        id_solicitacao_academica: int,
        data: SolicitacaoAcademicaStatusUpdate,
    ) -> SolicitacaoAcademicaRead:
        return await self.service.update_solicitacao_status(
            session=session,
            id_solicitacao_academica=id_solicitacao_academica,
            data=data,
        )
