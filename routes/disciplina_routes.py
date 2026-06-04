from fastapi import APIRouter, Depends, Query, status
from sqlmodel.ext.asyncio.session import AsyncSession

from controller.disciplina_controller import DisciplinaController
from dtos.disciplina_dto import DisciplinaCreate, DisciplinaRead, DisciplinaUpdate
from repositories.postgres_conn import get_session

router = APIRouter(prefix="/disciplinas", tags=["Disciplinas"])
controller = DisciplinaController()


@router.post("", response_model=DisciplinaRead, status_code=status.HTTP_201_CREATED)
async def create_disciplina(
    data: DisciplinaCreate,
    session: AsyncSession = Depends(get_session),
) -> DisciplinaRead:
    return await controller.create_disciplina(session=session, data=data)


@router.get("", response_model=list[DisciplinaRead], status_code=status.HTTP_200_OK)
async def list_disciplinas(
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    session: AsyncSession = Depends(get_session),
) -> list[DisciplinaRead]:
    return await controller.list_disciplinas(session=session, limit=limit, offset=offset)


@router.get("/codigo/{codigo}", response_model=DisciplinaRead, status_code=status.HTTP_200_OK)
async def get_disciplina_by_codigo(
    codigo: str,
    session: AsyncSession = Depends(get_session),
) -> DisciplinaRead:
    return await controller.get_disciplina_by_codigo(session=session, codigo=codigo)


@router.get("/{id_disciplina}", response_model=DisciplinaRead, status_code=status.HTTP_200_OK)
async def get_disciplina_by_id(
    id_disciplina: int,
    session: AsyncSession = Depends(get_session),
) -> DisciplinaRead:
    return await controller.get_disciplina_by_id(session=session, id_disciplina=id_disciplina)


@router.patch("/{id_disciplina}", response_model=DisciplinaRead, status_code=status.HTTP_200_OK)
async def update_disciplina(
    id_disciplina: int,
    data: DisciplinaUpdate,
    session: AsyncSession = Depends(get_session),
) -> DisciplinaRead:
    return await controller.update_disciplina(session=session, id_disciplina=id_disciplina, data=data)
