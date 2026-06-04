from datetime import datetime

from fastapi import HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession

from dtos.solicitacao_academica_dto import (
    SolicitacaoAcademicaCreate,
    SolicitacaoAcademicaRead,
    SolicitacaoAcademicaStatusUpdate,
)
from models.historico_solicitacao import HistoricoSolicitacao, StatusHistoricoSolicitacao
from models.solicitacao_academica import SolicitacaoAcademica, StatusSolicitacaoAcademica
from repositories.aluno_repository import AlunoRepository
from repositories.historico_solicitacao_repository import HistoricoSolicitacaoRepository
from repositories.matricula_curso_repository import MatriculaCursoRepository
from repositories.solicitacao_academica_repository import SolicitacaoAcademicaRepository
from utils.protocol import generate_protocol


class SolicitacaoAcademicaService:
    def __init__(self) -> None:
        self.solicitacao_repository = SolicitacaoAcademicaRepository()
        self.historico_repository = HistoricoSolicitacaoRepository()
        self.aluno_repository = AlunoRepository()
        self.matricula_curso_repository = MatriculaCursoRepository()

    async def create_solicitacao_academica(
        self,
        session: AsyncSession,
        data: SolicitacaoAcademicaCreate,
    ) -> SolicitacaoAcademicaRead:
        if data.observacao is not None and not data.observacao.strip():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Observação não pode ser vazia.")

        async with session.begin():
            await self._validate_aluno_and_matricula(
                session=session,
                id_aluno=data.id_aluno,
                id_matricula_curso=data.id_matricula_curso,
            )
            protocolo = await self._generate_unique_protocol(session)
            solicitacao = SolicitacaoAcademica(
                **data.model_dump(),
                protocolo=protocolo,
                status=StatusSolicitacaoAcademica.ABERTA,
            )
            solicitacao = await self.solicitacao_repository.create(session, solicitacao)
        return self._to_read(solicitacao)

    async def get_solicitacao_academica_by_id(
        self,
        session: AsyncSession,
        id_solicitacao_academica: int,
    ) -> SolicitacaoAcademicaRead:
        solicitacao = await self.solicitacao_repository.get_by_id(session, id_solicitacao_academica)
        if solicitacao is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Solicitação acadêmica não encontrada.")
        return self._to_read(solicitacao)

    async def list_solicitacoes_by_aluno(
        self,
        session: AsyncSession,
        id_aluno: int,
        limit: int = 100,
        offset: int = 0,
    ) -> list[SolicitacaoAcademicaRead]:
        aluno = await self.aluno_repository.get_by_id(session, id_aluno)
        if aluno is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Aluno não encontrado.")
        solicitacoes = await self.solicitacao_repository.list_by_aluno(
            session=session,
            id_aluno=id_aluno,
            limit=limit,
            offset=offset,
        )
        return [self._to_read(solicitacao) for solicitacao in solicitacoes]

    async def update_solicitacao_status(
        self,
        session: AsyncSession,
        id_solicitacao_academica: int,
        data: SolicitacaoAcademicaStatusUpdate,
    ) -> SolicitacaoAcademicaRead:
        if data.observacao is not None and not data.observacao.strip():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Observação não pode ser vazia.")

        async with session.begin():
            solicitacao = await self.solicitacao_repository.get_by_id(session, id_solicitacao_academica)
            if solicitacao is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Solicitação acadêmica não encontrada.")
            if solicitacao.status == data.status:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Novo status deve ser diferente do status atual.",
                )

            status_anterior = solicitacao.status
            solicitacao.status = data.status
            solicitacao.observacao = data.observacao if data.observacao is not None else solicitacao.observacao
            solicitacao.atualizado_em = datetime.utcnow()

            historico = HistoricoSolicitacao(
                id_solicitacao_academica=solicitacao.id,
                status_anterior=self._to_historico_status(status_anterior),
                status_novo=self._to_historico_status(data.status),
                observacao=data.observacao,
            )
            await self.historico_repository.create(session, historico)
            solicitacao = await self.solicitacao_repository.update(session, solicitacao)
        return self._to_read(solicitacao)

    async def _validate_aluno_and_matricula(
        self,
        session: AsyncSession,
        id_aluno: int,
        id_matricula_curso: int | None,
    ) -> None:
        aluno = await self.aluno_repository.get_by_id(session, id_aluno)
        if aluno is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Aluno não encontrado.")
        if id_matricula_curso is None:
            return
        matricula = await self.matricula_curso_repository.get_by_id(session, id_matricula_curso)
        if matricula is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Matrícula de curso não encontrada.")
        if matricula.id_aluno != id_aluno:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Matrícula de curso não pertence ao aluno informado.",
            )

    async def _generate_unique_protocol(self, session: AsyncSession) -> str:
        for _ in range(5):
            protocolo = generate_protocol("SOL")
            existente = await self.solicitacao_repository.get_by_protocolo(session, protocolo)
            if existente is None:
                return protocolo
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Não foi possível gerar protocolo único para a solicitação.",
        )

    def _to_historico_status(self, status_value: StatusSolicitacaoAcademica) -> StatusHistoricoSolicitacao:
        return StatusHistoricoSolicitacao(status_value.value)

    def _to_read(self, solicitacao: SolicitacaoAcademica) -> SolicitacaoAcademicaRead:
        return SolicitacaoAcademicaRead(
            id=solicitacao.id,
            id_aluno=solicitacao.id_aluno,
            id_matricula_curso=solicitacao.id_matricula_curso,
            tipo=solicitacao.tipo,
            protocolo=solicitacao.protocolo,
            status=solicitacao.status,
            origem=solicitacao.origem,
            criado_em=solicitacao.criado_em,
            atualizado_em=solicitacao.atualizado_em,
            observacao=solicitacao.observacao,
        )
