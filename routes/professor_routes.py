from fastapi import APIRouter, Depends, Query, status
from sqlmodel.ext.asyncio.session import AsyncSession

from controller.professor_controller import ProfessorController
from dtos.professor_dto import ProfessorCreate, ProfessorRead
from repositories.postgres_conn import get_session

router = APIRouter(prefix="/professores", tags=["Professores"])
controller = ProfessorController()


@router.post("", response_model=ProfessorRead, status_code=status.HTTP_201_CREATED)
async def create_professor(
    data: ProfessorCreate,
    session: AsyncSession = Depends(get_session),
) -> ProfessorRead:
    return await controller.create_professor(session=session, data=data)


@router.get("", response_model=list[ProfessorRead], status_code=status.HTTP_200_OK)
async def list_professores(
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    session: AsyncSession = Depends(get_session),
) -> list[ProfessorRead]:
    return await controller.list_professores(session=session, limit=limit, offset=offset)


@router.get("/{id_professor}", response_model=ProfessorRead, status_code=status.HTTP_200_OK)
async def get_professor_by_id(
    id_professor: int,
    session: AsyncSession = Depends(get_session),
) -> ProfessorRead:
    return await controller.get_professor_by_id(session=session, id_professor=id_professor)
