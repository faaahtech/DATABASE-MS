from sqlmodel.ext.asyncio.session import AsyncSession

from dtos.disciplina_dto import DisciplinaCreate, DisciplinaRead, DisciplinaUpdate
from services.disciplina_service import DisciplinaService


class DisciplinaController:
    def __init__(self) -> None:
        self.service = DisciplinaService()

    async def create_disciplina(self, session: AsyncSession, data: DisciplinaCreate) -> DisciplinaRead:
        return await self.service.create_disciplina(session=session, data=data)

    async def get_disciplina_by_id(self, session: AsyncSession, id_disciplina: int) -> DisciplinaRead:
        return await self.service.get_disciplina_by_id(session=session, id_disciplina=id_disciplina)

    async def get_disciplina_by_codigo(self, session: AsyncSession, codigo: str) -> DisciplinaRead:
        return await self.service.get_disciplina_by_codigo(session=session, codigo=codigo)

    async def list_disciplinas(
        self,
        session: AsyncSession,
        limit: int = 100,
        offset: int = 0,
    ) -> list[DisciplinaRead]:
        return await self.service.list_disciplinas(session=session, limit=limit, offset=offset)

    async def update_disciplina(self, session: AsyncSession, id_disciplina: int, data: DisciplinaUpdate) -> DisciplinaRead:
        return await self.service.update_disciplina(session=session, id_disciplina=id_disciplina, data=data)
