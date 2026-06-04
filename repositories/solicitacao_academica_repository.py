from __future__ import annotations

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from models.solicitacao_academica import SolicitacaoAcademica


class SolicitacaoAcademicaRepository:
    async def create(
        self,
        session: AsyncSession,
        solicitacao: SolicitacaoAcademica,
    ) -> SolicitacaoAcademica:
        session.add(solicitacao)
        await session.flush()
        return solicitacao

    async def get_by_id(
        self,
        session: AsyncSession,
        id_solicitacao_academica: int,
    ) -> SolicitacaoAcademica | None:
        return await session.get(SolicitacaoAcademica, id_solicitacao_academica)

    async def get_by_protocolo(
        self,
        session: AsyncSession,
        protocolo: str,
    ) -> SolicitacaoAcademica | None:
        statement = select(SolicitacaoAcademica).where(
            SolicitacaoAcademica.protocolo == protocolo.strip().upper()
        )
        result = await session.exec(statement)
        return result.first()

    async def list_by_aluno(
        self,
        session: AsyncSession,
        id_aluno: int,
        limit: int = 100,
        offset: int = 0,
    ) -> list[SolicitacaoAcademica]:
        statement = (
            select(SolicitacaoAcademica)
            .where(SolicitacaoAcademica.id_aluno == id_aluno)
            .order_by(SolicitacaoAcademica.criado_em.desc(), SolicitacaoAcademica.id.desc())
            .offset(offset)
            .limit(limit)
        )
        result = await session.exec(statement)
        return list(result.all())

    async def update(
        self,
        session: AsyncSession,
        solicitacao: SolicitacaoAcademica,
    ) -> SolicitacaoAcademica:
        session.add(solicitacao)
        await session.flush()
        return solicitacao
