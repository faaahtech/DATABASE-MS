from sqlmodel.ext.asyncio.session import AsyncSession

from dtos.matricula_disciplina_dto import (
    MatriculaDisciplinaCreate,
    MatriculaDisciplinaRead,
    MatriculaDisciplinaUpdateStatus,
)
from services.matricula_disciplina_service import MatriculaDisciplinaService


class MatriculaDisciplinaController:
    def __init__(self) -> None:
        self.service = MatriculaDisciplinaService()

    async def create_matricula_disciplina(
        self,
        session: AsyncSession,
        data: MatriculaDisciplinaCreate,
    ) -> MatriculaDisciplinaRead:
        return await self.service.create_matricula_disciplina(session=session, data=data)

    async def get_matricula_disciplina_by_id(
        self,
        session: AsyncSession,
        id_matricula_disciplina: int,
    ) -> MatriculaDisciplinaRead:
        return await self.service.get_matricula_disciplina_by_id(
            session=session,
            id_matricula_disciplina=id_matricula_disciplina,
        )

    async def list_matriculas_disciplina_by_matricula_curso(
        self,
        session: AsyncSession,
        id_matricula_curso: int,
        limit: int = 100,
        offset: int = 0,
    ) -> list[MatriculaDisciplinaRead]:
        return await self.service.list_matriculas_disciplina_by_matricula_curso(
            session=session,
            id_matricula_curso=id_matricula_curso,
            limit=limit,
            offset=offset,
        )

    async def list_matriculas_disciplina_by_oferta_disciplina(
        self,
        session: AsyncSession,
        id_oferta_disciplina: int,
        limit: int = 100,
        offset: int = 0,
    ) -> list[MatriculaDisciplinaRead]:
        return await self.service.list_matriculas_disciplina_by_oferta_disciplina(
            session=session,
            id_oferta_disciplina=id_oferta_disciplina,
            limit=limit,
            offset=offset,
        )

    async def update_matricula_disciplina_status(
        self,
        session: AsyncSession,
        id_matricula_disciplina: int,
        data: MatriculaDisciplinaUpdateStatus,
    ) -> MatriculaDisciplinaRead:
        return await self.service.update_matricula_disciplina_status(
            session=session,
            id_matricula_disciplina=id_matricula_disciplina,
            data=data,
        )
