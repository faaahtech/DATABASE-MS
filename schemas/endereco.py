from typing import TYPE_CHECKING

from sqlalchemy import Column, String
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from schemas.aluno import Aluno
    from schemas.unidade import Unidade


class Endereco(SQLModel, table=True):
    __tablename__ = "endereco"

    id: int | None = Field(default=None, primary_key=True)

    rua: str = Field(
        sa_column=Column(String(255), nullable=False)
    )

    cep: str = Field(
        sa_column=Column(String(8), nullable=False, index=True)
    )

    numero: str = Field(
        sa_column=Column(String(20), nullable=False)
    )

    bairro: str = Field(
        sa_column=Column(String(120), nullable=False)
    )

    estado: str = Field(
        sa_column=Column(String(2), nullable=False)
    )

    cidade: str = Field(
        sa_column=Column(String(120), nullable=False)
    )

    complemento: str | None = Field(
        default=None,
        sa_column=Column(String(255), nullable=True),
    )

    alunos: list["Aluno"] = Relationship(back_populates="endereco")
    unidades: list["Unidade"] = Relationship(back_populates="endereco")
