from sqlmodel.ext.asyncio.session import AsyncSession

from dtos.base_conhecimento_dto import (
    BaseConhecimentoCreate,
    BaseConhecimentoRead,
    BaseConhecimentoUpdate,
)
from models.base_conhecimento import CategoriaBaseConhecimento
from services.base_conhecimento_service import BaseConhecimentoService


class BaseConhecimentoController:
    def __init__(self) -> None:
        self.service = BaseConhecimentoService()

    async def create_base_conhecimento(
        self,
        session: AsyncSession,
        data: BaseConhecimentoCreate,
    ) -> BaseConhecimentoRead:
        return await self.service.create_base_conhecimento(session=session, data=data)

    async def list_bases_conhecimento(
        self,
        session: AsyncSession,
        limit: int = 100,
        offset: int = 0,
    ) -> list[BaseConhecimentoRead]:
        return await self.service.list_bases_conhecimento(session=session, limit=limit, offset=offset)

    async def get_base_conhecimento_by_id(
        self,
        session: AsyncSession,
        id_base_conhecimento: int,
    ) -> BaseConhecimentoRead:
        return await self.service.get_base_conhecimento_by_id(
            session=session,
            id_base_conhecimento=id_base_conhecimento,
        )

    async def list_bases_by_categoria(
        self,
        session: AsyncSession,
        categoria: CategoriaBaseConhecimento,
        limit: int = 100,
        offset: int = 0,
    ) -> list[BaseConhecimentoRead]:
        return await self.service.list_bases_by_categoria(
            session=session,
            categoria=categoria,
            limit=limit,
            offset=offset,
        )

    async def update_base_conhecimento(
        self,
        session: AsyncSession,
        id_base_conhecimento: int,
        data: BaseConhecimentoUpdate,
    ) -> BaseConhecimentoRead:
        return await self.service.update_base_conhecimento(
            session=session,
            id_base_conhecimento=id_base_conhecimento,
            data=data,
        )
