from __future__ import annotations

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from models.historico_solicitacao import HistoricoSolicitacao


class HistoricoSolicitacaoRepository:
    async def create(
        self,
        session: AsyncSession,
        historico: HistoricoSolicitacao,
    ) -> HistoricoSolicitacao:
        session.add(historico)
        await session.flush()
        return historico

    async def list_by_solicitacao(
        self,
        session: AsyncSession,
        id_solicitacao_academica: int,
        limit: int = 100,
        offset: int = 0,
    ) -> list[HistoricoSolicitacao]:
        statement = (
            select(HistoricoSolicitacao)
            .where(HistoricoSolicitacao.id_solicitacao_academica == id_solicitacao_academica)
            .order_by(HistoricoSolicitacao.criado_em, HistoricoSolicitacao.id)
            .offset(offset)
            .limit(limit)
        )
        result = await session.exec(statement)
        return list(result.all())
