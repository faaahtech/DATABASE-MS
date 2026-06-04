from enum import Enum
from typing import Optional, TYPE_CHECKING

from sqlalchemy import Column, String
from sqlalchemy import Enum as SQLAlchemyEnum
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from models.oferta_disciplina import OfertaDisciplina
    from models.usuario import Usuario


class StatusProfessor(str, Enum):
    ATIVO = "ativo"
    INATIVO = "inativo"


class Professor(SQLModel, table=True):
    __tablename__ = "professor"

    id: int | None = Field(default=None, primary_key=True)

    nome: str = Field(
        sa_column=Column(String(255), nullable=False, index=True)
    )

    email: str = Field(
        sa_column=Column(String(255), unique=True, nullable=False, index=True)
    )

    telefone: str | None = Field(
        default=None,
        sa_column=Column(String(20), nullable=True),
    )

    status: StatusProfessor = Field(
        default=StatusProfessor.ATIVO,
        sa_column=Column(
            SQLAlchemyEnum(
                StatusProfessor,
                name="status_professor_enum",
                values_callable=lambda enum: [item.value for item in enum],
            ),
            nullable=False,
        ),
    )

    usuario: Optional["Usuario"] = Relationship(back_populates="professor")
    ofertas_disciplina: list["OfertaDisciplina"] = Relationship(back_populates="professor")
