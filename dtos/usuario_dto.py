from datetime import date

from sqlmodel import SQLModel

from dtos.endereco_dto import EnderecoCreate
from models.usuario import PerfilUsuario, StatusUsuario


class AlunoRegisterData(SQLModel):
    nome: str
    cpf: str
    data_nascimento: date
    telefone: str | None = None
    # O e-mail do aluno pode ser omitido para reutilizar o e-mail do usuário.
    # O service deve decidir essa regra de negócio na FASE 4.
    email: str | None = None


class ProfessorRegisterData(SQLModel):
    nome: str
    telefone: str | None = None
    # O model Professor exige e-mail. Se omitido, o service pode reutilizar o e-mail do usuário.
    email: str | None = None


class UsuarioRegisterRequest(SQLModel):
    perfil: PerfilUsuario
    email: str
    senha: str
    endereco: EnderecoCreate | None = None
    aluno: AlunoRegisterData | None = None
    professor: ProfessorRegisterData | None = None


class UsuarioCreateAlunoRequest(SQLModel):
    perfil: PerfilUsuario = PerfilUsuario.ALUNO
    email: str
    senha: str
    endereco: EnderecoCreate
    aluno: AlunoRegisterData


class UsuarioCreateProfessorRequest(SQLModel):
    perfil: PerfilUsuario = PerfilUsuario.PROFESSOR
    email: str
    senha: str
    professor: ProfessorRegisterData


class UsuarioRegisterResponse(SQLModel):
    id_usuario: int
    perfil: PerfilUsuario
    email: str
    id_aluno: int | None = None
    id_professor: int | None = None
    status: StatusUsuario


class UsuarioRead(SQLModel):
    id: int
    id_aluno: int | None = None
    id_professor: int | None = None
    perfil: PerfilUsuario
    email: str
    status: StatusUsuario
