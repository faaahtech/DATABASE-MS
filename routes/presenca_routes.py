from fastapi import APIRouter, Depends, Query, status
from sqlmodel.ext.asyncio.session import AsyncSession

from controller.presenca_controller import PresencaController
from dtos.presenca_dto import PresencaCreate, PresencaPorAlunoRead, PresencaRead, PresencaUpdate
from repositories.postgres_conn import get_session

router = APIRouter(prefix="/presencas", tags=["Presenças"])
controller = PresencaController()


@router.post("", response_model=PresencaRead, status_code=status.HTTP_201_CREATED)
async def atribuir_presenca(
    data: PresencaCreate,
    session: AsyncSession = Depends(get_session),
) -> PresencaRead:
    return await controller.atribuir_presenca(session=session, data=data)


@router.patch("/{id_presenca}", response_model=PresencaRead, status_code=status.HTTP_200_OK)
async def update_presenca(
    id_presenca: int,
    data: PresencaUpdate,
    session: AsyncSession = Depends(get_session),
) -> PresencaRead:
    return await controller.update_presenca(
        session=session,
        id_presenca=id_presenca,
        data=data,
    )


@router.get("/aluno/{id_aluno}", response_model=list[PresencaPorAlunoRead], status_code=status.HTTP_200_OK)
async def consultar_presencas_por_aluno(
    id_aluno: int,
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    session: AsyncSession = Depends(get_session),
) -> list[PresencaPorAlunoRead]:
    return await controller.consultar_presencas_por_aluno(
        session=session,
        id_aluno=id_aluno,
        limit=limit,
        offset=offset,
    )


@router.get(
    "/matricula-disciplina/{id_matricula_disciplina}",
    response_model=list[PresencaRead],
    status_code=status.HTTP_200_OK,
)
async def consultar_presencas_por_matricula_disciplina(
    id_matricula_disciplina: int,
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    session: AsyncSession = Depends(get_session),
) -> list[PresencaRead]:
    return await controller.consultar_presencas_por_matricula_disciplina(
        session=session,
        id_matricula_disciplina=id_matricula_disciplina,
        limit=limit,
        offset=offset,
    )
