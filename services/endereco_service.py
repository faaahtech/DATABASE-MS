from fastapi import HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession

from dtos.endereco_dto import EnderecoCreate, EnderecoRead
from models.endereco import Endereco
from repositories.endereco_repository import EnderecoRepository


class EnderecoService:
    def __init__(self) -> None:
        self.endereco_repository = EnderecoRepository()

    async def create_endereco(self, session: AsyncSession, data: EnderecoCreate) -> EnderecoRead:
        endereco = Endereco(**data.model_dump())
        async with session.begin():
            endereco = await self.endereco_repository.create(session, endereco)
        return self._to_read(endereco)

    async def get_endereco_by_id(self, session: AsyncSession, id_endereco: int) -> EnderecoRead:
        endereco = await self.endereco_repository.get_by_id(session, id_endereco)
        if endereco is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Endereço não encontrado.",
            )
        return self._to_read(endereco)

    async def list_enderecos(
        self,
        session: AsyncSession,
        limit: int = 100,
        offset: int = 0,
    ) -> list[EnderecoRead]:
        enderecos = await self.endereco_repository.list(session, limit=limit, offset=offset)
        return [self._to_read(endereco) for endereco in enderecos]

    def _to_read(self, endereco: Endereco) -> EnderecoRead:
        return EnderecoRead(
            id=endereco.id,
            rua=endereco.rua,
            cep=endereco.cep,
            numero=endereco.numero,
            bairro=endereco.bairro,
            estado=endereco.estado,
            cidade=endereco.cidade,
            complemento=endereco.complemento,
        )
