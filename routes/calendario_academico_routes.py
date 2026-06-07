from fastapi import APIRouter, Depends, Query, Response, status
from sqlmodel.ext.asyncio.session import AsyncSession

from controller.calendario_academico_controller import CalendarioAcademicoController
from dtos.calendario_academico_dto import (
    CalendarioAcademicoCreate,
    CalendarioAcademicoRead,
    CalendarioAcademicoUpdate,
)
from models.calendario_academico import TipoCalendarioAcademico
from repositories.postgres_conn import get_session

router = APIRouter(prefix="/calendario-academico", tags=["Calendário Acadêmico"])
controller = CalendarioAcademicoController()


@router.post("", response_model=CalendarioAcademicoRead, status_code=status.HTTP_201_CREATED)
async def create_calendario_academico(
    data: CalendarioAcademicoCreate,
    session: AsyncSession = Depends(get_session),
) -> CalendarioAcademicoRead:
    return await controller.create_calendario_academico(session=session, data=data)


@router.get("", response_model=list[CalendarioAcademicoRead], status_code=status.HTTP_200_OK)
async def list_calendarios_academicos(
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    session: AsyncSession = Depends(get_session),
) -> list[CalendarioAcademicoRead]:
    return await controller.list_calendarios_academicos(session=session, limit=limit, offset=offset)


@router.get("/aluno/{id_aluno}/pdf", status_code=status.HTTP_200_OK)
async def get_calendario_pdf_by_aluno(
    id_aluno: int,
    session: AsyncSession = Depends(get_session),
) -> Response:
    pdf_bytes = await controller.gerar_pdf_by_aluno(session=session, id_aluno=id_aluno)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"inline; filename=calendario_academico_aluno_{id_aluno}.pdf"},
    )


@router.get("/unidade/{id_unidade}/pdf", status_code=status.HTTP_200_OK)
async def get_calendario_pdf_by_unidade(
    id_unidade: int,
    session: AsyncSession = Depends(get_session),
) -> Response:
    pdf_bytes = await controller.gerar_pdf_by_unidade(session=session, id_unidade=id_unidade)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"inline; filename=calendario_academico_unidade_{id_unidade}.pdf"},
    )


@router.get("/unidade/{id_unidade}", response_model=list[CalendarioAcademicoRead], status_code=status.HTTP_200_OK)
async def list_calendarios_by_unidade(
    id_unidade: int,
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    session: AsyncSession = Depends(get_session),
) -> list[CalendarioAcademicoRead]:
    return await controller.list_calendarios_by_unidade(
        session=session,
        id_unidade=id_unidade,
        limit=limit,
        offset=offset,
    )


@router.get("/tipo/{tipo}", response_model=list[CalendarioAcademicoRead], status_code=status.HTTP_200_OK)
async def list_calendarios_by_tipo(
    tipo: TipoCalendarioAcademico,
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    session: AsyncSession = Depends(get_session),
) -> list[CalendarioAcademicoRead]:
    return await controller.list_calendarios_by_tipo(
        session=session,
        tipo=tipo,
        limit=limit,
        offset=offset,
    )


@router.get("/{id_calendario_academico}", response_model=CalendarioAcademicoRead, status_code=status.HTTP_200_OK)
async def get_calendario_academico_by_id(
    id_calendario_academico: int,
    session: AsyncSession = Depends(get_session),
) -> CalendarioAcademicoRead:
    return await controller.get_calendario_academico_by_id(
        session=session,
        id_calendario_academico=id_calendario_academico,
    )


@router.patch("/{id_calendario_academico}", response_model=CalendarioAcademicoRead, status_code=status.HTTP_200_OK)
async def update_calendario_academico(
    id_calendario_academico: int,
    data: CalendarioAcademicoUpdate,
    session: AsyncSession = Depends(get_session),
) -> CalendarioAcademicoRead:
    return await controller.update_calendario_academico(
        session=session,
        id_calendario_academico=id_calendario_academico,
        data=data,
    )
