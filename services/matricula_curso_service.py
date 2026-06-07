from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlmodel.ext.asyncio.session import AsyncSession

from dtos.llm_academico_dto import TransferirHorarioRequest
from dtos.matricula_curso_dto import MatriculaCursoCreate, MatriculaCursoRead, MatriculaCursoUpdateStatus
from models.aluno import Aluno
from models.curso_unidade import CursoUnidade
from models.matricula_curso import MatriculaCurso, StatusMatriculaCurso
from repositories.matricula_curso_repository import MatriculaCursoRepository
from services.service_utils import validate_or_400
from utils.academic_validators import validate_positive_int, validate_semestre_letivo
from utils.validators import validate_ra


class MatriculaCursoService:
    def __init__(self) -> None:
        self.matricula_curso_repository = MatriculaCursoRepository()

    async def create_matricula_curso(
        self,
        session: AsyncSession,
        data: MatriculaCursoCreate,
    ) -> MatriculaCursoRead:
        ra = validate_or_400(validate_ra, data.ra)
        validate_or_400(validate_positive_int, data.semestre_curso, "Semestre do curso")
        validate_or_400(validate_semestre_letivo, data.semestre_ingresso)
        validate_or_400(validate_positive_int, data.ano_ingresso, "Ano de ingresso")

        matricula_curso = MatriculaCurso(**{**data.model_dump(), "ra": ra})

        try:
            async with session.begin():
                await self._validate_aluno_exists(session, data.id_aluno)
                await self._validate_curso_unidade_exists(session, data.id_curso_unidade)

                if await self.matricula_curso_repository.exists_by_ra(session, ra):
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail="Já existe matrícula de curso com este RA.",
                    )

                matricula_curso = await self.matricula_curso_repository.create(session, matricula_curso)
        except IntegrityError as exc:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Não foi possível criar matrícula de curso por conflito de dados únicos.",
            ) from exc

        return self._to_read(matricula_curso)

    async def get_matricula_curso_by_id(
        self,
        session: AsyncSession,
        id_matricula_curso: int,
    ) -> MatriculaCursoRead:
        matricula_curso = await self.matricula_curso_repository.get_by_id(session, id_matricula_curso)
        if matricula_curso is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Matrícula de curso não encontrada.")
        return self._to_read(matricula_curso)

    async def get_matricula_curso_by_ra(self, session: AsyncSession, ra: str) -> MatriculaCursoRead:
        normalized_ra = validate_or_400(validate_ra, ra)
        matricula_curso = await self.matricula_curso_repository.get_by_ra(session, normalized_ra)
        if matricula_curso is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Matrícula de curso não encontrada.")
        return self._to_read(matricula_curso)

    async def list_matriculas_curso_by_aluno(
        self,
        session: AsyncSession,
        id_aluno: int,
        limit: int = 100,
        offset: int = 0,
    ) -> list[MatriculaCursoRead]:
        await self._validate_aluno_exists(session, id_aluno)
        matriculas = await self.matricula_curso_repository.list_by_aluno(
            session=session,
            id_aluno=id_aluno,
            limit=limit,
            offset=offset,
        )
        return [self._to_read(matricula) for matricula in matriculas]

    async def update_matricula_curso_status(
        self,
        session: AsyncSession,
        id_matricula_curso: int,
        data: MatriculaCursoUpdateStatus,
    ) -> MatriculaCursoRead:
        async with session.begin():
            matricula_curso = await self._get_matricula_or_404(session, id_matricula_curso)
            matricula_curso.status = data.status
            matricula_curso = await self.matricula_curso_repository.update(session, matricula_curso)

        return self._to_read(matricula_curso)

    async def transferir_horario(
        self,
        session: AsyncSession,
        id_matricula_curso: int,
        data: TransferirHorarioRequest,
    ) -> MatriculaCursoRead:
        async with session.begin():
            matricula_curso = await self._get_matricula_or_404(session, id_matricula_curso)
            if matricula_curso.status in (StatusMatriculaCurso.CANCELADO, StatusMatriculaCurso.CONCLUIDO):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Matrícula cancelada ou concluída não pode ser transferida.",
                )

            curso_unidade_atual = await self._get_curso_unidade_or_404(session, matricula_curso.id_curso_unidade)
            curso_unidade_destino = await self._get_curso_unidade_or_404(session, data.id_curso_unidade_destino)

            if curso_unidade_destino.id_curso != curso_unidade_atual.id_curso:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Transferência de horário só é permitida para o mesmo curso.",
                )

            periodo_destino = data.periodo_destino or matricula_curso.periodo
            if (
                matricula_curso.id_curso_unidade == data.id_curso_unidade_destino
                and matricula_curso.periodo == periodo_destino
            ):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="A matrícula já está vinculada ao curso/unidade/período informado.",
                )

            matricula_curso.id_curso_unidade = data.id_curso_unidade_destino
            matricula_curso.periodo = periodo_destino
            matricula_curso = await self.matricula_curso_repository.update(session, matricula_curso)

        return self._to_read(matricula_curso)

    async def trancar_matricula(
        self,
        session: AsyncSession,
        id_matricula_curso: int,
    ) -> MatriculaCursoRead:
        return await self.update_matricula_curso_status(
            session=session,
            id_matricula_curso=id_matricula_curso,
            data=MatriculaCursoUpdateStatus(status=StatusMatriculaCurso.TRANCADO),
        )

    async def ativar_matricula(
        self,
        session: AsyncSession,
        id_matricula_curso: int,
    ) -> MatriculaCursoRead:
        return await self.update_matricula_curso_status(
            session=session,
            id_matricula_curso=id_matricula_curso,
            data=MatriculaCursoUpdateStatus(status=StatusMatriculaCurso.CURSANDO),
        )

    async def _validate_aluno_exists(self, session: AsyncSession, id_aluno: int) -> None:
        aluno = await session.get(Aluno, id_aluno)
        if aluno is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Aluno não encontrado.")

    async def _validate_curso_unidade_exists(self, session: AsyncSession, id_curso_unidade: int) -> None:
        curso_unidade = await session.get(CursoUnidade, id_curso_unidade)
        if curso_unidade is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="CursoUnidade não encontrado.")

    async def _get_matricula_or_404(
        self,
        session: AsyncSession,
        id_matricula_curso: int,
    ) -> MatriculaCurso:
        matricula_curso = await self.matricula_curso_repository.get_by_id(session, id_matricula_curso)
        if matricula_curso is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Matrícula de curso não encontrada.")
        return matricula_curso

    async def _get_curso_unidade_or_404(
        self,
        session: AsyncSession,
        id_curso_unidade: int,
    ) -> CursoUnidade:
        curso_unidade = await session.get(CursoUnidade, id_curso_unidade)
        if curso_unidade is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="CursoUnidade não encontrado.")
        return curso_unidade

    def _to_read(self, matricula_curso: MatriculaCurso) -> MatriculaCursoRead:
        return MatriculaCursoRead(
            id=matricula_curso.id,
            id_aluno=matricula_curso.id_aluno,
            id_curso_unidade=matricula_curso.id_curso_unidade,
            ra=matricula_curso.ra,
            semestre_curso=matricula_curso.semestre_curso,
            periodo=matricula_curso.periodo,
            status=matricula_curso.status,
            ano_ingresso=matricula_curso.ano_ingresso,
            semestre_ingresso=matricula_curso.semestre_ingresso,
        )
