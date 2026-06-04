from fastapi import APIRouter, Depends, Query, status
from sqlmodel.ext.asyncio.session import AsyncSession

from controller.nota_controller import NotaController
from dtos.nota_dto import NotaCreate, NotaPorAlunoRead, NotaRead, NotaUpdate
from repositories.postgres_conn import get_session

router = APIRouter(prefix="/notas", tags=["Notas"])
controller = NotaController()


@router.post("", response_model=NotaRead, status_code=status.HTTP_201_CREATED)
async def atribuir_nota(
    data: NotaCreate,
    session: AsyncSession = Depends(get_session),
) -> NotaRead:
    return await controller.atribuir_nota(session=session, data=data)


@router.patch("/{id_nota}", response_model=NotaRead, status_code=status.HTTP_200_OK)
async def update_nota(
    id_nota: int,
    data: NotaUpdate,
    session: AsyncSession = Depends(get_session),
) -> NotaRead:
    return await controller.update_nota(
        session=session,
        id_nota=id_nota,
        data=data,
    )


@router.get("/aluno/{id_aluno}", response_model=list[NotaPorAlunoRead], status_code=status.HTTP_200_OK)
async def consultar_notas_por_aluno(
    id_aluno: int,
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    session: AsyncSession = Depends(get_session),
) -> list[NotaPorAlunoRead]:
    return await controller.consultar_notas_por_aluno(
        session=session,
        id_aluno=id_aluno,
        limit=limit,
        offset=offset,
    )


@router.get(
    "/matricula-disciplina/{id_matricula_disciplina}",
    response_model=list[NotaRead],
    status_code=status.HTTP_200_OK,
)
async def consultar_notas_por_matricula_disciplina(
    id_matricula_disciplina: int,
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    session: AsyncSession = Depends(get_session),
) -> list[NotaRead]:
    return await controller.consultar_notas_por_matricula_disciplina(
        session=session,
        id_matricula_disciplina=id_matricula_disciplina,
        limit=limit,
        offset=offset,
    )
