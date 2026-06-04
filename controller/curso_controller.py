from sqlmodel.ext.asyncio.session import AsyncSession

from dtos.curso_dto import CursoCreate, CursoRead, CursoUpdate
from services.curso_service import CursoService


class CursoController:
    def __init__(self) -> None:
        self.service = CursoService()

    async def create_curso(self, session: AsyncSession, data: CursoCreate) -> CursoRead:
        return await self.service.create_curso(session=session, data=data)

    async def get_curso_by_id(self, session: AsyncSession, id_curso: int) -> CursoRead:
        return await self.service.get_curso_by_id(session=session, id_curso=id_curso)

    async def get_curso_by_sigla(self, session: AsyncSession, sigla: str) -> CursoRead:
        return await self.service.get_curso_by_sigla(session=session, sigla=sigla)

    async def list_cursos(
        self,
        session: AsyncSession,
        limit: int = 100,
        offset: int = 0,
    ) -> list[CursoRead]:
        return await self.service.list_cursos(session=session, limit=limit, offset=offset)

    async def update_curso(self, session: AsyncSession, id_curso: int, data: CursoUpdate) -> CursoRead:
        return await self.service.update_curso(session=session, id_curso=id_curso, data=data)
