from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlmodel.ext.asyncio.session import AsyncSession

from dtos.matricula_disciplina_dto import (
    MatriculaDisciplinaCreate,
    MatriculaDisciplinaRead,
    MatriculaDisciplinaUpdateStatus,
)
from models.matricula_curso import MatriculaCurso
from models.matricula_disciplina import MatriculaDisciplina, StatusMatriculaDisciplina
from models.matriz_curricular import MatrizCurricular
from models.oferta_disciplina import OfertaDisciplina
from repositories.matricula_curso_repository import MatriculaCursoRepository
from repositories.matricula_disciplina_repository import MatriculaDisciplinaRepository
from repositories.oferta_disciplina_repository import OfertaDisciplinaRepository


class MatriculaDisciplinaService:
    def __init__(self) -> None:
        self.matricula_disciplina_repository = MatriculaDisciplinaRepository()
        self.matricula_curso_repository = MatriculaCursoRepository()
        self.oferta_disciplina_repository = OfertaDisciplinaRepository()

    async def create_matricula_disciplina(
        self,
        session: AsyncSession,
        data: MatriculaDisciplinaCreate,
    ) -> MatriculaDisciplinaRead:
        matricula_disciplina = MatriculaDisciplina(**data.model_dump())

        try:
            async with session.begin():
                matricula_curso = await self._get_matricula_curso_or_404(session, data.id_matricula_curso)
                oferta_disciplina = await self._get_oferta_disciplina_or_404(session, data.id_oferta_disciplina)
                await self._validate_compatibilidade_matricula_oferta(session, matricula_curso, oferta_disciplina)

                exists = await self.matricula_disciplina_repository.exists_by_matricula_curso_and_oferta(
                    session=session,
                    id_matricula_curso=data.id_matricula_curso,
                    id_oferta_disciplina=data.id_oferta_disciplina,
                )
                if exists:
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail="Aluno já matriculado nesta oferta de disciplina.",
                    )

                if data.status == StatusMatriculaDisciplina.CURSANDO:
                    self._consumir_vaga(oferta_disciplina)
                    await self.oferta_disciplina_repository.update(session, oferta_disciplina)

                matricula_disciplina = await self.matricula_disciplina_repository.create(session, matricula_disciplina)
        except IntegrityError as exc:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Não foi possível criar matrícula em disciplina por conflito de dados únicos.",
            ) from exc

        return self._to_read(matricula_disciplina)

    async def get_matricula_disciplina_by_id(
        self,
        session: AsyncSession,
        id_matricula_disciplina: int,
    ) -> MatriculaDisciplinaRead:
        matricula_disciplina = await self.matricula_disciplina_repository.get_by_id(session, id_matricula_disciplina)
        if matricula_disciplina is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Matrícula em disciplina não encontrada.")
        return self._to_read(matricula_disciplina)

    async def list_matriculas_disciplina_by_matricula_curso(
        self,
        session: AsyncSession,
        id_matricula_curso: int,
        limit: int = 100,
        offset: int = 0,
    ) -> list[MatriculaDisciplinaRead]:
        await self._get_matricula_curso_or_404(session, id_matricula_curso)
        matriculas = await self.matricula_disciplina_repository.list_by_matricula_curso(
            session=session,
            id_matricula_curso=id_matricula_curso,
            limit=limit,
            offset=offset,
        )
        return [self._to_read(matricula) for matricula in matriculas]

    async def list_matriculas_disciplina_by_oferta_disciplina(
        self,
        session: AsyncSession,
        id_oferta_disciplina: int,
        limit: int = 100,
        offset: int = 0,
    ) -> list[MatriculaDisciplinaRead]:
        await self._get_oferta_disciplina_or_404(session, id_oferta_disciplina)
        matriculas = await self.matricula_disciplina_repository.list_by_oferta_disciplina(
            session=session,
            id_oferta_disciplina=id_oferta_disciplina,
            limit=limit,
            offset=offset,
        )
        return [self._to_read(matricula) for matricula in matriculas]

    async def update_matricula_disciplina_status(
        self,
        session: AsyncSession,
        id_matricula_disciplina: int,
        data: MatriculaDisciplinaUpdateStatus,
    ) -> MatriculaDisciplinaRead:
        try:
            async with session.begin():
                matricula_disciplina = await self.matricula_disciplina_repository.get_by_id(
                    session,
                    id_matricula_disciplina,
                )
                if matricula_disciplina is None:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Matrícula em disciplina não encontrada.",
                    )

                oferta_disciplina = await self._get_oferta_disciplina_or_404(
                    session,
                    matricula_disciplina.id_oferta_disciplina,
                )

                status_anterior = matricula_disciplina.status
                novo_status = data.status

                if status_anterior != StatusMatriculaDisciplina.CURSANDO and novo_status == StatusMatriculaDisciplina.CURSANDO:
                    self._consumir_vaga(oferta_disciplina)
                    await self.oferta_disciplina_repository.update(session, oferta_disciplina)
                elif status_anterior == StatusMatriculaDisciplina.CURSANDO and novo_status != StatusMatriculaDisciplina.CURSANDO:
                    self._devolver_vaga(oferta_disciplina)
                    await self.oferta_disciplina_repository.update(session, oferta_disciplina)

                matricula_disciplina.status = novo_status
                matricula_disciplina = await self.matricula_disciplina_repository.update(session, matricula_disciplina)
        except IntegrityError as exc:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Não foi possível atualizar matrícula em disciplina por conflito de dados.",
            ) from exc

        return self._to_read(matricula_disciplina)

    async def _get_matricula_curso_or_404(
        self,
        session: AsyncSession,
        id_matricula_curso: int,
    ) -> MatriculaCurso:
        matricula_curso = await self.matricula_curso_repository.get_by_id(session, id_matricula_curso)
        if matricula_curso is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Matrícula de curso não encontrada.")
        return matricula_curso

    async def _get_oferta_disciplina_or_404(
        self,
        session: AsyncSession,
        id_oferta_disciplina: int,
    ) -> OfertaDisciplina:
        oferta_disciplina = await self.oferta_disciplina_repository.get_by_id(session, id_oferta_disciplina)
        if oferta_disciplina is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Oferta de disciplina não encontrada.")
        return oferta_disciplina

    async def _validate_compatibilidade_matricula_oferta(
        self,
        session: AsyncSession,
        matricula_curso: MatriculaCurso,
        oferta_disciplina: OfertaDisciplina,
    ) -> None:
        matriz_curricular = await session.get(MatrizCurricular, oferta_disciplina.id_matriz_curricular)
        if matriz_curricular is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Matriz curricular da oferta não encontrada.")

        if matriz_curricular.id_curso_unidade != matricula_curso.id_curso_unidade:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A oferta de disciplina não pertence ao mesmo curso_unidade da matrícula de curso.",
            )

    def _consumir_vaga(self, oferta_disciplina: OfertaDisciplina) -> None:
        if oferta_disciplina.vagas_disponiveis <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Não há vagas disponíveis para esta oferta de disciplina.",
            )
        oferta_disciplina.vagas_disponiveis -= 1

    def _devolver_vaga(self, oferta_disciplina: OfertaDisciplina) -> None:
        if oferta_disciplina.vagas_disponiveis < oferta_disciplina.vagas_total:
            oferta_disciplina.vagas_disponiveis += 1

    def _to_read(self, matricula_disciplina: MatriculaDisciplina) -> MatriculaDisciplinaRead:
        return MatriculaDisciplinaRead(
            id=matricula_disciplina.id,
            id_matricula_curso=matricula_disciplina.id_matricula_curso,
            id_oferta_disciplina=matricula_disciplina.id_oferta_disciplina,
            status=matricula_disciplina.status,
            data_matricula=matricula_disciplina.data_matricula,
        )
