from dtos.aluno_dto import AlunoCreate, AlunoListItem, AlunoRead, AlunoUpdate
from dtos.auth_dto import (
    LoginRequest,
    LoginResponse,
    RecuperarSenhaRequest,
    ResetarSenhaRequest,
    TokenPayload,
)
from dtos.curso_unidade_dto import (
    CursoUnidadeCreate,
    CursoUnidadeListItem,
    CursoUnidadeRead,
)
from dtos.endereco_dto import EnderecoCreate, EnderecoRead
from dtos.nota_dto import NotaCreate, NotaPorAlunoRead, NotaRead
from dtos.presenca_dto import PresencaCreate, PresencaPorAlunoRead, PresencaRead
from dtos.professor_dto import ProfessorCreate, ProfessorRead, ProfessorUpdate
from dtos.usuario_dto import (
    AlunoRegisterData,
    ProfessorRegisterData,
    UsuarioCreateAlunoRequest,
    UsuarioCreateProfessorRequest,
    UsuarioRead,
    UsuarioRegisterRequest,
    UsuarioRegisterResponse,
)
