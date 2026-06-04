from fastapi import APIRouter, Depends, Query, status
from sqlmodel.ext.asyncio.session import AsyncSession

from controller.matriz_curricular_controller import MatrizCurricularController
from dtos.matriz_curricular_dto import MatrizCurricularCreate, MatrizCurricularRead, MatrizCurricularUpdate
from repositories.postgres_conn import get_session

router = APIRouter(prefix="/matrizes-curriculares", tags=["Matrizes Curriculares"])
controller = MatrizCurricularController()


@router.post("", response_model=MatrizCurricularRead, status_code=status.HTTP_201_CREATED)
async def create_matriz_curricular(
    data: MatrizCurricularCreate,
    session: AsyncSession = Depends(get_session),
) -> MatrizCurricularRead:
    return await controller.create_matriz_curricular(session=session, data=data)


@router.get("", response_model=list[MatrizCurricularRead], status_code=status.HTTP_200_OK)
async def list_matrizes_curriculares(
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    session: AsyncSession = Depends(get_session),
) -> list[MatrizCurricularRead]:
    return await controller.list_matrizes_curriculares(session=session, limit=limit, offset=offset)


@router.get(
    "/curso-unidade/{id_curso_unidade}",
    response_model=list[MatrizCurricularRead],
    status_code=status.HTTP_200_OK,
)
async def list_matrizes_curriculares_by_curso_unidade(
    id_curso_unidade: int,
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    session: AsyncSession = Depends(get_session),
) -> list[MatrizCurricularRead]:
    return await controller.list_matrizes_curriculares_by_curso_unidade(
        session=session,
        id_curso_unidade=id_curso_unidade,
        limit=limit,
        offset=offset,
    )


@router.get("/{id_matriz_curricular}", response_model=MatrizCurricularRead, status_code=status.HTTP_200_OK)
async def get_matriz_curricular_by_id(
    id_matriz_curricular: int,
    session: AsyncSession = Depends(get_session),
) -> MatrizCurricularRead:
    return await controller.get_matriz_curricular_by_id(
        session=session,
        id_matriz_curricular=id_matriz_curricular,
    )


@router.patch("/{id_matriz_curricular}", response_model=MatrizCurricularRead, status_code=status.HTTP_200_OK)
async def update_matriz_curricular(
    id_matriz_curricular: int,
    data: MatrizCurricularUpdate,
    session: AsyncSession = Depends(get_session),
) -> MatrizCurricularRead:
    return await controller.update_matriz_curricular(
        session=session,
        id_matriz_curricular=id_matriz_curricular,
        data=data,
    )
