from sqlmodel.ext.asyncio.session import AsyncSession

from dtos.unidade_dto import UnidadeCreate, UnidadeRead, UnidadeUpdate
from services.unidade_service import UnidadeService


class UnidadeController:
    def __init__(self) -> None:
        self.service = UnidadeService()

    async def create_unidade(self, session: AsyncSession, data: UnidadeCreate) -> UnidadeRead:
        return await self.service.create_unidade(session=session, data=data)

    async def get_unidade_by_id(self, session: AsyncSession, id_unidade: int) -> UnidadeRead:
        return await self.service.get_unidade_by_id(session=session, id_unidade=id_unidade)

    async def list_unidades(
        self,
        session: AsyncSession,
        limit: int = 100,
        offset: int = 0,
    ) -> list[UnidadeRead]:
        return await self.service.list_unidades(session=session, limit=limit, offset=offset)

    async def update_unidade(self, session: AsyncSession, id_unidade: int, data: UnidadeUpdate) -> UnidadeRead:
        return await self.service.update_unidade(session=session, id_unidade=id_unidade, data=data)
