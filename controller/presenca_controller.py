from sqlmodel.ext.asyncio.session import AsyncSession

from dtos.presenca_dto import PresencaCreate, PresencaPorAlunoRead, PresencaRead, PresencaUpdate
from services.presenca_service import PresencaService


class PresencaController:
    def __init__(self) -> None:
        self.service = PresencaService()

    async def atribuir_presenca(
        self,
        session: AsyncSession,
        data: PresencaCreate,
    ) -> PresencaRead:
        return await self.service.atribuir_presenca(session=session, data=data)

    async def update_presenca(
        self,
        session: AsyncSession,
        id_presenca: int,
        data: PresencaUpdate,
    ) -> PresencaRead:
        return await self.service.update_presenca(
            session=session,
            id_presenca=id_presenca,
            data=data,
        )

    async def consultar_presencas_por_aluno(
        self,
        session: AsyncSession,
        id_aluno: int,
        limit: int = 100,
        offset: int = 0,
    ) -> list[PresencaPorAlunoRead]:
        return await self.service.consultar_presencas_por_aluno(
            session=session,
            id_aluno=id_aluno,
            limit=limit,
            offset=offset,
        )

    async def consultar_presencas_por_matricula_disciplina(
        self,
        session: AsyncSession,
        id_matricula_disciplina: int,
        limit: int = 100,
        offset: int = 0,
    ) -> list[PresencaRead]:
        return await self.service.consultar_presencas_por_matricula_disciplina(
            session=session,
            id_matricula_disciplina=id_matricula_disciplina,
            limit=limit,
            offset=offset,
        )
