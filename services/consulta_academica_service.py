from fastapi import HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession

from dtos.consulta_dto import (
    DisciplinaCursoUnidadeRead,
    MatriculaCursoRead,
    OfertaDisciplinaRead,
    PeriodoLetivoAtivoRead,
    ResumoAlunoRead,
)
from models.aluno import Aluno
from models.disciplina import Disciplina
from models.matricula_curso import MatriculaCurso
from models.oferta_disciplina import OfertaDisciplina
from models.periodo_letivo import PeriodoLetivo
from repositories.aluno_repository import AlunoRepository
from repositories.curso_unidade_repository import CursoUnidadeRepository
from repositories.disciplina_repository import DisciplinaRepository
from repositories.oferta_disciplina_repository import OfertaDisciplinaRepository
from repositories.periodo_letivo_repository import PeriodoLetivoRepository
from services.nota_service import NotaService
from services.presenca_service import PresencaService


class ConsultaAcademicaService:
    def __init__(self) -> None:
        self.aluno_repository = AlunoRepository()
        self.curso_unidade_repository = CursoUnidadeRepository()
        self.disciplina_repository = DisciplinaRepository()
        self.periodo_letivo_repository = PeriodoLetivoRepository()
        self.oferta_disciplina_repository = OfertaDisciplinaRepository()
        self.nota_service = NotaService()
        self.presenca_service = PresencaService()

    async def consultar_disciplinas_por_curso_unidade(
        self,
        session: AsyncSession,
        id_curso_unidade: int,
        limit: int = 100,
        offset: int = 0,
    ) -> list[DisciplinaCursoUnidadeRead]:
        curso_unidade = await self.curso_unidade_repository.get_by_id(session, id_curso_unidade)
        if curso_unidade is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Curso_unidade não encontrado.",
            )

        disciplinas = await self.disciplina_repository.list_by_curso_unidade_enriched(
            session=session,
            id_curso_unidade=id_curso_unidade,
            limit=limit,
            offset=offset,
        )
        return [self._to_disciplina_curso_unidade_read_from_row(row) for row in disciplinas]

    async def consultar_periodo_letivo_ativo(
        self,
        session: AsyncSession,
    ) -> PeriodoLetivoAtivoRead:
        periodo_letivo = await self.periodo_letivo_repository.get_ativo(session)
        if periodo_letivo is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Nenhum período letivo ativo encontrado.",
            )
        return self._to_periodo_letivo_ativo_read(periodo_letivo)

    async def consultar_ofertas_por_periodo(
        self,
        session: AsyncSession,
        id_periodo_letivo: int,
        limit: int = 100,
        offset: int = 0,
    ) -> list[OfertaDisciplinaRead]:
        periodo_letivo = await self.periodo_letivo_repository.get_by_id(session, id_periodo_letivo)
        if periodo_letivo is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Período letivo não encontrado.",
            )

        ofertas = await self.oferta_disciplina_repository.list_by_periodo_letivo_enriched(
            session=session,
            id_periodo_letivo=id_periodo_letivo,
            limit=limit,
            offset=offset,
        )
        return [self._to_oferta_disciplina_read_from_row(row) for row in ofertas]

    async def consultar_resumo_aluno(
        self,
        session: AsyncSession,
        id_aluno: int,
    ) -> ResumoAlunoRead:
        aluno = await self.aluno_repository.get_by_id(session, id_aluno)
        if aluno is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Aluno não encontrado.",
            )

        # Evita lazy loading assíncrono: consulta as matrículas explicitamente.
        from sqlmodel import select

        statement = select(MatriculaCurso).where(MatriculaCurso.id_aluno == id_aluno)
        result = await session.exec(statement)
        matriculas = list(result.all())

        return ResumoAlunoRead(
            id_aluno=aluno.id,
            nome=aluno.nome,
            email=aluno.email,
            cpf=aluno.cpf,
            matriculas=[self._to_matricula_curso_read(matricula) for matricula in matriculas],
        )


    async def consultar_notas_por_aluno(
        self,
        session: AsyncSession,
        id_aluno: int,
        limit: int = 100,
        offset: int = 0,
    ):
        return await self.nota_service.consultar_notas_por_aluno(
            session=session,
            id_aluno=id_aluno,
            limit=limit,
            offset=offset,
        )

    async def consultar_presencas_por_aluno(
        self,
        session: AsyncSession,
        id_aluno: int,
        limit: int = 100,
        offset: int = 0,
    ):
        return await self.presenca_service.consultar_presencas_por_aluno(
            session=session,
            id_aluno=id_aluno,
            limit=limit,
            offset=offset,
        )

    def _to_disciplina_curso_unidade_read(
        self,
        disciplina: Disciplina,
    ) -> DisciplinaCursoUnidadeRead:
        return DisciplinaCursoUnidadeRead(
            id_disciplina=disciplina.id,
            nome=disciplina.nome,
            codigo=disciplina.codigo,
            carga_horaria=disciplina.carga_horaria,
            status=disciplina.status,
        )

    def _to_disciplina_curso_unidade_read_from_row(self, row) -> DisciplinaCursoUnidadeRead:
        (
            id_disciplina,
            nome,
            codigo,
            carga_horaria,
            disciplina_status,
            id_matriz_curricular,
            semestre_recomendado,
            obrigatoria,
        ) = row
        return DisciplinaCursoUnidadeRead(
            id_disciplina=id_disciplina,
            nome=nome,
            codigo=codigo,
            carga_horaria=carga_horaria,
            status=disciplina_status,
            id_matriz_curricular=id_matriz_curricular,
            semestre_recomendado=semestre_recomendado,
            obrigatoria=obrigatoria,
        )

    def _to_periodo_letivo_ativo_read(
        self,
        periodo_letivo: PeriodoLetivo,
    ) -> PeriodoLetivoAtivoRead:
        return PeriodoLetivoAtivoRead(
            id=periodo_letivo.id,
            ano=periodo_letivo.ano,
            semestre=periodo_letivo.semestre,
            data_inicio=periodo_letivo.data_inicio,
            data_fim=periodo_letivo.data_fim,
            status=periodo_letivo.status,
        )

    def _to_oferta_disciplina_read(self, oferta: OfertaDisciplina) -> OfertaDisciplinaRead:
        return OfertaDisciplinaRead(
            id=oferta.id,
            id_matriz_curricular=oferta.id_matriz_curricular,
            id_professor=oferta.id_professor,
            id_periodo_letivo=oferta.id_periodo_letivo,
            codigo_oferta=oferta.codigo_oferta,
            vagas_total=oferta.vagas_total,
            vagas_disponiveis=oferta.vagas_disponiveis,
            periodo=oferta.periodo,
            status=oferta.status,
        )

    def _to_oferta_disciplina_read_from_row(self, row) -> OfertaDisciplinaRead:
        (
            id_oferta,
            id_matriz_curricular,
            id_professor,
            id_periodo_letivo,
            codigo_oferta,
            vagas_total,
            vagas_disponiveis,
            periodo,
            oferta_status,
            disciplina_nome,
            disciplina_codigo,
            professor_nome,
        ) = row
        return OfertaDisciplinaRead(
            id=id_oferta,
            id_matriz_curricular=id_matriz_curricular,
            id_professor=id_professor,
            id_periodo_letivo=id_periodo_letivo,
            codigo_oferta=codigo_oferta,
            vagas_total=vagas_total,
            vagas_disponiveis=vagas_disponiveis,
            periodo=periodo,
            status=oferta_status,
            disciplina_nome=disciplina_nome,
            disciplina_codigo=disciplina_codigo,
            professor_nome=professor_nome,
        )

    def _to_matricula_curso_read(self, matricula: MatriculaCurso) -> MatriculaCursoRead:
        return MatriculaCursoRead(
            id=matricula.id,
            id_aluno=matricula.id_aluno,
            id_curso_unidade=matricula.id_curso_unidade,
            ra=matricula.ra,
            semestre_curso=matricula.semestre_curso,
            periodo=matricula.periodo,
            status=matricula.status,
            ano_ingresso=matricula.ano_ingresso,
            semestre_ingresso=matricula.semestre_ingresso,
        )
