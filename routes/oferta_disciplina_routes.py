from fastapi import APIRouter, Depends, Query, status
from sqlmodel.ext.asyncio.session import AsyncSession

from controller.oferta_disciplina_controller import OfertaDisciplinaController
from dtos.oferta_disciplina_dto import OfertaDisciplinaCreate, OfertaDisciplinaRead, OfertaDisciplinaUpdate
from repositories.postgres_conn import get_session

router = APIRouter(prefix="/ofertas-disciplinas", tags=["Ofertas de Disciplinas"])
controller = OfertaDisciplinaController()


@router.post("", response_model=OfertaDisciplinaRead, status_code=status.HTTP_201_CREATED)
async def create_oferta_disciplina(
    data: OfertaDisciplinaCreate,
    session: AsyncSession = Depends(get_session),
) -> OfertaDisciplinaRead:
    return await controller.create_oferta_disciplina(session=session, data=data)


@router.get(
    "/periodo-letivo/{id_periodo_letivo}",
    response_model=list[OfertaDisciplinaRead],
    status_code=status.HTTP_200_OK,
)
async def list_ofertas_by_periodo_letivo(
    id_periodo_letivo: int,
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    session: AsyncSession = Depends(get_session),
) -> list[OfertaDisciplinaRead]:
    return await controller.list_ofertas_by_periodo_letivo(
        session=session,
        id_periodo_letivo=id_periodo_letivo,
        limit=limit,
        offset=offset,
    )


@router.get(
    "/curso-unidade/{id_curso_unidade}",
    response_model=list[OfertaDisciplinaRead],
    status_code=status.HTTP_200_OK,
)
async def list_ofertas_by_curso_unidade(
    id_curso_unidade: int,
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    session: AsyncSession = Depends(get_session),
) -> list[OfertaDisciplinaRead]:
    return await controller.list_ofertas_by_curso_unidade(
        session=session,
        id_curso_unidade=id_curso_unidade,
        limit=limit,
        offset=offset,
    )


@router.get(
    "/disciplina/{id_disciplina}",
    response_model=list[OfertaDisciplinaRead],
    status_code=status.HTTP_200_OK,
)
async def list_ofertas_by_disciplina(
    id_disciplina: int,
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    session: AsyncSession = Depends(get_session),
) -> list[OfertaDisciplinaRead]:
    return await controller.list_ofertas_by_disciplina(
        session=session,
        id_disciplina=id_disciplina,
        limit=limit,
        offset=offset,
    )


@router.get("/{id_oferta_disciplina}", response_model=OfertaDisciplinaRead, status_code=status.HTTP_200_OK)
async def get_oferta_disciplina_by_id(
    id_oferta_disciplina: int,
    session: AsyncSession = Depends(get_session),
) -> OfertaDisciplinaRead:
    return await controller.get_oferta_disciplina_by_id(
        session=session,
        id_oferta_disciplina=id_oferta_disciplina,
    )


@router.patch("/{id_oferta_disciplina}", response_model=OfertaDisciplinaRead, status_code=status.HTTP_200_OK)
async def update_oferta_disciplina(
    id_oferta_disciplina: int,
    data: OfertaDisciplinaUpdate,
    session: AsyncSession = Depends(get_session),
) -> OfertaDisciplinaRead:
    return await controller.update_oferta_disciplina(
        session=session,
        id_oferta_disciplina=id_oferta_disciplina,
        data=data,
    )
