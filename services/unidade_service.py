from fastapi import HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession

from dtos.endereco_dto import EnderecoRead
from dtos.unidade_dto import UnidadeCreate, UnidadeRead, UnidadeUpdate
from models.endereco import Endereco
from models.unidade import Unidade
from repositories.endereco_repository import EnderecoRepository
from repositories.unidade_repository import UnidadeRepository


class UnidadeService:
    def __init__(self) -> None:
        self.endereco_repository = EnderecoRepository()
        self.unidade_repository = UnidadeRepository()

    async def create_unidade(self, session: AsyncSession, data: UnidadeCreate) -> UnidadeRead:
        if data.id_endereco is None and data.endereco is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Informe id_endereco ou endereco para cadastrar a unidade.",
            )
        if data.id_endereco is not None and data.endereco is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Informe apenas id_endereco ou endereco, não ambos.",
            )

        async with session.begin():
            endereco_obj: Endereco | None = None
            id_endereco = data.id_endereco
            if data.endereco is not None:
                endereco_obj = await self.endereco_repository.create(
                    session,
                    Endereco(**data.endereco.model_dump()),
                )
                id_endereco = endereco_obj.id
            else:
                endereco_obj = await self.endereco_repository.get_by_id(session, data.id_endereco)
                if endereco_obj is None:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Endereço não encontrado.",
                    )

            unidade = Unidade(
                nome=data.nome,
                id_endereco=id_endereco,
                status=data.status,
            )
            unidade = await self.unidade_repository.create(session, unidade)

        return self._to_read(unidade, endereco_obj)

    async def get_unidade_by_id(self, session: AsyncSession, id_unidade: int) -> UnidadeRead:
        unidade = await self.unidade_repository.get_by_id(session, id_unidade)
        if unidade is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Unidade não encontrada.")
        endereco = await self.endereco_repository.get_by_id(session, unidade.id_endereco)
        return self._to_read(unidade, endereco)

    async def list_unidades(
        self,
        session: AsyncSession,
        limit: int = 100,
        offset: int = 0,
    ) -> list[UnidadeRead]:
        unidades = await self.unidade_repository.list(session, limit=limit, offset=offset)
        return [self._to_read(unidade) for unidade in unidades]

    async def update_unidade(
        self,
        session: AsyncSession,
        id_unidade: int,
        data: UnidadeUpdate,
    ) -> UnidadeRead:
        async with session.begin():
            unidade = await self.unidade_repository.get_by_id(session, id_unidade)
            if unidade is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Unidade não encontrada.")
            update_data = data.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                setattr(unidade, field, value)
            unidade = await self.unidade_repository.update(session, unidade)
        return self._to_read(unidade)

    def _to_read(self, unidade: Unidade, endereco: Endereco | None = None) -> UnidadeRead:
        endereco_read = None
        if endereco is not None:
            endereco_read = EnderecoRead(
                id=endereco.id,
                rua=endereco.rua,
                cep=endereco.cep,
                numero=endereco.numero,
                bairro=endereco.bairro,
                estado=endereco.estado,
                cidade=endereco.cidade,
                complemento=endereco.complemento,
            )
        return UnidadeRead(
            id=unidade.id,
            nome=unidade.nome,
            id_endereco=unidade.id_endereco,
            status=unidade.status,
            endereco=endereco_read,
        )
