from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlmodel.ext.asyncio.session import AsyncSession

from dtos.matriz_curricular_dto import MatrizCurricularCreate, MatrizCurricularRead, MatrizCurricularUpdate
from models.matriz_curricular import MatrizCurricular
from repositories.curso_unidade_repository import CursoUnidadeRepository
from repositories.disciplina_repository import DisciplinaRepository
from repositories.matriz_curricular_repository import MatrizCurricularRepository
from services.service_utils import validate_or_400
from utils.academic_validators import validate_positive_int


class MatrizCurricularService:
    def __init__(self) -> None:
        self.matriz_curricular_repository = MatrizCurricularRepository()
        self.curso_unidade_repository = CursoUnidadeRepository()
        self.disciplina_repository = DisciplinaRepository()

    async def create_matriz_curricular(
        self,
        session: AsyncSession,
        data: MatrizCurricularCreate,
    ) -> MatrizCurricularRead:
        validate_or_400(validate_positive_int, data.semestre_recomendado, "Semestre recomendado")
        matriz_curricular = MatrizCurricular(**data.model_dump())

        try:
            async with session.begin():
                await self._validate_curso_unidade_exists(session, data.id_curso_unidade)
                await self._validate_disciplina_exists(session, data.id_disciplina)

                exists = await self.matriz_curricular_repository.exists_by_curso_unidade_and_disciplina(
                    session=session,
                    id_curso_unidade=data.id_curso_unidade,
                    id_disciplina=data.id_disciplina,
                )
                if exists:
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail="Já existe matriz curricular para este curso_unidade e disciplina.",
                    )

                matriz_curricular = await self.matriz_curricular_repository.create(session, matriz_curricular)
        except IntegrityError as exc:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Não foi possível criar matriz curricular por conflito de dados.",
            ) from exc

        return self._to_read(matriz_curricular)

    async def get_matriz_curricular_by_id(
        self,
        session: AsyncSession,
        id_matriz_curricular: int,
    ) -> MatrizCurricularRead:
        matriz_curricular = await self.matriz_curricular_repository.get_by_id(session, id_matriz_curricular)
        if matriz_curricular is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Matriz curricular não encontrada.")
        return self._to_read(matriz_curricular)

    async def list_matrizes_curriculares(
        self,
        session: AsyncSession,
        limit: int = 100,
        offset: int = 0,
    ) -> list[MatrizCurricularRead]:
        matrizes = await self.matriz_curricular_repository.list(session, limit=limit, offset=offset)
        return [self._to_read(matriz) for matriz in matrizes]

    async def list_matrizes_curriculares_by_curso_unidade(
        self,
        session: AsyncSession,
        id_curso_unidade: int,
        limit: int = 100,
        offset: int = 0,
    ) -> list[MatrizCurricularRead]:
        await self._validate_curso_unidade_exists(session, id_curso_unidade)
        matrizes = await self.matriz_curricular_repository.list_by_curso_unidade(
            session=session,
            id_curso_unidade=id_curso_unidade,
            limit=limit,
            offset=offset,
        )
        return [self._to_read(matriz) for matriz in matrizes]

    async def update_matriz_curricular(
        self,
        session: AsyncSession,
        id_matriz_curricular: int,
        data: MatrizCurricularUpdate,
    ) -> MatrizCurricularRead:
        try:
            async with session.begin():
                matriz_curricular = await self.matriz_curricular_repository.get_by_id(session, id_matriz_curricular)
                if matriz_curricular is None:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Matriz curricular não encontrada.",
                    )

                update_data = data.model_dump(exclude_unset=True)

                novo_id_curso_unidade = update_data.get("id_curso_unidade", matriz_curricular.id_curso_unidade)
                novo_id_disciplina = update_data.get("id_disciplina", matriz_curricular.id_disciplina)

                if "id_curso_unidade" in update_data and update_data["id_curso_unidade"] is not None:
                    await self._validate_curso_unidade_exists(session, update_data["id_curso_unidade"])
                if "id_disciplina" in update_data and update_data["id_disciplina"] is not None:
                    await self._validate_disciplina_exists(session, update_data["id_disciplina"])
                if "semestre_recomendado" in update_data and update_data["semestre_recomendado"] is not None:
                    validate_or_400(
                        validate_positive_int,
                        update_data["semestre_recomendado"],
                        "Semestre recomendado",
                    )

                existente = await self.matriz_curricular_repository.get_by_curso_unidade_and_disciplina(
                    session=session,
                    id_curso_unidade=novo_id_curso_unidade,
                    id_disciplina=novo_id_disciplina,
                )
                if existente is not None and existente.id != id_matriz_curricular:
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail="Já existe outra matriz curricular para este curso_unidade e disciplina.",
                    )

                for field, value in update_data.items():
                    setattr(matriz_curricular, field, value)

                matriz_curricular = await self.matriz_curricular_repository.update(session, matriz_curricular)
        except IntegrityError as exc:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Não foi possível atualizar matriz curricular por conflito de dados.",
            ) from exc

        return self._to_read(matriz_curricular)

    async def _validate_curso_unidade_exists(self, session: AsyncSession, id_curso_unidade: int) -> None:
        curso_unidade = await self.curso_unidade_repository.get_by_id(session, id_curso_unidade)
        if curso_unidade is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="CursoUnidade não encontrado.")

    async def _validate_disciplina_exists(self, session: AsyncSession, id_disciplina: int) -> None:
        disciplina = await self.disciplina_repository.get_by_id(session, id_disciplina)
        if disciplina is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Disciplina não encontrada.")

    def _to_read(self, matriz_curricular: MatrizCurricular) -> MatrizCurricularRead:
        return MatrizCurricularRead(
            id=matriz_curricular.id,
            id_curso_unidade=matriz_curricular.id_curso_unidade,
            id_disciplina=matriz_curricular.id_disciplina,
            semestre_recomendado=matriz_curricular.semestre_recomendado,
            obrigatoria=matriz_curricular.obrigatoria,
            status=matriz_curricular.status,
        )
