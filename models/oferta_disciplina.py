from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import Column, CheckConstraint, Integer, String
from sqlalchemy import Enum as SQLAlchemyEnum
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from schemas.aula import Aula
    from schemas.avaliacao import Avaliacao
    from schemas.horario_aula import HorarioAula
    from schemas.matriz_curricular import MatrizCurricular
    from schemas.matricula_disciplina import MatriculaDisciplina
    from schemas.periodo_letivo import PeriodoLetivo
    from schemas.professor import Professor


class PeriodoOfertaDisciplina(str, Enum):
    MATUTINO = "matutino"
    VESPERTINO = "vespertino"
    NOTURNO = "noturno"


class StatusOfertaDisciplina(str, Enum):
    ATIVO = "ativo"
    ENCERRADA = "encerrada"
    PLANEJADA = "planejada"
    CANCELADA = "cancelada"


class OfertaDisciplina(SQLModel, table=True):
    __tablename__ = "oferta_disciplina"

    __table_args__ = (
        CheckConstraint(
            "vagas_total >= 0",
            name="ck_oferta_disciplina_vagas_total",
        ),
        CheckConstraint(
            "vagas_disponiveis >= 0 AND vagas_disponiveis <= vagas_total",
            name="ck_oferta_disciplina_vagas_disponiveis",
        ),
    )

    id: int | None = Field(default=None, primary_key=True)

    id_matriz_curricular: int = Field(
        foreign_key="matriz_curricular.id",
        nullable=False,
        index=True,
    )

    id_professor: int = Field(
        foreign_key="professor.id",
        nullable=False,
        index=True,
    )

    id_periodo_letivo: int = Field(
        foreign_key="periodo_letivo.id",
        nullable=False,
        index=True,
    )

    codigo_oferta: str = Field(
        sa_column=Column(String(50), nullable=False, index=True)
    )

    vagas_total: int = Field(
        sa_column=Column(Integer, nullable=False)
    )

    vagas_disponiveis: int = Field(
        sa_column=Column(Integer, nullable=False)
    )

    periodo: PeriodoOfertaDisciplina = Field(
        sa_column=Column(
            SQLAlchemyEnum(
                PeriodoOfertaDisciplina,
                name="periodo_oferta_disciplina_enum",
                values_callable=lambda enum: [item.value for item in enum],
            ),
            nullable=False,
        ),
    )

    status: StatusOfertaDisciplina = Field(
        default=StatusOfertaDisciplina.PLANEJADA,
        sa_column=Column(
            SQLAlchemyEnum(
                StatusOfertaDisciplina,
                name="status_oferta_disciplina_enum",
                values_callable=lambda enum: [item.value for item in enum],
            ),
            nullable=False,
        ),
    )

    matriz_curricular: "MatrizCurricular | None" = Relationship(back_populates="ofertas_disciplina")
    professor: "Professor | None" = Relationship(back_populates="ofertas_disciplina")
    periodo_letivo: "PeriodoLetivo | None" = Relationship(back_populates="ofertas_disciplina")
    horarios_aula: list["HorarioAula"] = Relationship(back_populates="oferta_disciplina")
    aulas: list["Aula"] = Relationship(back_populates="oferta_disciplina")
    matriculas_disciplina: list["MatriculaDisciplina"] = Relationship(back_populates="oferta_disciplina")
    avaliacoes: list["Avaliacao"] = Relationship(back_populates="oferta_disciplina")
