from sqlmodel.ext.asyncio.session import AsyncSession

from dtos.aluno_dto import AlunoCreate, AlunoListItem, AlunoRead
from services.aluno_service import AlunoService


class AlunoController:
    def __init__(self) -> None:
        self.service = AlunoService()

    async def create_aluno(self, session: AsyncSession, data: AlunoCreate) -> AlunoRead:
        return await self.service.create_aluno(session=session, data=data)

    async def get_aluno_by_id(self, session: AsyncSession, id_aluno: int) -> AlunoRead:
        return await self.service.get_aluno_by_id(session=session, id_aluno=id_aluno)

    async def get_aluno_by_ra(self, session: AsyncSession, ra: str) -> AlunoRead:
        return await self.service.get_aluno_by_ra(session=session, ra=ra)

    async def list_alunos(
        self,
        session: AsyncSession,
        limit: int = 100,
        offset: int = 0,
    ) -> list[AlunoListItem]:
        return await self.service.list_alunos(session=session, limit=limit, offset=offset)
