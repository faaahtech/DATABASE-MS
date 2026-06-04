from fastapi import APIRouter, Depends, Query, status
from sqlmodel.ext.asyncio.session import AsyncSession

from controller.periodo_letivo_controller import PeriodoLetivoController
from dtos.periodo_letivo_dto import PeriodoLetivoCreate, PeriodoLetivoRead, PeriodoLetivoUpdate
from repositories.postgres_conn import get_session

router = APIRouter(prefix="/periodos-letivos", tags=["Períodos Letivos"])
controller = PeriodoLetivoController()


@router.post("", response_model=PeriodoLetivoRead, status_code=status.HTTP_201_CREATED)
async def create_periodo_letivo(
    data: PeriodoLetivoCreate,
    session: AsyncSession = Depends(get_session),
) -> PeriodoLetivoRead:
    return await controller.create_periodo_letivo(session=session, data=data)


@router.get("", response_model=list[PeriodoLetivoRead], status_code=status.HTTP_200_OK)
async def list_periodos_letivos(
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    session: AsyncSession = Depends(get_session),
) -> list[PeriodoLetivoRead]:
    return await controller.list_periodos_letivos(session=session, limit=limit, offset=offset)


@router.get("/ativo", response_model=PeriodoLetivoRead, status_code=status.HTTP_200_OK)
async def get_periodo_letivo_ativo(
    session: AsyncSession = Depends(get_session),
) -> PeriodoLetivoRead:
    return await controller.get_periodo_letivo_ativo(session=session)


@router.get("/{id_periodo_letivo}", response_model=PeriodoLetivoRead, status_code=status.HTTP_200_OK)
async def get_periodo_letivo_by_id(
    id_periodo_letivo: int,
    session: AsyncSession = Depends(get_session),
) -> PeriodoLetivoRead:
    return await controller.get_periodo_letivo_by_id(
        session=session,
        id_periodo_letivo=id_periodo_letivo,
    )


@router.patch("/{id_periodo_letivo}", response_model=PeriodoLetivoRead, status_code=status.HTTP_200_OK)
async def update_periodo_letivo(
    id_periodo_letivo: int,
    data: PeriodoLetivoUpdate,
    session: AsyncSession = Depends(get_session),
) -> PeriodoLetivoRead:
    return await controller.update_periodo_letivo(
        session=session,
        id_periodo_letivo=id_periodo_letivo,
        data=data,
    )


@router.patch("/{id_periodo_letivo}/ativar", response_model=PeriodoLetivoRead, status_code=status.HTTP_200_OK)
async def ativar_periodo_letivo(
    id_periodo_letivo: int,
    session: AsyncSession = Depends(get_session),
) -> PeriodoLetivoRead:
    return await controller.ativar_periodo_letivo(
        session=session,
        id_periodo_letivo=id_periodo_letivo,
    )


@router.patch("/{id_periodo_letivo}/encerrar", response_model=PeriodoLetivoRead, status_code=status.HTTP_200_OK)
async def encerrar_periodo_letivo(
    id_periodo_letivo: int,
    session: AsyncSession = Depends(get_session),
) -> PeriodoLetivoRead:
    return await controller.encerrar_periodo_letivo(
        session=session,
        id_periodo_letivo=id_periodo_letivo,
    )
