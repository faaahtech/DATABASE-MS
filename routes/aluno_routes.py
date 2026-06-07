from fastapi import APIRouter, Depends, Query, status
from sqlmodel.ext.asyncio.session import AsyncSession

from controller.aluno_controller import AlunoController
from dtos.aluno_dto import AlunoCreate, AlunoListItem, AlunoRead
from dtos.llm_academico_dto import OpcoesTransferenciaHorarioRead
from repositories.postgres_conn import get_session

router = APIRouter(prefix="/alunos", tags=["Alunos"])
controller = AlunoController()


@router.post("", response_model=AlunoRead, status_code=status.HTTP_201_CREATED)
async def create_aluno(
    data: AlunoCreate,
    session: AsyncSession = Depends(get_session),
) -> AlunoRead:
    return await controller.create_aluno(session=session, data=data)


@router.get("", response_model=list[AlunoListItem], status_code=status.HTTP_200_OK)
async def list_alunos(
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    session: AsyncSession = Depends(get_session),
) -> list[AlunoListItem]:
    return await controller.list_alunos(session=session, limit=limit, offset=offset)


@router.get(
    "/{id_aluno}/opcoes-transferencia-horario",
    response_model=OpcoesTransferenciaHorarioRead,
    status_code=status.HTTP_200_OK,
)
async def listar_opcoes_transferencia_horario(
    id_aluno: int,
    session: AsyncSession = Depends(get_session),
) -> OpcoesTransferenciaHorarioRead:
    return await controller.listar_opcoes_transferencia_horario(
        session=session,
        id_aluno=id_aluno,
    )


@router.get("/ra/{ra}", response_model=AlunoRead, status_code=status.HTTP_200_OK)
async def get_aluno_by_ra(
    ra: str,
    session: AsyncSession = Depends(get_session),
) -> AlunoRead:
    return await controller.get_aluno_by_ra(session=session, ra=ra)


@router.get("/{id_aluno}", response_model=AlunoRead, status_code=status.HTTP_200_OK)
async def get_aluno_by_id(
    id_aluno: int,
    session: AsyncSession = Depends(get_session),
) -> AlunoRead:
    return await controller.get_aluno_by_id(session=session, id_aluno=id_aluno)
