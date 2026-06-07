from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from dtos.aluno_dto import AlunoCreate, AlunoListItem, AlunoRead
from dtos.llm_academico_dto import (
    AlunoTransferenciaRead,
    MatriculaAtualTransferenciaRead,
    OpcaoTransferenciaHorarioRead,
    OpcoesTransferenciaHorarioRead,
)
from models.aluno import Aluno
from models.curso import Curso
from models.curso_unidade import CursoUnidade, StatusCursoUnidade
from models.matricula_curso import MatriculaCurso, PeriodoMatriculaCurso, StatusMatriculaCurso
from models.unidade import Unidade
from repositories.aluno_repository import AlunoRepository
from repositories.endereco_repository import EnderecoRepository
from repositories.matricula_curso_repository import MatriculaCursoRepository
from services.service_utils import validate_or_400
from utils.validators import validate_cpf, validate_email


class AlunoService:
    def __init__(self) -> None:
        self.aluno_repository = AlunoRepository()
        self.endereco_repository = EnderecoRepository()
        self.matricula_curso_repository = MatriculaCursoRepository()

    async def create_aluno(self, session: AsyncSession, data: AlunoCreate) -> AlunoRead:
        email = validate_or_400(validate_email, data.email)
        cpf = validate_or_400(validate_cpf, data.cpf)

        aluno = Aluno(**{**data.model_dump(), "email": email, "cpf": cpf})

        try:
            async with session.begin():
                endereco = await self.endereco_repository.get_by_id(session, data.id_endereco)
                if endereco is None:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Endereço não encontrado.",
                    )

                if await self.aluno_repository.exists_by_cpf(session, cpf):
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail="Já existe aluno cadastrado com este CPF.",
                    )

                aluno = await self.aluno_repository.create(session, aluno)
        except IntegrityError as exc:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Já existe aluno cadastrado com algum dado único informado.",
            ) from exc

        return self._to_read(aluno)

    async def get_aluno_by_id(self, session: AsyncSession, id_aluno: int) -> AlunoRead:
        aluno = await self.aluno_repository.get_by_id(session, id_aluno)
        if aluno is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Aluno não encontrado.",
            )
        return self._to_read(aluno)

    async def get_aluno_by_ra(self, session: AsyncSession, ra: str) -> AlunoRead:
        aluno = await self.aluno_repository.get_by_ra(session, ra)
        if aluno is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Aluno não encontrado para o RA informado.",
            )
        return self._to_read(aluno)

    async def list_alunos(
        self,
        session: AsyncSession,
        limit: int = 100,
        offset: int = 0,
    ) -> list[AlunoListItem]:
        alunos = await self.aluno_repository.list(session, limit=limit, offset=offset)
        return [self._to_list_item(aluno) for aluno in alunos]

    async def listar_opcoes_transferencia_horario(
        self,
        session: AsyncSession,
        id_aluno: int,
    ) -> OpcoesTransferenciaHorarioRead:
        aluno = await self.aluno_repository.get_by_id(session, id_aluno)
        if aluno is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Aluno não encontrado.")

        matricula_atual = await self.matricula_curso_repository.get_matricula_cursando_by_aluno(
            session=session,
            id_aluno=id_aluno,
        )
        if matricula_atual is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Matrícula ativa do aluno não encontrada.",
            )

        curso_unidade_atual = await session.get(CursoUnidade, matricula_atual.id_curso_unidade)
        if curso_unidade_atual is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="CursoUnidade atual não encontrado.")

        statement = (
            select(CursoUnidade, Curso, Unidade)
            .join(Curso, Curso.id == CursoUnidade.id_curso)
            .join(Unidade, Unidade.id == CursoUnidade.id_unidade)
            .where(
                CursoUnidade.id_curso == curso_unidade_atual.id_curso,
                CursoUnidade.status == StatusCursoUnidade.ATIVO,
            )
        )
        result = await session.exec(statement)
        rows = list(result.all())
        rows.sort(key=lambda row: (row[0].id_unidade != curso_unidade_atual.id_unidade, row[2].nome, row[0].id))

        options: list[OpcaoTransferenciaHorarioRead] = []
        option_id = 1
        for curso_unidade, curso, unidade in rows:
            for periodo in PeriodoMatriculaCurso:
                if curso_unidade.id == matricula_atual.id_curso_unidade and periodo == matricula_atual.periodo:
                    continue
                label_periodo = self._periodo_label(periodo)
                options.append(
                    OpcaoTransferenciaHorarioRead(
                        option_id=option_id,
                        id_curso_unidade=curso_unidade.id,
                        curso=curso.nome,
                        sigla=curso.sigla,
                        unidade=unidade.nome,
                        periodo=periodo,
                        label=f"{curso.sigla} {label_periodo} - {unidade.nome}",
                    )
                )
                option_id += 1

        return OpcoesTransferenciaHorarioRead(
            aluno=AlunoTransferenciaRead(id=aluno.id, nome=aluno.nome),
            matricula_atual=MatriculaAtualTransferenciaRead(
                id=matricula_atual.id,
                id_aluno=matricula_atual.id_aluno,
                id_curso_unidade=matricula_atual.id_curso_unidade,
                ra=matricula_atual.ra,
                semestre_curso=matricula_atual.semestre_curso,
                periodo=matricula_atual.periodo,
                status=matricula_atual.status,
            ),
            options=options,
        )

    def _periodo_label(self, periodo: PeriodoMatriculaCurso) -> str:
        labels = {
            PeriodoMatriculaCurso.MATUTINO: "Manhã",
            PeriodoMatriculaCurso.VESPERTINO: "Tarde",
            PeriodoMatriculaCurso.NOTURNO: "Noite",
        }
        return labels.get(periodo, periodo.value)

    def _to_read(self, aluno: Aluno) -> AlunoRead:
        return AlunoRead(
            id=aluno.id,
            id_endereco=aluno.id_endereco,
            nome=aluno.nome,
            cpf=aluno.cpf,
            data_nascimento=aluno.data_nascimento,
            email=aluno.email,
            telefone=aluno.telefone,
            status=aluno.status,
        )

    def _to_list_item(self, aluno: Aluno) -> AlunoListItem:
        return AlunoListItem(
            id=aluno.id,
            nome=aluno.nome,
            cpf=aluno.cpf,
            email=aluno.email,
            telefone=aluno.telefone,
            status=aluno.status,
        )
