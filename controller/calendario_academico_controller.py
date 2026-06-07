from sqlmodel.ext.asyncio.session import AsyncSession

from dtos.calendario_academico_dto import (
    CalendarioAcademicoCreate,
    CalendarioAcademicoRead,
    CalendarioAcademicoUpdate,
)
from models.calendario_academico import TipoCalendarioAcademico
from services.calendario_academico_service import CalendarioAcademicoService


class CalendarioAcademicoController:
    def __init__(self) -> None:
        self.service = CalendarioAcademicoService()

    async def create_calendario_academico(
        self,
        session: AsyncSession,
        data: CalendarioAcademicoCreate,
    ) -> CalendarioAcademicoRead:
        return await self.service.create_calendario_academico(session=session, data=data)

    async def list_calendarios_academicos(
        self,
        session: AsyncSession,
        limit: int = 100,
        offset: int = 0,
    ) -> list[CalendarioAcademicoRead]:
        return await self.service.list_calendarios_academicos(session=session, limit=limit, offset=offset)

    async def get_calendario_academico_by_id(
        self,
        session: AsyncSession,
        id_calendario_academico: int,
    ) -> CalendarioAcademicoRead:
        return await self.service.get_calendario_academico_by_id(
            session=session,
            id_calendario_academico=id_calendario_academico,
        )

    async def list_calendarios_by_unidade(
        self,
        session: AsyncSession,
        id_unidade: int,
        limit: int = 100,
        offset: int = 0,
    ) -> list[CalendarioAcademicoRead]:
        return await self.service.list_calendarios_by_unidade(
            session=session,
            id_unidade=id_unidade,
            limit=limit,
            offset=offset,
        )

    async def list_calendarios_by_tipo(
        self,
        session: AsyncSession,
        tipo: TipoCalendarioAcademico,
        limit: int = 100,
        offset: int = 0,
    ) -> list[CalendarioAcademicoRead]:
        return await self.service.list_calendarios_by_tipo(
            session=session,
            tipo=tipo,
            limit=limit,
            offset=offset,
        )

    async def update_calendario_academico(
        self,
        session: AsyncSession,
        id_calendario_academico: int,
        data: CalendarioAcademicoUpdate,
    ) -> CalendarioAcademicoRead:
        return await self.service.update_calendario_academico(
            session=session,
            id_calendario_academico=id_calendario_academico,
            data=data,
        )

    async def gerar_pdf_by_unidade(
        self,
        session: AsyncSession,
        id_unidade: int,
    ) -> bytes:
        return await self.service.gerar_pdf_by_unidade(session=session, id_unidade=id_unidade)

    async def gerar_pdf_by_aluno(
        self,
        session: AsyncSession,
        id_aluno: int,
    ) -> bytes:
        return await self.service.gerar_pdf_by_aluno(session=session, id_aluno=id_aluno)
