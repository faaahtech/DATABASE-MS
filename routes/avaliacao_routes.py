from fastapi import APIRouter, Depends, Query, status
from sqlmodel.ext.asyncio.session import AsyncSession

from controller.avaliacao_controller import AvaliacaoController
from dtos.avaliacao_dto import AvaliacaoCreate, AvaliacaoRead, AvaliacaoUpdate
from repositories.postgres_conn import get_session

router = APIRouter(prefix="/avaliacoes", tags=["Avaliações"])
controller = AvaliacaoController()


@router.post("", response_model=AvaliacaoRead, status_code=status.HTTP_201_CREATED)
async def create_avaliacao(
    data: AvaliacaoCreate,
    session: AsyncSession = Depends(get_session),
) -> AvaliacaoRead:
    return await controller.create_avaliacao(session=session, data=data)


@router.get("/oferta-disciplina/{id_oferta_disciplina}", response_model=list[AvaliacaoRead], status_code=status.HTTP_200_OK)
async def list_avaliacoes_by_oferta_disciplina(
    id_oferta_disciplina: int,
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    session: AsyncSession = Depends(get_session),
) -> list[AvaliacaoRead]:
    return await controller.list_avaliacoes_by_oferta_disciplina(
        session=session,
        id_oferta_disciplina=id_oferta_disciplina,
        limit=limit,
        offset=offset,
    )


@router.get("/{id_avaliacao}", response_model=AvaliacaoRead, status_code=status.HTTP_200_OK)
async def get_avaliacao_by_id(
    id_avaliacao: int,
    session: AsyncSession = Depends(get_session),
) -> AvaliacaoRead:
    return await controller.get_avaliacao_by_id(session=session, id_avaliacao=id_avaliacao)


@router.patch("/{id_avaliacao}", response_model=AvaliacaoRead, status_code=status.HTTP_200_OK)
async def update_avaliacao(
    id_avaliacao: int,
    data: AvaliacaoUpdate,
    session: AsyncSession = Depends(get_session),
) -> AvaliacaoRead:
    return await controller.update_avaliacao(session=session, id_avaliacao=id_avaliacao, data=data)
