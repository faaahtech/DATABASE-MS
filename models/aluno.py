from datetime import date
from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import Column, Date, String
from sqlalchemy import Enum as SQLAlchemyEnum
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from schemas.conversa import Conversa
    from schemas.documento import Documento
    from schemas.endereco import Endereco
    from schemas.matricula_curso import MatriculaCurso
    from schemas.solicitacao_academica import SolicitacaoAcademica
    from schemas.usuario import Usuario


class StatusAluno(str, Enum):
    ATIVO = "ativo"
    INATIVO = "inativo"


class Aluno(SQLModel, table=True):
    __tablename__ = "aluno"

    id: int | None = Field(default=None, primary_key=True)

    id_endereco: int = Field(
        foreign_key="endereco.id",
        nullable=False,
        index=True,
    )

    nome: str = Field(
        sa_column=Column(String(255), nullable=False, index=True)
    )

    cpf: str = Field(
        sa_column=Column(String(11), unique=True, nullable=False, index=True)
    )

    data_nascimento: date = Field(
        sa_column=Column(Date, nullable=False)
    )

    telefone: str | None = Field(
        default=None,
        sa_column=Column(String(20), nullable=True),
    )

    email: str = Field(
        sa_column=Column(String(255), unique=True, nullable=False, index=True)
    )

    status: StatusAluno = Field(
        default=StatusAluno.ATIVO,
        sa_column=Column(
            SQLAlchemyEnum(
                StatusAluno,
                name="status_aluno_enum",
                values_callable=lambda enum: [item.value for item in enum],
            ),
            nullable=False,
        ),
    )

    endereco: "Endereco | None" = Relationship(back_populates="alunos")
    usuario: "Usuario | None" = Relationship(back_populates="aluno")
    matriculas_curso: list["MatriculaCurso"] = Relationship(back_populates="aluno")
    conversas: list["Conversa"] = Relationship(back_populates="aluno")
    solicitacoes_academicas: list["SolicitacaoAcademica"] = Relationship(back_populates="aluno")
    documentos: list["Documento"] = Relationship(back_populates="aluno")
