from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlmodel.ext.asyncio.session import AsyncSession

from dtos.disciplina_dto import DisciplinaCreate, DisciplinaRead, DisciplinaUpdate
from models.disciplina import Disciplina
from repositories.disciplina_repository import DisciplinaRepository
from services.service_utils import validate_or_400
from utils.academic_validators import validate_positive_int


class DisciplinaService:
    def __init__(self) -> None:
        self.disciplina_repository = DisciplinaRepository()

    async def create_disciplina(self, session: AsyncSession, data: DisciplinaCreate) -> DisciplinaRead:
        codigo = data.codigo.upper().strip()
        validate_or_400(validate_positive_int, data.carga_horaria, "Carga horária")
        disciplina = Disciplina(**{**data.model_dump(), "codigo": codigo})

        try:
            async with session.begin():
                if await self.disciplina_repository.exists_by_codigo(session, codigo):
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail="Já existe disciplina cadastrada com este código.",
                    )
                disciplina = await self.disciplina_repository.create(session, disciplina)
        except IntegrityError as exc:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Já existe disciplina cadastrada com algum dado único informado.",
            ) from exc

        return self._to_read(disciplina)

    async def get_disciplina_by_id(self, session: AsyncSession, id_disciplina: int) -> DisciplinaRead:
        disciplina = await self.disciplina_repository.get_by_id(session, id_disciplina)
        if disciplina is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Disciplina não encontrada.")
        return self._to_read(disciplina)

    async def get_disciplina_by_codigo(self, session: AsyncSession, codigo: str) -> DisciplinaRead:
        disciplina = await self.disciplina_repository.get_by_codigo(session, codigo)
        if disciplina is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Disciplina não encontrada.")
        return self._to_read(disciplina)

    async def list_disciplinas(
        self,
        session: AsyncSession,
        limit: int = 100,
        offset: int = 0,
    ) -> list[DisciplinaRead]:
        disciplinas = await self.disciplina_repository.list(session, limit=limit, offset=offset)
        return [self._to_read(disciplina) for disciplina in disciplinas]

    async def update_disciplina(
        self,
        session: AsyncSession,
        id_disciplina: int,
        data: DisciplinaUpdate,
    ) -> DisciplinaRead:
        async with session.begin():
            disciplina = await self.disciplina_repository.get_by_id(session, id_disciplina)
            if disciplina is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Disciplina não encontrada.")
            update_data = data.model_dump(exclude_unset=True)
            if "codigo" in update_data and update_data["codigo"] is not None:
                novo_codigo = update_data["codigo"].upper().strip()
                existente = await self.disciplina_repository.get_by_codigo(session, novo_codigo)
                if existente is not None and existente.id != id_disciplina:
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail="Já existe outra disciplina com este código.",
                    )
                update_data["codigo"] = novo_codigo
            if "carga_horaria" in update_data and update_data["carga_horaria"] is not None:
                validate_or_400(validate_positive_int, update_data["carga_horaria"], "Carga horária")
            for field, value in update_data.items():
                setattr(disciplina, field, value)
            disciplina = await self.disciplina_repository.update(session, disciplina)
        return self._to_read(disciplina)

    def _to_read(self, disciplina: Disciplina) -> DisciplinaRead:
        return DisciplinaRead(
            id=disciplina.id,
            nome=disciplina.nome,
            codigo=disciplina.codigo,
            carga_horaria=disciplina.carga_horaria,
            status=disciplina.status,
        )
