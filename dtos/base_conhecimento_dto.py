from datetime import datetime

from sqlmodel import SQLModel

from models.base_conhecimento import (
    CategoriaBaseConhecimento,
    StatusBaseConhecimento,
)


class BaseConhecimentoCreate(SQLModel):
    titulo: str
    categoria: CategoriaBaseConhecimento
    pergunta_base: str | None = None
    resposta: str
    tags: list[str] | None = None
    status: StatusBaseConhecimento = StatusBaseConhecimento.ATIVO


class BaseConhecimentoRead(SQLModel):
    id: int
    titulo: str
    categoria: CategoriaBaseConhecimento
    pergunta_base: str | None = None
    resposta: str
    tags: list[str] | None = None
    status: StatusBaseConhecimento
    atualizado_em: datetime


class BaseConhecimentoUpdate(SQLModel):
    titulo: str | None = None
    categoria: CategoriaBaseConhecimento | None = None
    pergunta_base: str | None = None
    resposta: str | None = None
    tags: list[str] | None = None
    status: StatusBaseConhecimento | None = None
