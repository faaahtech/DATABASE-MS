from datetime import datetime

from sqlmodel import SQLModel

from dtos.usuario_dto import UsuarioRead
from models.usuario import PerfilUsuario


class LoginRequest(SQLModel):
    email: str
    senha: str


class TokenPayload(SQLModel):
    sub: str | None = None
    id_usuario: int | None = None
    perfil: PerfilUsuario | None = None
    email: str | None = None
    exp: datetime | int | None = None


class LoginResponse(SQLModel):
    access_token: str
    token_type: str = "bearer"
    usuario: UsuarioRead


class RecuperarSenhaRequest(SQLModel):
    email: str


class ResetarSenhaRequest(SQLModel):
    token: str
    nova_senha: str
