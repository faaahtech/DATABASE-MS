from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from dtos.auth_dto import LoginRequest, LoginResponse, RecuperarSenhaRequest, ResetarSenhaRequest
from dtos.usuario_dto import UsuarioRead
from models.usuario import StatusUsuario, Usuario
from repositories.usuario_repository import UsuarioRepository
from services.service_utils import validate_or_400
from utils.security import (
    create_access_token,
    generate_recovery_token,
    hash_password,
    hash_token,
    verify_password,
)
from utils.validators import validate_email, validate_password_strength


class AuthService:
    def __init__(self) -> None:
        self.usuario_repository = UsuarioRepository()

    async def login(self, session: AsyncSession, data: LoginRequest) -> LoginResponse:
        email = validate_or_400(validate_email, data.email)

        usuario = await self.usuario_repository.get_by_email(session, email)
        if usuario is None or not verify_password(data.senha, usuario.senha_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="E-mail ou senha inválidos.",
            )

        if usuario.status != StatusUsuario.ATIVO:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Usuário inativo.",
            )

        access_token = create_access_token(
            {
                "sub": str(usuario.id),
                "id_usuario": usuario.id,
                "email": usuario.email,
                "perfil": usuario.perfil.value,
            }
        )

        return LoginResponse(
            access_token=access_token,
            usuario=self._to_usuario_read(usuario),
        )

    async def request_password_recovery(
        self,
        session: AsyncSession,
        data: RecuperarSenhaRequest,
    ) -> dict[str, str]:
        email = validate_or_400(validate_email, data.email)
        # Resposta genérica para não permitir enumeração de e-mails.
        generic_response = {
            "message": "Se o e-mail existir, um fluxo de recuperação será iniciado."
        }

        recovery_token = generate_recovery_token()
        recovery_token_hash = hash_token(recovery_token)

        try:
            async with session.begin():
                usuario = await self.usuario_repository.get_by_email(session, email)
                if usuario is None:
                    return generic_response

                await self.usuario_repository.update_recovery_token(
                    session=session,
                    usuario=usuario,
                    token_recuperacao=recovery_token_hash,
                )
        except IntegrityError as exc:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Não foi possível gerar token de recuperação.",
            ) from exc

        # Em produção, o token bruto deve ser enviado por e-mail e nunca salvo puro no banco.
        # O service retorna apenas mensagem genérica para não expor token_recuperacao em resposta pública.
        return generic_response

    async def reset_password(
        self,
        session: AsyncSession,
        data: ResetarSenhaRequest,
    ) -> dict[str, str]:
        validate_or_400(validate_password_strength, data.nova_senha)
        token_hash = hash_token(data.token)

        try:
            async with session.begin():
                statement = select(Usuario).where(Usuario.token_recuperacao == token_hash)
                result = await session.exec(statement)
                usuario = result.first()

                if usuario is None:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Token de recuperação inválido ou expirado.",
                    )

                usuario.senha_hash = hash_password(data.nova_senha)
                usuario.token_recuperacao = None
                session.add(usuario)
                await session.flush()
        except IntegrityError as exc:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Não foi possível resetar a senha.",
            ) from exc

        return {"message": "Senha redefinida com sucesso."}

    def _to_usuario_read(self, usuario: Usuario) -> UsuarioRead:
        return UsuarioRead(
            id=usuario.id,
            id_aluno=usuario.id_aluno,
            id_professor=usuario.id_professor,
            perfil=usuario.perfil,
            email=usuario.email,
            status=usuario.status,
        )
