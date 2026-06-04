from sqlmodel.ext.asyncio.session import AsyncSession

from dtos.oferta_disciplina_dto import OfertaDisciplinaCreate, OfertaDisciplinaRead, OfertaDisciplinaUpdate
from services.oferta_disciplina_service import OfertaDisciplinaService


class OfertaDisciplinaController:
    def __init__(self) -> None:
        self.service = OfertaDisciplinaService()

    async def create_oferta_disciplina(
        self,
        session: AsyncSession,
        data: OfertaDisciplinaCreate,
    ) -> OfertaDisciplinaRead:
        return await self.service.create_oferta_disciplina(session=session, data=data)

    async def get_oferta_disciplina_by_id(
        self,
        session: AsyncSession,
        id_oferta_disciplina: int,
    ) -> OfertaDisciplinaRead:
        return await self.service.get_oferta_disciplina_by_id(
            session=session,
            id_oferta_disciplina=id_oferta_disciplina,
        )

    async def list_ofertas_by_periodo_letivo(
        self,
        session: AsyncSession,
        id_periodo_letivo: int,
        limit: int = 100,
        offset: int = 0,
    ) -> list[OfertaDisciplinaRead]:
        return await self.service.list_ofertas_by_periodo_letivo(
            session=session,
            id_periodo_letivo=id_periodo_letivo,
            limit=limit,
            offset=offset,
        )

    async def list_ofertas_by_curso_unidade(
        self,
        session: AsyncSession,
        id_curso_unidade: int,
        limit: int = 100,
        offset: int = 0,
    ) -> list[OfertaDisciplinaRead]:
        return await self.service.list_ofertas_by_curso_unidade(
            session=session,
            id_curso_unidade=id_curso_unidade,
            limit=limit,
            offset=offset,
        )

    async def list_ofertas_by_disciplina(
        self,
        session: AsyncSession,
        id_disciplina: int,
        limit: int = 100,
        offset: int = 0,
    ) -> list[OfertaDisciplinaRead]:
        return await self.service.list_ofertas_by_disciplina(
            session=session,
            id_disciplina=id_disciplina,
            limit=limit,
            offset=offset,
        )

    async def update_oferta_disciplina(
        self,
        session: AsyncSession,
        id_oferta_disciplina: int,
        data: OfertaDisciplinaUpdate,
    ) -> OfertaDisciplinaRead:
        return await self.service.update_oferta_disciplina(
            session=session,
            id_oferta_disciplina=id_oferta_disciplina,
            data=data,
        )
