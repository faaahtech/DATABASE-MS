# Compatibilidade com imports antigos.
# Os DTOs oficiais da FASE 1 ficam em dtos/usuario_dto.py e dtos/endereco_dto.py.

from dtos.endereco_dto import EnderecoCreate, EnderecoRead
from dtos.usuario_dto import (
    AlunoRegisterData,
    ProfessorRegisterData,
    UsuarioCreateAlunoRequest,
    UsuarioCreateProfessorRequest,
    UsuarioRead,
    UsuarioRegisterRequest,
    UsuarioRegisterResponse,
)

__all__ = [
    "EnderecoCreate",
    "EnderecoRead",
    "AlunoRegisterData",
    "ProfessorRegisterData",
    "UsuarioCreateAlunoRequest",
    "UsuarioCreateProfessorRequest",
    "UsuarioRead",
    "UsuarioRegisterRequest",
    "UsuarioRegisterResponse",
]
