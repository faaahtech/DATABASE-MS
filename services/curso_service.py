from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlmodel.ext.asyncio.session import AsyncSession

from dtos.curso_dto import CursoCreate, CursoRead, CursoUpdate
from models.curso import Curso
from repositories.curso_repository import CursoRepository
from services.service_utils import validate_or_400
from utils.academic_validators import validate_positive_int


class CursoService:
    def __init__(self) -> None:
        self.curso_repository = CursoRepository()

    async def create_curso(self, session: AsyncSession, data: CursoCreate) -> CursoRead:
        sigla = data.sigla.upper().strip()
        validate_or_400(validate_positive_int, data.duracao_semestres, "Duração em semestres")
        curso = Curso(**{**data.model_dump(), "sigla": sigla})

        try:
            async with session.begin():
                if await self.curso_repository.exists_by_sigla(session, sigla):
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail="Já existe curso cadastrado com esta sigla.",
                    )
                curso = await self.curso_repository.create(session, curso)
        except IntegrityError as exc:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Já existe curso cadastrado com algum dado único informado.",
            ) from exc

        return self._to_read(curso)

    async def get_curso_by_id(self, session: AsyncSession, id_curso: int) -> CursoRead:
        curso = await self.curso_repository.get_by_id(session, id_curso)
        if curso is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Curso não encontrado.")
        return self._to_read(curso)

    async def get_curso_by_sigla(self, session: AsyncSession, sigla: str) -> CursoRead:
        curso = await self.curso_repository.get_by_sigla(session, sigla)
        if curso is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Curso não encontrado.")
        return self._to_read(curso)

    async def list_cursos(
        self,
        session: AsyncSession,
        limit: int = 100,
        offset: int = 0,
    ) -> list[CursoRead]:
        cursos = await self.curso_repository.list(session, limit=limit, offset=offset)
        return [self._to_read(curso) for curso in cursos]

    async def update_curso(
        self,
        session: AsyncSession,
        id_curso: int,
        data: CursoUpdate,
    ) -> CursoRead:
        async with session.begin():
            curso = await self.curso_repository.get_by_id(session, id_curso)
            if curso is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Curso não encontrado.")

            update_data = data.model_dump(exclude_unset=True)
            if "sigla" in update_data and update_data["sigla"] is not None:
                nova_sigla = update_data["sigla"].upper().strip()
                existente = await self.curso_repository.get_by_sigla(session, nova_sigla)
                if existente is not None and existente.id != id_curso:
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail="Já existe outro curso com esta sigla.",
                    )
                update_data["sigla"] = nova_sigla

            if "duracao_semestres" in update_data and update_data["duracao_semestres"] is not None:
                validate_or_400(
                    validate_positive_int,
                    update_data["duracao_semestres"],
                    "Duração em semestres",
                )

            for field, value in update_data.items():
                setattr(curso, field, value)
            curso = await self.curso_repository.update(session, curso)

        return self._to_read(curso)

    def _to_read(self, curso: Curso) -> CursoRead:
        return CursoRead(
            id=curso.id,
            nome=curso.nome,
            sigla=curso.sigla,
            duracao_semestres=curso.duracao_semestres,
            status=curso.status,
        )
