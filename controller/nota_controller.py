from sqlmodel.ext.asyncio.session import AsyncSession

from dtos.nota_dto import NotaCreate, NotaPorAlunoRead, NotaRead, NotaUpdate
from services.nota_service import NotaService


class NotaController:
    def __init__(self) -> None:
        self.service = NotaService()

    async def atribuir_nota(self, session: AsyncSession, data: NotaCreate) -> NotaRead:
        return await self.service.atribuir_nota(session=session, data=data)

    async def update_nota(
        self,
        session: AsyncSession,
        id_nota: int,
        data: NotaUpdate,
    ) -> NotaRead:
        return await self.service.update_nota(
            session=session,
            id_nota=id_nota,
            data=data,
        )

    async def consultar_notas_por_aluno(
        self,
        session: AsyncSession,
        id_aluno: int,
        limit: int = 100,
        offset: int = 0,
    ) -> list[NotaPorAlunoRead]:
        return await self.service.consultar_notas_por_aluno(
            session=session,
            id_aluno=id_aluno,
            limit=limit,
            offset=offset,
        )

    async def consultar_notas_por_matricula_disciplina(
        self,
        session: AsyncSession,
        id_matricula_disciplina: int,
        limit: int = 100,
        offset: int = 0,
    ) -> list[NotaRead]:
        return await self.service.consultar_notas_por_matricula_disciplina(
            session=session,
            id_matricula_disciplina=id_matricula_disciplina,
            limit=limit,
            offset=offset,
        )
