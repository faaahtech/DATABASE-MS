from sqlmodel import SQLModel

from dtos.endereco_dto import EnderecoCreate, EnderecoRead
from models.unidade import StatusUnidade


class UnidadeCreate(SQLModel):
    nome: str
    id_endereco: int | None = None
    endereco: EnderecoCreate | None = None
    status: StatusUnidade = StatusUnidade.ATIVA


class UnidadeRead(SQLModel):
    id: int
    nome: str
    id_endereco: int
    status: StatusUnidade
    endereco: EnderecoRead | None = None


class UnidadeUpdate(SQLModel):
    nome: str | None = None
    status: StatusUnidade | None = None
