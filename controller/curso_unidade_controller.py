from sqlmodel.ext.asyncio.session import AsyncSession

from dtos.curso_unidade_dto import CursoUnidadeCreate, CursoUnidadeListItem, CursoUnidadeRead
from services.curso_unidade_service import CursoUnidadeService


class CursoUnidadeController:
    def __init__(self) -> None:
        self.service = CursoUnidadeService()

    async def create_curso_unidade(
        self,
        session: AsyncSession,
        data: CursoUnidadeCreate,
    ) -> CursoUnidadeRead:
        return await self.service.create_curso_unidade(session=session, data=data)

    async def get_curso_unidade_by_id(
        self,
        session: AsyncSession,
        id_curso_unidade: int,
    ) -> CursoUnidadeRead:
        return await self.service.get_curso_unidade_by_id(
            session=session,
            id_curso_unidade=id_curso_unidade,
        )

    async def list_curso_unidade(
        self,
        session: AsyncSession,
        limit: int = 100,
        offset: int = 0,
    ) -> list[CursoUnidadeListItem]:
        return await self.service.list_curso_unidade(session=session, limit=limit, offset=offset)
