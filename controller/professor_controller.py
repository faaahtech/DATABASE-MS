from sqlmodel.ext.asyncio.session import AsyncSession

from dtos.professor_dto import ProfessorCreate, ProfessorRead
from services.professor_service import ProfessorService


class ProfessorController:
    def __init__(self) -> None:
        self.service = ProfessorService()

    async def create_professor(self, session: AsyncSession, data: ProfessorCreate) -> ProfessorRead:
        return await self.service.create_professor(session=session, data=data)

    async def get_professor_by_id(self, session: AsyncSession, id_professor: int) -> ProfessorRead:
        return await self.service.get_professor_by_id(session=session, id_professor=id_professor)

    async def list_professores(
        self,
        session: AsyncSession,
        limit: int = 100,
        offset: int = 0,
    ) -> list[ProfessorRead]:
        return await self.service.list_professores(session=session, limit=limit, offset=offset)
