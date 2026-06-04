from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlmodel.ext.asyncio.session import AsyncSession

from dtos.periodo_letivo_dto import PeriodoLetivoCreate, PeriodoLetivoRead, PeriodoLetivoUpdate
from models.periodo_letivo import PeriodoLetivo, StatusPeriodoLetivo
from repositories.periodo_letivo_repository import PeriodoLetivoRepository
from services.service_utils import validate_or_400
from utils.academic_validators import validate_periodo_letivo_datas, validate_semestre_letivo


class PeriodoLetivoService:
    def __init__(self) -> None:
        self.periodo_repository = PeriodoLetivoRepository()

    async def create_periodo_letivo(
        self,
        session: AsyncSession,
        data: PeriodoLetivoCreate,
    ) -> PeriodoLetivoRead:
        validate_or_400(validate_semestre_letivo, data.semestre)
        validate_or_400(validate_periodo_letivo_datas, data.data_inicio, data.data_fim)

        periodo = PeriodoLetivo(**data.model_dump())
        try:
            async with session.begin():
                existente = await self.periodo_repository.get_by_ano_semestre(
                    session=session,
                    ano=data.ano,
                    semestre=data.semestre,
                )
                if existente is not None:
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail="Já existe período letivo para este ano e semestre.",
                    )
                if data.status == StatusPeriodoLetivo.ATIVO:
                    await self._encerrar_periodos_ativos(session)
                periodo = await self.periodo_repository.create(session, periodo)
        except IntegrityError as exc:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Já existe período letivo cadastrado para este ano e semestre.",
            ) from exc
        return self._to_read(periodo)

    async def get_periodo_letivo_by_id(
        self,
        session: AsyncSession,
        id_periodo_letivo: int,
    ) -> PeriodoLetivoRead:
        periodo = await self.periodo_repository.get_by_id(session, id_periodo_letivo)
        if periodo is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Período letivo não encontrado.")
        return self._to_read(periodo)

    async def get_periodo_letivo_ativo(self, session: AsyncSession) -> PeriodoLetivoRead:
        periodo = await self.periodo_repository.get_ativo(session)
        if periodo is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Nenhum período letivo ativo encontrado.",
            )
        return self._to_read(periodo)

    async def list_periodos_letivos(
        self,
        session: AsyncSession,
        limit: int = 100,
        offset: int = 0,
    ) -> list[PeriodoLetivoRead]:
        periodos = await self.periodo_repository.list(session, limit=limit, offset=offset)
        return [self._to_read(periodo) for periodo in periodos]

    async def update_periodo_letivo(
        self,
        session: AsyncSession,
        id_periodo_letivo: int,
        data: PeriodoLetivoUpdate,
    ) -> PeriodoLetivoRead:
        async with session.begin():
            periodo = await self.periodo_repository.get_by_id(session, id_periodo_letivo)
            if periodo is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Período letivo não encontrado.")
            update_data = data.model_dump(exclude_unset=True)

            ano = update_data.get("ano", periodo.ano)
            semestre = update_data.get("semestre", periodo.semestre)
            data_inicio = update_data.get("data_inicio", periodo.data_inicio)
            data_fim = update_data.get("data_fim", periodo.data_fim)
            status_novo = update_data.get("status", periodo.status)

            validate_or_400(validate_semestre_letivo, semestre)
            validate_or_400(validate_periodo_letivo_datas, data_inicio, data_fim)

            if ano != periodo.ano or semestre != periodo.semestre:
                existente = await self.periodo_repository.get_by_ano_semestre(session, ano, semestre)
                if existente is not None and existente.id != id_periodo_letivo:
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail="Já existe outro período letivo para este ano e semestre.",
                    )

            if status_novo == StatusPeriodoLetivo.ATIVO:
                await self._encerrar_periodos_ativos(session, ignore_id=id_periodo_letivo)

            for field, value in update_data.items():
                setattr(periodo, field, value)
            periodo = await self.periodo_repository.update(session, periodo)
        return self._to_read(periodo)

    async def ativar_periodo_letivo(
        self,
        session: AsyncSession,
        id_periodo_letivo: int,
    ) -> PeriodoLetivoRead:
        return await self.update_periodo_letivo(
            session=session,
            id_periodo_letivo=id_periodo_letivo,
            data=PeriodoLetivoUpdate(status=StatusPeriodoLetivo.ATIVO),
        )

    async def encerrar_periodo_letivo(
        self,
        session: AsyncSession,
        id_periodo_letivo: int,
    ) -> PeriodoLetivoRead:
        return await self.update_periodo_letivo(
            session=session,
            id_periodo_letivo=id_periodo_letivo,
            data=PeriodoLetivoUpdate(status=StatusPeriodoLetivo.ENCERRADO),
        )

    async def _encerrar_periodos_ativos(
        self,
        session: AsyncSession,
        ignore_id: int | None = None,
    ) -> None:
        ativos = await self.periodo_repository.list_ativos(session)
        for ativo in ativos:
            if ignore_id is not None and ativo.id == ignore_id:
                continue
            ativo.status = StatusPeriodoLetivo.ENCERRADO
            await self.periodo_repository.update(session, ativo)

    def _to_read(self, periodo: PeriodoLetivo) -> PeriodoLetivoRead:
        return PeriodoLetivoRead(
            id=periodo.id,
            ano=periodo.ano,
            semestre=periodo.semestre,
            data_inicio=periodo.data_inicio,
            data_fim=periodo.data_fim,
            status=periodo.status,
        )
