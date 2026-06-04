from datetime import date
from decimal import Decimal

from sqlmodel import SQLModel

from models.avaliacao import TipoAvaliacao


class AvaliacaoCreate(SQLModel):
    id_oferta_disciplina: int
    nome: str
    tipo: TipoAvaliacao
    peso: Decimal
    data: date


class AvaliacaoRead(SQLModel):
    id: int
    id_oferta_disciplina: int
    nome: str
    tipo: TipoAvaliacao
    peso: Decimal
    data: date


class AvaliacaoUpdate(SQLModel):
    id_oferta_disciplina: int | None = None
    nome: str | None = None
    tipo: TipoAvaliacao | None = None
    peso: Decimal | None = None
    data: date | None = None
