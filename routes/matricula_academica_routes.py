from fastapi import APIRouter, Depends, status
from sqlmodel.ext.asyncio.session import AsyncSession

from controller.matricula_curso_controller import MatriculaCursoController
from dtos.matricula_curso_dto import MatriculaCursoRead, TransferirHorarioRequest
from repositories.postgres_conn import get_session

router = APIRouter(prefix="/matriculas", tags=["Matrículas - Fluxos Acadêmicos"])
controller = MatriculaCursoController()


@router.post(
    "/{id_matricula_curso}/transferir-horario",
    response_model=MatriculaCursoRead,
    status_code=status.HTTP_200_OK,
)
async def transferir_horario(
    id_matricula_curso: int,
    data: TransferirHorarioRequest,
    session: AsyncSession = Depends(get_session),
) -> MatriculaCursoRead:
    return await controller.transferir_horario(
        session=session,
        id_matricula_curso=id_matricula_curso,
        data=data,
    )


@router.post(
    "/{id_matricula_curso}/trancar",
    response_model=MatriculaCursoRead,
    status_code=status.HTTP_200_OK,
)
async def trancar_matricula(
    id_matricula_curso: int,
    session: AsyncSession = Depends(get_session),
) -> MatriculaCursoRead:
    return await controller.trancar_matricula(
        session=session,
        id_matricula_curso=id_matricula_curso,
    )


@router.post(
    "/{id_matricula_curso}/ativar",
    response_model=MatriculaCursoRead,
    status_code=status.HTTP_200_OK,
)
async def ativar_matricula(
    id_matricula_curso: int,
    session: AsyncSession = Depends(get_session),
) -> MatriculaCursoRead:
    return await controller.ativar_matricula(
        session=session,
        id_matricula_curso=id_matricula_curso,
    )
