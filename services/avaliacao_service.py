from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlmodel.ext.asyncio.session import AsyncSession

from dtos.avaliacao_dto import AvaliacaoCreate, AvaliacaoRead, AvaliacaoUpdate
from models.avaliacao import Avaliacao
from repositories.avaliacao_repository import AvaliacaoRepository
from repositories.oferta_disciplina_repository import OfertaDisciplinaRepository


class AvaliacaoService:
    def __init__(self) -> None:
        self.avaliacao_repository = AvaliacaoRepository()
        self.oferta_disciplina_repository = OfertaDisciplinaRepository()

    async def create_avaliacao(self, session: AsyncSession, data: AvaliacaoCreate) -> AvaliacaoRead:
        nome = self._normalize_nome(data.nome)
        self._validate_peso(data.peso)
        avaliacao = Avaliacao(**{**data.model_dump(), "nome": nome})

        try:
            async with session.begin():
                await self._validate_oferta_disciplina_exists(session, data.id_oferta_disciplina)
                exists = await self.avaliacao_repository.exists_by_oferta_and_nome(
                    session=session,
                    id_oferta_disciplina=data.id_oferta_disciplina,
                    nome=nome,
                )
                if exists:
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail="Já existe avaliação com este nome para esta oferta de disciplina.",
                    )

                avaliacao = await self.avaliacao_repository.create(session, avaliacao)
        except IntegrityError as exc:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Não foi possível criar avaliação por conflito de dados únicos.",
            ) from exc

        return self._to_read(avaliacao)

    async def get_avaliacao_by_id(self, session: AsyncSession, id_avaliacao: int) -> AvaliacaoRead:
        avaliacao = await self.avaliacao_repository.get_by_id(session, id_avaliacao)
        if avaliacao is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Avaliação não encontrada.")
        return self._to_read(avaliacao)

    async def list_avaliacoes_by_oferta_disciplina(
        self,
        session: AsyncSession,
        id_oferta_disciplina: int,
        limit: int = 100,
        offset: int = 0,
    ) -> list[AvaliacaoRead]:
        await self._validate_oferta_disciplina_exists(session, id_oferta_disciplina)
        avaliacoes = await self.avaliacao_repository.list_by_oferta_disciplina(
            session=session,
            id_oferta_disciplina=id_oferta_disciplina,
            limit=limit,
            offset=offset,
        )
        return [self._to_read(avaliacao) for avaliacao in avaliacoes]

    async def update_avaliacao(
        self,
        session: AsyncSession,
        id_avaliacao: int,
        data: AvaliacaoUpdate,
    ) -> AvaliacaoRead:
        try:
            async with session.begin():
                avaliacao = await self.avaliacao_repository.get_by_id(session, id_avaliacao)
                if avaliacao is None:
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Avaliação não encontrada.")

                update_data = data.model_dump(exclude_unset=True)

                if "id_oferta_disciplina" in update_data and update_data["id_oferta_disciplina"] is not None:
                    await self._validate_oferta_disciplina_exists(session, update_data["id_oferta_disciplina"])
                if "nome" in update_data and update_data["nome"] is not None:
                    update_data["nome"] = self._normalize_nome(update_data["nome"])
                if "peso" in update_data and update_data["peso"] is not None:
                    self._validate_peso(update_data["peso"])

                novo_id_oferta_disciplina = update_data.get("id_oferta_disciplina", avaliacao.id_oferta_disciplina)
                novo_nome = update_data.get("nome", avaliacao.nome)

                existente = await self.avaliacao_repository.get_by_oferta_and_nome(
                    session=session,
                    id_oferta_disciplina=novo_id_oferta_disciplina,
                    nome=novo_nome,
                )
                if existente is not None and existente.id != id_avaliacao:
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail="Já existe outra avaliação com este nome para esta oferta de disciplina.",
                    )

                for field, value in update_data.items():
                    setattr(avaliacao, field, value)

                avaliacao = await self.avaliacao_repository.update(session, avaliacao)
        except IntegrityError as exc:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Não foi possível atualizar avaliação por conflito de dados únicos.",
            ) from exc

        return self._to_read(avaliacao)

    async def _validate_oferta_disciplina_exists(self, session: AsyncSession, id_oferta_disciplina: int) -> None:
        oferta_disciplina = await self.oferta_disciplina_repository.get_by_id(session, id_oferta_disciplina)
        if oferta_disciplina is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Oferta de disciplina não encontrada.")

    def _normalize_nome(self, nome: str) -> str:
        if not isinstance(nome, str) or not nome.strip():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Nome da avaliação é obrigatório.")
        return nome.strip()

    def _validate_peso(self, peso: Decimal) -> None:
        if peso <= Decimal("0"):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Peso da avaliação deve ser positivo.")

    def _to_read(self, avaliacao: Avaliacao) -> AvaliacaoRead:
        return AvaliacaoRead(
            id=avaliacao.id,
            id_oferta_disciplina=avaliacao.id_oferta_disciplina,
            nome=avaliacao.nome,
            tipo=avaliacao.tipo,
            peso=avaliacao.peso,
            data=avaliacao.data,
        )
