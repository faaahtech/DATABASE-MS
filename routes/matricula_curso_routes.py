from fastapi import APIRouter, Depends, Query, status
from sqlmodel.ext.asyncio.session import AsyncSession

from controller.matricula_curso_controller import MatriculaCursoController
from dtos.matricula_curso_dto import MatriculaCursoCreate, MatriculaCursoRead, MatriculaCursoUpdateStatus
from repositories.postgres_conn import get_session

router = APIRouter(prefix="/matriculas-curso", tags=["Matrículas de Curso"])
controller = MatriculaCursoController()


@router.post("", response_model=MatriculaCursoRead, status_code=status.HTTP_201_CREATED)
async def create_matricula_curso(
    data: MatriculaCursoCreate,
    session: AsyncSession = Depends(get_session),
) -> MatriculaCursoRead:
    return await controller.create_matricula_curso(session=session, data=data)


@router.get("/aluno/{id_aluno}", response_model=list[MatriculaCursoRead], status_code=status.HTTP_200_OK)
async def list_matriculas_curso_by_aluno(
    id_aluno: int,
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    session: AsyncSession = Depends(get_session),
) -> list[MatriculaCursoRead]:
    return await controller.list_matriculas_curso_by_aluno(
        session=session,
        id_aluno=id_aluno,
        limit=limit,
        offset=offset,
    )


@router.get("/ra/{ra}", response_model=MatriculaCursoRead, status_code=status.HTTP_200_OK)
async def get_matricula_curso_by_ra(
    ra: str,
    session: AsyncSession = Depends(get_session),
) -> MatriculaCursoRead:
    return await controller.get_matricula_curso_by_ra(session=session, ra=ra)


@router.get("/{id_matricula_curso}", response_model=MatriculaCursoRead, status_code=status.HTTP_200_OK)
async def get_matricula_curso_by_id(
    id_matricula_curso: int,
    session: AsyncSession = Depends(get_session),
) -> MatriculaCursoRead:
    return await controller.get_matricula_curso_by_id(
        session=session,
        id_matricula_curso=id_matricula_curso,
    )


@router.patch("/{id_matricula_curso}/status", response_model=MatriculaCursoRead, status_code=status.HTTP_200_OK)
async def update_matricula_curso_status(
    id_matricula_curso: int,
    data: MatriculaCursoUpdateStatus,
    session: AsyncSession = Depends(get_session),
) -> MatriculaCursoRead:
    return await controller.update_matricula_curso_status(
        session=session,
        id_matricula_curso=id_matricula_curso,
        data=data,
    )
