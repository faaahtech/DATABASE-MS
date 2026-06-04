from fastapi import HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession

from dtos.calendario_academico_dto import (
    CalendarioAcademicoCreate,
    CalendarioAcademicoRead,
    CalendarioAcademicoUpdate,
)
from models.calendario_academico import CalendarioAcademico, TipoCalendarioAcademico
from repositories.calendario_academico_repository import CalendarioAcademicoRepository
from repositories.unidade_repository import UnidadeRepository


class CalendarioAcademicoService:
    def __init__(self) -> None:
        self.calendario_repository = CalendarioAcademicoRepository()
        self.unidade_repository = UnidadeRepository()

    async def create_calendario_academico(
        self,
        session: AsyncSession,
        data: CalendarioAcademicoCreate,
    ) -> CalendarioAcademicoRead:
        self._validate_payload(data)
        async with session.begin():
            unidade = await self.unidade_repository.get_by_id(session, data.id_unidade)
            if unidade is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Unidade não encontrada.")
            calendario = CalendarioAcademico(**data.model_dump())
            calendario = await self.calendario_repository.create(session, calendario)
        return self._to_read(calendario)

    async def list_calendarios_academicos(
        self,
        session: AsyncSession,
        limit: int = 100,
        offset: int = 0,
    ) -> list[CalendarioAcademicoRead]:
        calendarios = await self.calendario_repository.list(session, limit=limit, offset=offset)
        return [self._to_read(calendario) for calendario in calendarios]

    async def get_calendario_academico_by_id(
        self,
        session: AsyncSession,
        id_calendario_academico: int,
    ) -> CalendarioAcademicoRead:
        calendario = await self.calendario_repository.get_by_id(session, id_calendario_academico)
        if calendario is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Calendário acadêmico não encontrado.")
        return self._to_read(calendario)

    async def list_calendarios_by_unidade(
        self,
        session: AsyncSession,
        id_unidade: int,
        limit: int = 100,
        offset: int = 0,
    ) -> list[CalendarioAcademicoRead]:
        unidade = await self.unidade_repository.get_by_id(session, id_unidade)
        if unidade is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Unidade não encontrada.")
        calendarios = await self.calendario_repository.list_by_unidade(
            session=session,
            id_unidade=id_unidade,
            limit=limit,
            offset=offset,
        )
        return [self._to_read(calendario) for calendario in calendarios]

    async def list_calendarios_by_tipo(
        self,
        session: AsyncSession,
        tipo: TipoCalendarioAcademico,
        limit: int = 100,
        offset: int = 0,
    ) -> list[CalendarioAcademicoRead]:
        calendarios = await self.calendario_repository.list_by_tipo(
            session=session,
            tipo=tipo,
            limit=limit,
            offset=offset,
        )
        return [self._to_read(calendario) for calendario in calendarios]

    async def update_calendario_academico(
        self,
        session: AsyncSession,
        id_calendario_academico: int,
        data: CalendarioAcademicoUpdate,
    ) -> CalendarioAcademicoRead:
        async with session.begin():
            calendario = await self.calendario_repository.get_by_id(session, id_calendario_academico)
            if calendario is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Calendário acadêmico não encontrado.")

            update_data = data.model_dump(exclude_unset=True)
            if "id_unidade" in update_data:
                unidade = await self.unidade_repository.get_by_id(session, update_data["id_unidade"])
                if unidade is None:
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Unidade não encontrada.")

            merged_data = {
                "id_unidade": update_data.get("id_unidade", calendario.id_unidade),
                "titulo": update_data.get("titulo", calendario.titulo),
                "descricao": update_data.get("descricao", calendario.descricao),
                "tipo": update_data.get("tipo", calendario.tipo),
                "data_inicio": update_data.get("data_inicio", calendario.data_inicio),
                "data_fim": update_data.get("data_fim", calendario.data_fim),
                "periodo": update_data.get("periodo", calendario.periodo),
                "status": update_data.get("status", calendario.status),
            }
            self._validate_payload(CalendarioAcademicoCreate(**merged_data))

            for field, value in update_data.items():
                setattr(calendario, field, value)
            calendario = await self.calendario_repository.update(session, calendario)
        return self._to_read(calendario)

    def _validate_payload(self, data: CalendarioAcademicoCreate) -> None:
        if not data.titulo.strip():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Título do calendário é obrigatório.")
        if data.periodo is not None and data.periodo not in (1, 2):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Período deve ser 1, 2 ou nulo.")
        if data.data_fim is not None and data.data_fim < data.data_inicio:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Data final do calendário deve ser maior ou igual à data inicial.",
            )

    def _to_read(self, calendario: CalendarioAcademico) -> CalendarioAcademicoRead:
        return CalendarioAcademicoRead(
            id=calendario.id,
            id_unidade=calendario.id_unidade,
            titulo=calendario.titulo,
            descricao=calendario.descricao,
            tipo=calendario.tipo,
            data_inicio=calendario.data_inicio,
            data_fim=calendario.data_fim,
            periodo=calendario.periodo,
            status=calendario.status,
        )
