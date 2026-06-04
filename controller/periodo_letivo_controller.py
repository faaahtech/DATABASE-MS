from sqlmodel.ext.asyncio.session import AsyncSession

from dtos.periodo_letivo_dto import PeriodoLetivoCreate, PeriodoLetivoRead, PeriodoLetivoUpdate
from services.periodo_letivo_service import PeriodoLetivoService


class PeriodoLetivoController:
    def __init__(self) -> None:
        self.service = PeriodoLetivoService()

    async def create_periodo_letivo(self, session: AsyncSession, data: PeriodoLetivoCreate) -> PeriodoLetivoRead:
        return await self.service.create_periodo_letivo(session=session, data=data)

    async def get_periodo_letivo_by_id(self, session: AsyncSession, id_periodo_letivo: int) -> PeriodoLetivoRead:
        return await self.service.get_periodo_letivo_by_id(session=session, id_periodo_letivo=id_periodo_letivo)

    async def get_periodo_letivo_ativo(self, session: AsyncSession) -> PeriodoLetivoRead:
        return await self.service.get_periodo_letivo_ativo(session=session)

    async def list_periodos_letivos(
        self,
        session: AsyncSession,
        limit: int = 100,
        offset: int = 0,
    ) -> list[PeriodoLetivoRead]:
        return await self.service.list_periodos_letivos(session=session, limit=limit, offset=offset)

    async def update_periodo_letivo(
        self,
        session: AsyncSession,
        id_periodo_letivo: int,
        data: PeriodoLetivoUpdate,
    ) -> PeriodoLetivoRead:
        return await self.service.update_periodo_letivo(session=session, id_periodo_letivo=id_periodo_letivo, data=data)

    async def ativar_periodo_letivo(self, session: AsyncSession, id_periodo_letivo: int) -> PeriodoLetivoRead:
        return await self.service.ativar_periodo_letivo(session=session, id_periodo_letivo=id_periodo_letivo)

    async def encerrar_periodo_letivo(self, session: AsyncSession, id_periodo_letivo: int) -> PeriodoLetivoRead:
        return await self.service.encerrar_periodo_letivo(session=session, id_periodo_letivo=id_periodo_letivo)
