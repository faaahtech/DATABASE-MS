from sqlmodel.ext.asyncio.session import AsyncSession

from dtos.llm_academico_dto import TransferirHorarioRequest
from dtos.matricula_curso_dto import MatriculaCursoCreate, MatriculaCursoRead, MatriculaCursoUpdateStatus
from services.matricula_curso_service import MatriculaCursoService


class MatriculaCursoController:
    def __init__(self) -> None:
        self.service = MatriculaCursoService()

    async def create_matricula_curso(
        self,
        session: AsyncSession,
        data: MatriculaCursoCreate,
    ) -> MatriculaCursoRead:
        return await self.service.create_matricula_curso(session=session, data=data)

    async def get_matricula_curso_by_id(
        self,
        session: AsyncSession,
        id_matricula_curso: int,
    ) -> MatriculaCursoRead:
        return await self.service.get_matricula_curso_by_id(
            session=session,
            id_matricula_curso=id_matricula_curso,
        )

    async def get_matricula_curso_by_ra(self, session: AsyncSession, ra: str) -> MatriculaCursoRead:
        return await self.service.get_matricula_curso_by_ra(session=session, ra=ra)

    async def list_matriculas_curso_by_aluno(
        self,
        session: AsyncSession,
        id_aluno: int,
        limit: int = 100,
        offset: int = 0,
    ) -> list[MatriculaCursoRead]:
        return await self.service.list_matriculas_curso_by_aluno(
            session=session,
            id_aluno=id_aluno,
            limit=limit,
            offset=offset,
        )

    async def update_matricula_curso_status(
        self,
        session: AsyncSession,
        id_matricula_curso: int,
        data: MatriculaCursoUpdateStatus,
    ) -> MatriculaCursoRead:
        return await self.service.update_matricula_curso_status(
            session=session,
            id_matricula_curso=id_matricula_curso,
            data=data,
        )

    async def transferir_horario(
        self,
        session: AsyncSession,
        id_matricula_curso: int,
        data: TransferirHorarioRequest,
    ) -> MatriculaCursoRead:
        return await self.service.transferir_horario(
            session=session,
            id_matricula_curso=id_matricula_curso,
            data=data,
        )

    async def trancar_matricula(
        self,
        session: AsyncSession,
        id_matricula_curso: int,
    ) -> MatriculaCursoRead:
        return await self.service.trancar_matricula(
            session=session,
            id_matricula_curso=id_matricula_curso,
        )

    async def ativar_matricula(
        self,
        session: AsyncSession,
        id_matricula_curso: int,
    ) -> MatriculaCursoRead:
        return await self.service.ativar_matricula(
            session=session,
            id_matricula_curso=id_matricula_curso,
        )
