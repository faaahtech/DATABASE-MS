from sqlmodel.ext.asyncio.session import AsyncSession

from dtos.endereco_dto import EnderecoCreate, EnderecoRead
from services.endereco_service import EnderecoService


class EnderecoController:
    def __init__(self) -> None:
        self.service = EnderecoService()

    async def create_endereco(self, session: AsyncSession, data: EnderecoCreate) -> EnderecoRead:
        return await self.service.create_endereco(session=session, data=data)

    async def get_endereco_by_id(self, session: AsyncSession, id_endereco: int) -> EnderecoRead:
        return await self.service.get_endereco_by_id(session=session, id_endereco=id_endereco)

    async def list_enderecos(
        self,
        session: AsyncSession,
        limit: int = 100,
        offset: int = 0,
    ) -> list[EnderecoRead]:
        return await self.service.list_enderecos(session=session, limit=limit, offset=offset)
