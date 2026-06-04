from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlmodel.ext.asyncio.session import AsyncSession

from dtos.usuario_dto import (
    UsuarioCreateAlunoRequest,
    UsuarioCreateProfessorRequest,
    UsuarioRead,
    UsuarioRegisterRequest,
    UsuarioRegisterResponse,
)
from models.aluno import Aluno
from models.endereco import Endereco
from models.professor import Professor
from models.usuario import PerfilUsuario, StatusUsuario, Usuario
from repositories.aluno_repository import AlunoRepository
from repositories.endereco_repository import EnderecoRepository
from repositories.professor_repository import ProfessorRepository
from repositories.usuario_repository import UsuarioRepository
from services.service_utils import validate_or_400
from utils.security import hash_password
from utils.validators import validate_cpf, validate_email, validate_password_strength


class UsuarioService:
    def __init__(self) -> None:
        self.endereco_repository = EnderecoRepository()
        self.aluno_repository = AlunoRepository()
        self.professor_repository = ProfessorRepository()
        self.usuario_repository = UsuarioRepository()

    async def register_usuario(
        self,
        session: AsyncSession,
        data: UsuarioRegisterRequest,
    ) -> UsuarioRegisterResponse:
        if data.perfil == PerfilUsuario.ALUNO:
            return await self.register_aluno_user(session=session, data=data)

        if data.perfil == PerfilUsuario.PROFESSOR:
            return await self.register_professor_user(session=session, data=data)

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Perfil de usuário inválido.",
        )

    async def register_aluno_user(
        self,
        session: AsyncSession,
        data: UsuarioRegisterRequest | UsuarioCreateAlunoRequest,
    ) -> UsuarioRegisterResponse:
        if data.aluno is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Dados de aluno são obrigatórios para perfil aluno.",
            )

        if data.endereco is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Endereço é obrigatório para cadastro de aluno.",
            )

        usuario_email = validate_or_400(validate_email, data.email)
        validate_or_400(validate_password_strength, data.senha)
        aluno_cpf = validate_or_400(validate_cpf, data.aluno.cpf)
        aluno_email = validate_or_400(validate_email, data.aluno.email or usuario_email)

        try:
            async with session.begin():
                if await self.usuario_repository.exists_by_email(session, usuario_email):
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail="Já existe usuário cadastrado com este e-mail.",
                    )

                if await self.aluno_repository.exists_by_cpf(session, aluno_cpf):
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail="Já existe aluno cadastrado com este CPF.",
                    )

                endereco = Endereco(**data.endereco.model_dump())
                endereco = await self.endereco_repository.create(session, endereco)

                aluno = Aluno(
                    id_endereco=endereco.id,
                    nome=data.aluno.nome,
                    cpf=aluno_cpf,
                    data_nascimento=data.aluno.data_nascimento,
                    email=aluno_email,
                    telefone=data.aluno.telefone,
                )
                aluno = await self.aluno_repository.create(session, aluno)

                usuario = Usuario(
                    id_aluno=aluno.id,
                    id_professor=None,
                    perfil=PerfilUsuario.ALUNO,
                    status=StatusUsuario.ATIVO,
                    email=usuario_email,
                    senha_hash=hash_password(data.senha),
                )
                usuario = await self.usuario_repository.create(session, usuario)

        except IntegrityError as exc:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Já existe um registro com algum dado único informado, como e-mail ou CPF.",
            ) from exc

        return self._to_register_response(usuario)

    async def register_professor_user(
        self,
        session: AsyncSession,
        data: UsuarioRegisterRequest | UsuarioCreateProfessorRequest,
    ) -> UsuarioRegisterResponse:
        if data.professor is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Dados de professor são obrigatórios para perfil professor.",
            )

        usuario_email = validate_or_400(validate_email, data.email)
        validate_or_400(validate_password_strength, data.senha)
        professor_email = validate_or_400(validate_email, data.professor.email or usuario_email)

        try:
            async with session.begin():
                if await self.usuario_repository.exists_by_email(session, usuario_email):
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail="Já existe usuário cadastrado com este e-mail.",
                    )

                if await self.professor_repository.exists_by_email(session, professor_email):
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail="Já existe professor cadastrado com este e-mail.",
                    )

                professor = Professor(
                    nome=data.professor.nome,
                    email=professor_email,
                    telefone=data.professor.telefone,
                )
                professor = await self.professor_repository.create(session, professor)

                usuario = Usuario(
                    id_aluno=None,
                    id_professor=professor.id,
                    perfil=PerfilUsuario.PROFESSOR,
                    status=StatusUsuario.ATIVO,
                    email=usuario_email,
                    senha_hash=hash_password(data.senha),
                )
                usuario = await self.usuario_repository.create(session, usuario)

        except IntegrityError as exc:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Já existe um registro com algum dado único informado, como e-mail.",
            ) from exc

        return self._to_register_response(usuario)

    async def get_usuario_by_email(self, session: AsyncSession, email: str) -> UsuarioRead:
        normalized_email = validate_or_400(validate_email, email)
        usuario = await self.usuario_repository.get_by_email(session, normalized_email)
        if usuario is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuário não encontrado.",
            )
        return self._to_usuario_read(usuario)

    async def get_usuario_by_id(self, session: AsyncSession, id_usuario: int) -> UsuarioRead:
        usuario = await self.usuario_repository.get_by_id(session, id_usuario)
        if usuario is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuário não encontrado.",
            )
        return self._to_usuario_read(usuario)

    def _to_register_response(self, usuario: Usuario) -> UsuarioRegisterResponse:
        return UsuarioRegisterResponse(
            id_usuario=usuario.id,
            perfil=usuario.perfil,
            email=usuario.email,
            id_aluno=usuario.id_aluno,
            id_professor=usuario.id_professor,
            status=usuario.status,
        )

    def _to_usuario_read(self, usuario: Usuario) -> UsuarioRead:
        return UsuarioRead(
            id=usuario.id,
            id_aluno=usuario.id_aluno,
            id_professor=usuario.id_professor,
            perfil=usuario.perfil,
            email=usuario.email,
            status=usuario.status,
        )
