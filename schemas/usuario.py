from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import Column, CheckConstraint, String
from sqlalchemy import Enum as SQLAlchemyEnum
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from schemas.aluno import Aluno
    from schemas.professor import Professor


class StatusUsuario(str, Enum):
    ATIVO = "ativo"
    INATIVO = "inativo"


class PerfilUsuario(str, Enum):
    ALUNO = "aluno"
    PROFESSOR = "professor"


class Usuario(SQLModel, table=True):
    __tablename__ = "usuario"

    __table_args__ = (
        CheckConstraint(
            """
            (
                perfil = 'aluno'
                AND id_aluno IS NOT NULL
                AND id_professor IS NULL
            )
            OR
            (
                perfil = 'professor'
                AND id_professor IS NOT NULL
                AND id_aluno IS NULL
            )
            """,
            name="ck_usuario_perfil_vinculo",
        ),
    )

    id: int | None = Field(default=None, primary_key=True)

    id_aluno: int | None = Field(
        default=None,
        foreign_key="aluno.id",
        unique=True,
        index=True,
    )

    id_professor: int | None = Field(
        default=None,
        foreign_key="professor.id",
        unique=True,
        index=True,
    )

    status: StatusUsuario = Field(
        default=StatusUsuario.ATIVO,
        sa_column=Column(
            SQLAlchemyEnum(
                StatusUsuario,
                name="status_usuario_enum",
                values_callable=lambda enum: [item.value for item in enum],
            ),
            nullable=False,
        ),
    )

    perfil: PerfilUsuario = Field(
        sa_column=Column(
            SQLAlchemyEnum(
                PerfilUsuario,
                name="perfil_usuario_enum",
                values_callable=lambda enum: [item.value for item in enum],
            ),
            nullable=False,
        ),
    )

    email: str = Field(
        sa_column=Column(String(255), unique=True, nullable=False, index=True)
    )

    senha_hash: str = Field(
        sa_column=Column(String(255), nullable=False)
    )

    token_navegacao: str | None = Field(
        default=None,
        sa_column=Column(String(255), nullable=True),
    )

    token_recuperacao: str | None = Field(
        default=None,
        sa_column=Column(String(255), nullable=True),
    )

    aluno: "Aluno | None" = Relationship(back_populates="usuario")
    professor: "Professor | None" = Relationship(back_populates="usuario")
