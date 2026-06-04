from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlmodel.ext.asyncio.session import AsyncSession

from dtos.professor_dto import ProfessorCreate, ProfessorRead
from models.professor import Professor
from repositories.professor_repository import ProfessorRepository
from services.service_utils import validate_or_400
from utils.validators import validate_email


class ProfessorService:
    def __init__(self) -> None:
        self.professor_repository = ProfessorRepository()

    async def create_professor(self, session: AsyncSession, data: ProfessorCreate) -> ProfessorRead:
        email = validate_or_400(validate_email, data.email)

        professor = Professor(**{**data.model_dump(), "email": email})

        try:
            async with session.begin():
                if await self.professor_repository.exists_by_email(session, email):
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail="Já existe professor cadastrado com este e-mail.",
                    )

                professor = await self.professor_repository.create(session, professor)
        except IntegrityError as exc:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Já existe professor cadastrado com algum dado único informado.",
            ) from exc

        return self._to_read(professor)

    async def get_professor_by_id(self, session: AsyncSession, id_professor: int) -> ProfessorRead:
        professor = await self.professor_repository.get_by_id(session, id_professor)
        if professor is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Professor não encontrado.",
            )
        return self._to_read(professor)

    async def list_professores(
        self,
        session: AsyncSession,
        limit: int = 100,
        offset: int = 0,
    ) -> list[ProfessorRead]:
        professores = await self.professor_repository.list(session, limit=limit, offset=offset)
        return [self._to_read(professor) for professor in professores]

    def _to_read(self, professor: Professor) -> ProfessorRead:
        return ProfessorRead(
            id=professor.id,
            nome=professor.nome,
            email=professor.email,
            telefone=professor.telefone,
            status=professor.status,
        )
