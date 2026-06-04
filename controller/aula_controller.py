from sqlmodel.ext.asyncio.session import AsyncSession

from dtos.aula_dto import AulaCreate, AulaRead, AulaUpdate
from services.aula_service import AulaService


class AulaController:
    def __init__(self) -> None:
        self.service = AulaService()

    async def create_aula(self, session: AsyncSession, data: AulaCreate) -> AulaRead:
        return await self.service.create_aula(session=session, data=data)

    async def get_aula_by_id(self, session: AsyncSession, id_aula: int) -> AulaRead:
        return await self.service.get_aula_by_id(session=session, id_aula=id_aula)

    async def list_aulas_by_oferta_disciplina(
        self,
        session: AsyncSession,
        id_oferta_disciplina: int,
        limit: int = 100,
        offset: int = 0,
    ) -> list[AulaRead]:
        return await self.service.list_aulas_by_oferta_disciplina(
            session=session,
            id_oferta_disciplina=id_oferta_disciplina,
            limit=limit,
            offset=offset,
        )

    async def update_aula(self, session: AsyncSession, id_aula: int, data: AulaUpdate) -> AulaRead:
        return await self.service.update_aula(session=session, id_aula=id_aula, data=data)
