from datetime import datetime

from sqlmodel import SQLModel

from models.historico_solicitacao import StatusHistoricoSolicitacao
from models.solicitacao_academica import (
    OrigemSolicitacaoAcademica,
    StatusSolicitacaoAcademica,
    TipoSolicitacaoAcademica,
)


class SolicitacaoAcademicaCreate(SQLModel):
    id_aluno: int
    id_matricula_curso: int | None = None
    tipo: TipoSolicitacaoAcademica
    origem: OrigemSolicitacaoAcademica = OrigemSolicitacaoAcademica.CHATBOT
    observacao: str | None = None


class SolicitacaoAcademicaRead(SQLModel):
    id: int
    id_aluno: int
    id_matricula_curso: int | None = None
    tipo: TipoSolicitacaoAcademica
    protocolo: str
    status: StatusSolicitacaoAcademica
    origem: OrigemSolicitacaoAcademica
    criado_em: datetime
    atualizado_em: datetime | None = None
    observacao: str | None = None


class SolicitacaoAcademicaStatusUpdate(SQLModel):
    status: StatusSolicitacaoAcademica
    observacao: str | None = None


class HistoricoSolicitacaoRead(SQLModel):
    id: int
    id_solicitacao_academica: int
    status_anterior: StatusHistoricoSolicitacao | None = None
    status_novo: StatusHistoricoSolicitacao
    observacao: str | None = None
    criado_em: datetime
