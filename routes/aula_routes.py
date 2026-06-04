from fastapi import APIRouter, Depends, Query, status
from sqlmodel.ext.asyncio.session import AsyncSession

from controller.aula_controller import AulaController
from dtos.aula_dto import AulaCreate, AulaRead, AulaUpdate
from repositories.postgres_conn import get_session

router = APIRouter(prefix="/aulas", tags=["Aulas"])
controller = AulaController()


@router.post("", response_model=AulaRead, status_code=status.HTTP_201_CREATED)
async def create_aula(
    data: AulaCreate,
    session: AsyncSession = Depends(get_session),
) -> AulaRead:
    return await controller.create_aula(session=session, data=data)


@router.get("/oferta-disciplina/{id_oferta_disciplina}", response_model=list[AulaRead], status_code=status.HTTP_200_OK)
async def list_aulas_by_oferta_disciplina(
    id_oferta_disciplina: int,
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    session: AsyncSession = Depends(get_session),
) -> list[AulaRead]:
    return await controller.list_aulas_by_oferta_disciplina(
        session=session,
        id_oferta_disciplina=id_oferta_disciplina,
        limit=limit,
        offset=offset,
    )


@router.get("/{id_aula}", response_model=AulaRead, status_code=status.HTTP_200_OK)
async def get_aula_by_id(
    id_aula: int,
    session: AsyncSession = Depends(get_session),
) -> AulaRead:
    return await controller.get_aula_by_id(session=session, id_aula=id_aula)


@router.patch("/{id_aula}", response_model=AulaRead, status_code=status.HTTP_200_OK)
async def update_aula(
    id_aula: int,
    data: AulaUpdate,
    session: AsyncSession = Depends(get_session),
) -> AulaRead:
    return await controller.update_aula(session=session, id_aula=id_aula, data=data)
