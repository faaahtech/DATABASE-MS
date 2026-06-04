from datetime import datetime

from fastapi import HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession

from dtos.base_conhecimento_dto import (
    BaseConhecimentoCreate,
    BaseConhecimentoRead,
    BaseConhecimentoUpdate,
)
from models.base_conhecimento import BaseConhecimento, CategoriaBaseConhecimento
from repositories.base_conhecimento_repository import BaseConhecimentoRepository


class BaseConhecimentoService:
    def __init__(self) -> None:
        self.base_repository = BaseConhecimentoRepository()

    async def create_base_conhecimento(
        self,
        session: AsyncSession,
        data: BaseConhecimentoCreate,
    ) -> BaseConhecimentoRead:
        self._validate_payload(data)
        async with session.begin():
            base = BaseConhecimento(**data.model_dump())
            base = await self.base_repository.create(session, base)
        return self._to_read(base)

    async def list_bases_conhecimento(
        self,
        session: AsyncSession,
        limit: int = 100,
        offset: int = 0,
    ) -> list[BaseConhecimentoRead]:
        bases = await self.base_repository.list(session, limit=limit, offset=offset)
        return [self._to_read(base) for base in bases]

    async def get_base_conhecimento_by_id(
        self,
        session: AsyncSession,
        id_base_conhecimento: int,
    ) -> BaseConhecimentoRead:
        base = await self.base_repository.get_by_id(session, id_base_conhecimento)
        if base is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Base de conhecimento não encontrada.")
        return self._to_read(base)

    async def list_bases_by_categoria(
        self,
        session: AsyncSession,
        categoria: CategoriaBaseConhecimento,
        limit: int = 100,
        offset: int = 0,
    ) -> list[BaseConhecimentoRead]:
        bases = await self.base_repository.list_by_categoria(
            session=session,
            categoria=categoria,
            limit=limit,
            offset=offset,
        )
        return [self._to_read(base) for base in bases]

    async def update_base_conhecimento(
        self,
        session: AsyncSession,
        id_base_conhecimento: int,
        data: BaseConhecimentoUpdate,
    ) -> BaseConhecimentoRead:
        async with session.begin():
            base = await self.base_repository.get_by_id(session, id_base_conhecimento)
            if base is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Base de conhecimento não encontrada.")

            update_data = data.model_dump(exclude_unset=True)
            merged_data = {
                "titulo": update_data.get("titulo", base.titulo),
                "categoria": update_data.get("categoria", base.categoria),
                "pergunta_base": update_data.get("pergunta_base", base.pergunta_base),
                "resposta": update_data.get("resposta", base.resposta),
                "tags": update_data.get("tags", base.tags),
                "status": update_data.get("status", base.status),
            }
            self._validate_payload(BaseConhecimentoCreate(**merged_data))

            for field, value in update_data.items():
                setattr(base, field, value)
            base.atualizado_em = datetime.utcnow()
            base = await self.base_repository.update(session, base)
        return self._to_read(base)

    def _validate_payload(self, data: BaseConhecimentoCreate) -> None:
        if not data.titulo.strip():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Título da base de conhecimento é obrigatório.")
        if not data.resposta.strip():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Resposta da base de conhecimento é obrigatória.")
        if data.tags is not None:
            normalized_tags = [tag.strip() for tag in data.tags if tag and tag.strip()]
            if len(normalized_tags) != len(data.tags):
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Tags não podem ser vazias.")

    def _to_read(self, base: BaseConhecimento) -> BaseConhecimentoRead:
        return BaseConhecimentoRead(
            id=base.id,
            titulo=base.titulo,
            categoria=base.categoria,
            pergunta_base=base.pergunta_base,
            resposta=base.resposta,
            tags=base.tags,
            status=base.status,
            atualizado_em=base.atualizado_em,
        )
