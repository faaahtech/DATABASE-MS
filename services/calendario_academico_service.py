from textwrap import wrap

from fastapi import HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession

from dtos.calendario_academico_dto import (
    CalendarioAcademicoCreate,
    CalendarioAcademicoRead,
    CalendarioAcademicoUpdate,
)
from models.calendario_academico import CalendarioAcademico, TipoCalendarioAcademico
from models.curso_unidade import CursoUnidade
from models.matricula_curso import MatriculaCurso, StatusMatriculaCurso
from repositories.aluno_repository import AlunoRepository
from repositories.calendario_academico_repository import CalendarioAcademicoRepository
from repositories.matricula_curso_repository import MatriculaCursoRepository
from repositories.unidade_repository import UnidadeRepository


class CalendarioAcademicoService:
    def __init__(self) -> None:
        self.calendario_repository = CalendarioAcademicoRepository()
        self.unidade_repository = UnidadeRepository()
        self.aluno_repository = AlunoRepository()
        self.matricula_curso_repository = MatriculaCursoRepository()

    async def create_calendario_academico(
        self,
        session: AsyncSession,
        data: CalendarioAcademicoCreate,
    ) -> CalendarioAcademicoRead:
        self._validate_payload(data)
        async with session.begin():
            unidade = await self.unidade_repository.get_by_id(session, data.id_unidade)
            if unidade is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Unidade não encontrada.")
            calendario = CalendarioAcademico(**data.model_dump())
            calendario = await self.calendario_repository.create(session, calendario)
        return self._to_read(calendario)

    async def list_calendarios_academicos(
        self,
        session: AsyncSession,
        limit: int = 100,
        offset: int = 0,
    ) -> list[CalendarioAcademicoRead]:
        calendarios = await self.calendario_repository.list(session, limit=limit, offset=offset)
        return [self._to_read(calendario) for calendario in calendarios]

    async def get_calendario_academico_by_id(
        self,
        session: AsyncSession,
        id_calendario_academico: int,
    ) -> CalendarioAcademicoRead:
        calendario = await self.calendario_repository.get_by_id(session, id_calendario_academico)
        if calendario is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Calendário acadêmico não encontrado.")
        return self._to_read(calendario)

    async def list_calendarios_by_unidade(
        self,
        session: AsyncSession,
        id_unidade: int,
        limit: int = 100,
        offset: int = 0,
    ) -> list[CalendarioAcademicoRead]:
        unidade = await self.unidade_repository.get_by_id(session, id_unidade)
        if unidade is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Unidade não encontrada.")
        calendarios = await self.calendario_repository.list_by_unidade(
            session=session,
            id_unidade=id_unidade,
            limit=limit,
            offset=offset,
        )
        return [self._to_read(calendario) for calendario in calendarios]

    async def list_calendarios_by_tipo(
        self,
        session: AsyncSession,
        tipo: TipoCalendarioAcademico,
        limit: int = 100,
        offset: int = 0,
    ) -> list[CalendarioAcademicoRead]:
        calendarios = await self.calendario_repository.list_by_tipo(
            session=session,
            tipo=tipo,
            limit=limit,
            offset=offset,
        )
        return [self._to_read(calendario) for calendario in calendarios]

    async def update_calendario_academico(
        self,
        session: AsyncSession,
        id_calendario_academico: int,
        data: CalendarioAcademicoUpdate,
    ) -> CalendarioAcademicoRead:
        async with session.begin():
            calendario = await self.calendario_repository.get_by_id(session, id_calendario_academico)
            if calendario is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Calendário acadêmico não encontrado.")

            update_data = data.model_dump(exclude_unset=True)
            if "id_unidade" in update_data:
                unidade = await self.unidade_repository.get_by_id(session, update_data["id_unidade"])
                if unidade is None:
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Unidade não encontrada.")

            merged_data = {
                "id_unidade": update_data.get("id_unidade", calendario.id_unidade),
                "titulo": update_data.get("titulo", calendario.titulo),
                "descricao": update_data.get("descricao", calendario.descricao),
                "tipo": update_data.get("tipo", calendario.tipo),
                "data_inicio": update_data.get("data_inicio", calendario.data_inicio),
                "data_fim": update_data.get("data_fim", calendario.data_fim),
                "periodo": update_data.get("periodo", calendario.periodo),
                "status": update_data.get("status", calendario.status),
            }
            self._validate_payload(CalendarioAcademicoCreate(**merged_data))

            for field, value in update_data.items():
                setattr(calendario, field, value)
            calendario = await self.calendario_repository.update(session, calendario)
        return self._to_read(calendario)

    async def gerar_pdf_by_unidade(
        self,
        session: AsyncSession,
        id_unidade: int,
    ) -> bytes:
        unidade = await self.unidade_repository.get_by_id(session, id_unidade)
        if unidade is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Unidade não encontrada.")

        calendarios = await self.calendario_repository.list_by_unidade(
            session=session,
            id_unidade=id_unidade,
            limit=500,
            offset=0,
        )
        linhas = self._calendarios_to_pdf_lines(
            titulo=f"Calendário Acadêmico - {unidade.nome}",
            calendarios=calendarios,
        )
        return self._build_simple_pdf(linhas)

    async def gerar_pdf_by_aluno(
        self,
        session: AsyncSession,
        id_aluno: int,
    ) -> bytes:
        aluno = await self.aluno_repository.get_by_id(session, id_aluno)
        if aluno is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Aluno não encontrado.")

        matricula = await self.matricula_curso_repository.get_matricula_cursando_by_aluno(
            session=session,
            id_aluno=id_aluno,
        )
        if matricula is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Matrícula ativa do aluno não encontrada.")

        curso_unidade = await session.get(CursoUnidade, matricula.id_curso_unidade)
        if curso_unidade is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="CursoUnidade não encontrado.")

        unidade = await self.unidade_repository.get_by_id(session, curso_unidade.id_unidade)
        if unidade is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Unidade não encontrada.")

        calendarios = await self.calendario_repository.list_by_unidade(
            session=session,
            id_unidade=unidade.id,
            limit=500,
            offset=0,
        )
        linhas = self._calendarios_to_pdf_lines(
            titulo=f"Calendário Acadêmico - {aluno.nome}",
            calendarios=calendarios,
            subtitulo=f"Unidade: {unidade.nome}",
        )
        return self._build_simple_pdf(linhas)

    def _validate_payload(self, data: CalendarioAcademicoCreate) -> None:
        if not data.titulo.strip():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Título do calendário é obrigatório.")
        if data.periodo is not None and data.periodo not in (1, 2):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Período deve ser 1, 2 ou nulo.")
        if data.data_fim is not None and data.data_fim < data.data_inicio:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Data final do calendário deve ser maior ou igual à data inicial.",
            )

    def _to_read(self, calendario: CalendarioAcademico) -> CalendarioAcademicoRead:
        return CalendarioAcademicoRead(
            id=calendario.id,
            id_unidade=calendario.id_unidade,
            titulo=calendario.titulo,
            descricao=calendario.descricao,
            tipo=calendario.tipo,
            data_inicio=calendario.data_inicio,
            data_fim=calendario.data_fim,
            periodo=calendario.periodo,
            status=calendario.status,
        )

    def _calendarios_to_pdf_lines(
        self,
        titulo: str,
        calendarios: list[CalendarioAcademico],
        subtitulo: str | None = None,
    ) -> list[str]:
        linhas = [titulo]
        if subtitulo:
            linhas.append(subtitulo)
        linhas.append("")

        if not calendarios:
            linhas.append("Nenhum evento acadêmico cadastrado.")
            return linhas

        for calendario in calendarios:
            data_fim = f" a {calendario.data_fim.strftime('%d/%m/%Y')}" if calendario.data_fim else ""
            periodo = f" - Período {calendario.periodo}" if calendario.periodo else ""
            linhas.append(
                f"{calendario.data_inicio.strftime('%d/%m/%Y')}{data_fim} - "
                f"{calendario.tipo.value.upper()}{periodo} - {calendario.titulo}"
            )
            if calendario.descricao:
                for wrapped in wrap(calendario.descricao, width=92):
                    linhas.append(f"  {wrapped}")
            linhas.append("")
        return linhas

    def _build_simple_pdf(self, linhas: list[str]) -> bytes:
        content_lines = ["BT", "/F1 11 Tf", "50 790 Td", "14 TL"]
        usable_lines = linhas[:52]
        for linha in usable_lines:
            escaped = self._escape_pdf_text(linha)
            content_lines.append(f"({escaped}) Tj")
            content_lines.append("T*")
        content_lines.append("ET")
        stream = "\n".join(content_lines).encode("latin-1", errors="replace")

        objects = [
            b"1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n",
            b"2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n",
            b"3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>\nendobj\n",
            b"4 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>\nendobj\n",
            b"5 0 obj\n<< /Length " + str(len(stream)).encode() + b" >>\nstream\n" + stream + b"\nendstream\nendobj\n",
        ]

        pdf = bytearray(b"%PDF-1.4\n")
        offsets = [0]
        for obj in objects:
            offsets.append(len(pdf))
            pdf.extend(obj)
        xref_offset = len(pdf)
        pdf.extend(f"xref\n0 {len(objects) + 1}\n".encode())
        pdf.extend(b"0000000000 65535 f \n")
        for offset in offsets[1:]:
            pdf.extend(f"{offset:010d} 00000 n \n".encode())
        pdf.extend(
            f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref_offset}\n%%EOF".encode()
        )
        return bytes(pdf)

    def _escape_pdf_text(self, text: str) -> str:
        return text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
