from sqlmodel.ext.asyncio.session import AsyncSession

from dtos.avaliacao_dto import AvaliacaoCreate, AvaliacaoRead, AvaliacaoUpdate
from services.avaliacao_service import AvaliacaoService


class AvaliacaoController:
    def __init__(self) -> None:
        self.service = AvaliacaoService()

    async def create_avaliacao(self, session: AsyncSession, data: AvaliacaoCreate) -> AvaliacaoRead:
        return await self.service.create_avaliacao(session=session, data=data)

    async def get_avaliacao_by_id(self, session: AsyncSession, id_avaliacao: int) -> AvaliacaoRead:
        return await self.service.get_avaliacao_by_id(session=session, id_avaliacao=id_avaliacao)

    async def list_avaliacoes_by_oferta_disciplina(
        self,
        session: AsyncSession,
        id_oferta_disciplina: int,
        limit: int = 100,
        offset: int = 0,
    ) -> list[AvaliacaoRead]:
        return await self.service.list_avaliacoes_by_oferta_disciplina(
            session=session,
            id_oferta_disciplina=id_oferta_disciplina,
            limit=limit,
            offset=offset,
        )

    async def update_avaliacao(
        self,
        session: AsyncSession,
        id_avaliacao: int,
        data: AvaliacaoUpdate,
    ) -> AvaliacaoRead:
        return await self.service.update_avaliacao(
            session=session,
            id_avaliacao=id_avaliacao,
            data=data,
        )
