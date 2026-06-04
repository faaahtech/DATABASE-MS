from sqlmodel.ext.asyncio.session import AsyncSession

from dtos.matriz_curricular_dto import MatrizCurricularCreate, MatrizCurricularRead, MatrizCurricularUpdate
from services.matriz_curricular_service import MatrizCurricularService


class MatrizCurricularController:
    def __init__(self) -> None:
        self.service = MatrizCurricularService()

    async def create_matriz_curricular(
        self,
        session: AsyncSession,
        data: MatrizCurricularCreate,
    ) -> MatrizCurricularRead:
        return await self.service.create_matriz_curricular(session=session, data=data)

    async def list_matrizes_curriculares(
        self,
        session: AsyncSession,
        limit: int = 100,
        offset: int = 0,
    ) -> list[MatrizCurricularRead]:
        return await self.service.list_matrizes_curriculares(session=session, limit=limit, offset=offset)

    async def get_matriz_curricular_by_id(
        self,
        session: AsyncSession,
        id_matriz_curricular: int,
    ) -> MatrizCurricularRead:
        return await self.service.get_matriz_curricular_by_id(
            session=session,
            id_matriz_curricular=id_matriz_curricular,
        )

    async def list_matrizes_curriculares_by_curso_unidade(
        self,
        session: AsyncSession,
        id_curso_unidade: int,
        limit: int = 100,
        offset: int = 0,
    ) -> list[MatrizCurricularRead]:
        return await self.service.list_matrizes_curriculares_by_curso_unidade(
            session=session,
            id_curso_unidade=id_curso_unidade,
            limit=limit,
            offset=offset,
        )

    async def update_matriz_curricular(
        self,
        session: AsyncSession,
        id_matriz_curricular: int,
        data: MatrizCurricularUpdate,
    ) -> MatrizCurricularRead:
        return await self.service.update_matriz_curricular(
            session=session,
            id_matriz_curricular=id_matriz_curricular,
            data=data,
        )
