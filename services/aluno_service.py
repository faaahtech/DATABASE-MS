from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlmodel.ext.asyncio.session import AsyncSession

from dtos.aluno_dto import AlunoCreate, AlunoListItem, AlunoRead
from models.aluno import Aluno
from repositories.aluno_repository import AlunoRepository
from repositories.endereco_repository import EnderecoRepository
from services.service_utils import validate_or_400
from utils.validators import validate_cpf, validate_email


class AlunoService:
    def __init__(self) -> None:
        self.aluno_repository = AlunoRepository()
        self.endereco_repository = EnderecoRepository()

    async def create_aluno(self, session: AsyncSession, data: AlunoCreate) -> AlunoRead:
        email = validate_or_400(validate_email, data.email)
        cpf = validate_or_400(validate_cpf, data.cpf)

        aluno = Aluno(**{**data.model_dump(), "email": email, "cpf": cpf})

        try:
            async with session.begin():
                endereco = await self.endereco_repository.get_by_id(session, data.id_endereco)
                if endereco is None:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Endereço não encontrado.",
                    )

                if await self.aluno_repository.exists_by_cpf(session, cpf):
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail="Já existe aluno cadastrado com este CPF.",
                    )

                aluno = await self.aluno_repository.create(session, aluno)
        except IntegrityError as exc:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Já existe aluno cadastrado com algum dado único informado.",
            ) from exc

        return self._to_read(aluno)

    async def get_aluno_by_id(self, session: AsyncSession, id_aluno: int) -> AlunoRead:
        aluno = await self.aluno_repository.get_by_id(session, id_aluno)
        if aluno is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Aluno não encontrado.",
            )
        return self._to_read(aluno)

    async def get_aluno_by_ra(self, session: AsyncSession, ra: str) -> AlunoRead:
        aluno = await self.aluno_repository.get_by_ra(session, ra)
        if aluno is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Aluno não encontrado para o RA informado.",
            )
        return self._to_read(aluno)

    async def list_alunos(
        self,
        session: AsyncSession,
        limit: int = 100,
        offset: int = 0,
    ) -> list[AlunoListItem]:
        alunos = await self.aluno_repository.list(session, limit=limit, offset=offset)
        return [self._to_list_item(aluno) for aluno in alunos]

    def _to_read(self, aluno: Aluno) -> AlunoRead:
        return AlunoRead(
            id=aluno.id,
            id_endereco=aluno.id_endereco,
            nome=aluno.nome,
            cpf=aluno.cpf,
            data_nascimento=aluno.data_nascimento,
            email=aluno.email,
            telefone=aluno.telefone,
            status=aluno.status,
        )

    def _to_list_item(self, aluno: Aluno) -> AlunoListItem:
        return AlunoListItem(
            id=aluno.id,
            nome=aluno.nome,
            cpf=aluno.cpf,
            email=aluno.email,
            telefone=aluno.telefone,
            status=aluno.status,
        )
