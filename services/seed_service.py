from datetime import date
from decimal import Decimal

from sqlmodel.ext.asyncio.session import AsyncSession

from dtos.seed_dto import SeedBaseResponse, SeedEntityRead
from models.aluno import Aluno, StatusAluno
from models.aula import Aula
from models.avaliacao import Avaliacao, TipoAvaliacao
from models.curso import Curso, StatusCurso
from models.curso_unidade import (
    CursoUnidade,
    ModalidadeCursoUnidade,
    NivelCursoUnidade,
    StatusCursoUnidade,
)
from models.disciplina import Disciplina, StatusDisciplina
from models.endereco import Endereco
from models.matricula_curso import (
    MatriculaCurso,
    PeriodoMatriculaCurso,
    StatusMatriculaCurso,
)
from models.matricula_disciplina import MatriculaDisciplina, StatusMatriculaDisciplina
from models.matriz_curricular import MatrizCurricular, StatusMatrizCurricular
from models.oferta_disciplina import (
    OfertaDisciplina,
    PeriodoOfertaDisciplina,
    StatusOfertaDisciplina,
)
from models.periodo_letivo import PeriodoLetivo, StatusPeriodoLetivo
from models.professor import Professor, StatusProfessor
from models.unidade import StatusUnidade, Unidade
from models.usuario import PerfilUsuario, StatusUsuario, Usuario
from repositories.aluno_repository import AlunoRepository
from repositories.aula_repository import AulaRepository
from repositories.avaliacao_repository import AvaliacaoRepository
from repositories.curso_repository import CursoRepository
from repositories.curso_unidade_repository import CursoUnidadeRepository
from repositories.disciplina_repository import DisciplinaRepository
from repositories.endereco_repository import EnderecoRepository
from repositories.matricula_curso_repository import MatriculaCursoRepository
from repositories.matricula_disciplina_repository import MatriculaDisciplinaRepository
from repositories.matriz_curricular_repository import MatrizCurricularRepository
from repositories.oferta_disciplina_repository import OfertaDisciplinaRepository
from repositories.periodo_letivo_repository import PeriodoLetivoRepository
from repositories.professor_repository import ProfessorRepository
from repositories.unidade_repository import UnidadeRepository
from repositories.usuario_repository import UsuarioRepository
from utils.security import hash_password


class SeedService:
    """Seed idempotente para criar dados base de demonstração do MVP.

    Este service é focado em desenvolvimento/homologação. Ele cria a cadeia
    acadêmica mínima para testar nota e presença pelo Swagger/Insomnia sem
    inserir registros manualmente no banco.
    """

    DEMO_PROFESSOR_EMAIL = "prof.demo@fatec.sp.gov.br"
    DEMO_ALUNO_EMAIL = "aluno.demo@fatec.sp.gov.br"
    DEMO_ALUNO_CPF = "12345678909"
    DEMO_RA = "2026000001"
    DEMO_OFERTA_CODIGO = "ADS-BD001-2026-1-NOTURNO"

    def __init__(self) -> None:
        self.curso_repository = CursoRepository()
        self.endereco_repository = EnderecoRepository()
        self.unidade_repository = UnidadeRepository()
        self.curso_unidade_repository = CursoUnidadeRepository()
        self.disciplina_repository = DisciplinaRepository()
        self.periodo_repository = PeriodoLetivoRepository()
        self.matriz_repository = MatrizCurricularRepository()
        self.professor_repository = ProfessorRepository()
        self.oferta_repository = OfertaDisciplinaRepository()
        self.aula_repository = AulaRepository()
        self.avaliacao_repository = AvaliacaoRepository()
        self.aluno_repository = AlunoRepository()
        self.usuario_repository = UsuarioRepository()
        self.matricula_curso_repository = MatriculaCursoRepository()
        self.matricula_disciplina_repository = MatriculaDisciplinaRepository()

    async def seed_base(self, session: AsyncSession) -> SeedBaseResponse:
        async with session.begin():
            curso, curso_acao = await self._get_or_create_curso(session)

            unidade_existente = await self.unidade_repository.get_by_nome(session, "Fatec Demo")
            if unidade_existente is not None:
                unidade = unidade_existente
                unidade_acao = "existing"
                endereco = await self.endereco_repository.get_by_id(session, unidade.id_endereco)
                endereco_acao = "existing"
            else:
                endereco, endereco_acao = await self._create_endereco_unidade(session)
                unidade, unidade_acao = await self._get_or_create_unidade(session, endereco.id)

            curso_unidade, curso_unidade_acao = await self._get_or_create_curso_unidade(
                session=session,
                id_curso=curso.id,
                id_unidade=unidade.id,
            )
            periodo, periodo_acao = await self._get_or_create_periodo_letivo(session)

            disciplinas: list[tuple[Disciplina, str]] = []
            for nome, codigo, carga_horaria in [
                ("Banco de Dados", "BD001", 80),
                ("Engenharia de Software", "ES001", 80),
                ("Programação Web", "PW001", 80),
            ]:
                disciplina, acao = await self._get_or_create_disciplina(
                    session=session,
                    nome=nome,
                    codigo=codigo,
                    carga_horaria=carga_horaria,
                )
                disciplinas.append((disciplina, acao))

            matrizes: list[tuple[MatrizCurricular, str]] = []
            for semestre_recomendado, (disciplina, _) in enumerate(disciplinas, start=1):
                matriz, acao = await self._get_or_create_matriz_curricular(
                    session=session,
                    id_curso_unidade=curso_unidade.id,
                    id_disciplina=disciplina.id,
                    semestre_recomendado=semestre_recomendado,
                )
                matrizes.append((matriz, acao))

            matriz_demo = matrizes[0][0]
            professor, professor_acao = await self._get_or_create_professor(session)
            oferta, oferta_acao = await self._get_or_create_oferta_disciplina(
                session=session,
                id_matriz_curricular=matriz_demo.id,
                id_professor=professor.id,
                id_periodo_letivo=periodo.id,
            )
            aula, aula_acao = await self._get_or_create_aula(session, oferta.id)
            avaliacao, avaliacao_acao = await self._get_or_create_avaliacao(session, oferta.id)
            endereco_aluno, endereco_aluno_acao, aluno, aluno_acao = await self._get_or_create_aluno(
                session=session,
            )
            usuario_aluno, usuario_aluno_acao = await self._get_or_create_usuario_aluno(
                session=session,
                id_aluno=aluno.id,
            )
            matricula_curso, matricula_curso_acao = await self._get_or_create_matricula_curso(
                session=session,
                id_aluno=aluno.id,
                id_curso_unidade=curso_unidade.id,
            )
            (
                matricula_disciplina,
                matricula_disciplina_acao,
            ) = await self._get_or_create_matricula_disciplina(
                session=session,
                id_matricula_curso=matricula_curso.id,
                oferta=oferta,
            )

        return SeedBaseResponse(
            mensagem="Seed base executado com sucesso.",
            curso=SeedEntityRead(id=curso.id, acao=curso_acao),
            endereco_unidade=SeedEntityRead(id=endereco.id, acao=endereco_acao),
            unidade=SeedEntityRead(id=unidade.id, acao=unidade_acao),
            curso_unidade=SeedEntityRead(id=curso_unidade.id, acao=curso_unidade_acao),
            periodo_letivo=SeedEntityRead(id=periodo.id, acao=periodo_acao),
            disciplinas=[
                SeedEntityRead(id=disciplina.id, acao=acao)
                for disciplina, acao in disciplinas
            ],
            matrizes_curriculares=[
                SeedEntityRead(id=matriz.id, acao=acao)
                for matriz, acao in matrizes
            ],
            professor=SeedEntityRead(id=professor.id, acao=professor_acao),
            oferta_disciplina=SeedEntityRead(id=oferta.id, acao=oferta_acao),
            aula=SeedEntityRead(id=aula.id, acao=aula_acao),
            avaliacao=SeedEntityRead(id=avaliacao.id, acao=avaliacao_acao),
            endereco_aluno=SeedEntityRead(id=endereco_aluno.id, acao=endereco_aluno_acao),
            aluno=SeedEntityRead(id=aluno.id, acao=aluno_acao),
            usuario_aluno=SeedEntityRead(id=usuario_aluno.id, acao=usuario_aluno_acao),
            matricula_curso=SeedEntityRead(id=matricula_curso.id, acao=matricula_curso_acao),
            matricula_disciplina=SeedEntityRead(
                id=matricula_disciplina.id,
                acao=matricula_disciplina_acao,
            ),
        )

    async def _get_or_create_curso(self, session: AsyncSession) -> tuple[Curso, str]:
        curso = await self.curso_repository.get_by_sigla(session, "ADS")
        if curso is not None:
            return curso, "existing"
        curso = Curso(
            nome="Análise e Desenvolvimento de Sistemas",
            sigla="ADS",
            duracao_semestres=6,
            status=StatusCurso.ATIVO,
        )
        curso = await self.curso_repository.create(session, curso)
        return curso, "created"

    async def _create_endereco_unidade(self, session: AsyncSession) -> tuple[Endereco, str]:
        endereco = Endereco(
            rua="Rua Acadêmica",
            cep="01001000",
            numero="100",
            bairro="Centro",
            estado="SP",
            cidade="São Paulo",
            complemento="Seed de demonstração",
        )
        endereco = await self.endereco_repository.create(session, endereco)
        return endereco, "created"

    async def _get_or_create_unidade(
        self,
        session: AsyncSession,
        id_endereco: int,
    ) -> tuple[Unidade, str]:
        unidade = await self.unidade_repository.get_by_nome(session, "Fatec Demo")
        if unidade is not None:
            return unidade, "existing"
        unidade = Unidade(
            nome="Fatec Demo",
            id_endereco=id_endereco,
            status=StatusUnidade.ATIVA,
        )
        unidade = await self.unidade_repository.create(session, unidade)
        return unidade, "created"

    async def _get_or_create_curso_unidade(
        self,
        session: AsyncSession,
        id_curso: int,
        id_unidade: int,
    ) -> tuple[CursoUnidade, str]:
        curso_unidade = await self.curso_unidade_repository.get_by_curso_and_unidade(
            session=session,
            id_curso=id_curso,
            id_unidade=id_unidade,
            nivel=NivelCursoUnidade.TECNOLOGO,
            modalidade=ModalidadeCursoUnidade.PRESENCIAL,
        )
        if curso_unidade is not None:
            return curso_unidade, "existing"
        curso_unidade = CursoUnidade(
            id_curso=id_curso,
            id_unidade=id_unidade,
            status=StatusCursoUnidade.ATIVO,
            nivel=NivelCursoUnidade.TECNOLOGO,
            modalidade=ModalidadeCursoUnidade.PRESENCIAL,
        )
        curso_unidade = await self.curso_unidade_repository.create(session, curso_unidade)
        return curso_unidade, "created"

    async def _get_or_create_periodo_letivo(self, session: AsyncSession) -> tuple[PeriodoLetivo, str]:
        periodo = await self.periodo_repository.get_by_ano_semestre(session, ano=2026, semestre=1)
        if periodo is not None:
            return periodo, "existing"
        ativos = await self.periodo_repository.list_ativos(session)
        for ativo in ativos:
            ativo.status = StatusPeriodoLetivo.ENCERRADO
            await self.periodo_repository.update(session, ativo)
        periodo = PeriodoLetivo(
            ano=2026,
            semestre=1,
            data_inicio=date(2026, 2, 1),
            data_fim=date(2026, 6, 30),
            status=StatusPeriodoLetivo.ATIVO,
        )
        periodo = await self.periodo_repository.create(session, periodo)
        return periodo, "created"

    async def _get_or_create_disciplina(
        self,
        session: AsyncSession,
        nome: str,
        codigo: str,
        carga_horaria: int,
    ) -> tuple[Disciplina, str]:
        disciplina = await self.disciplina_repository.get_by_codigo(session, codigo)
        if disciplina is not None:
            return disciplina, "existing"
        disciplina = Disciplina(
            nome=nome,
            codigo=codigo,
            carga_horaria=carga_horaria,
            status=StatusDisciplina.ATIVO,
        )
        disciplina = await self.disciplina_repository.create(session, disciplina)
        return disciplina, "created"

    async def _get_or_create_matriz_curricular(
        self,
        session: AsyncSession,
        id_curso_unidade: int,
        id_disciplina: int,
        semestre_recomendado: int,
    ) -> tuple[MatrizCurricular, str]:
        matriz = await self.matriz_repository.get_by_curso_unidade_and_disciplina(
            session=session,
            id_curso_unidade=id_curso_unidade,
            id_disciplina=id_disciplina,
        )
        if matriz is not None:
            return matriz, "existing"
        matriz = MatrizCurricular(
            id_curso_unidade=id_curso_unidade,
            id_disciplina=id_disciplina,
            semestre_recomendado=semestre_recomendado,
            obrigatoria=True,
            status=StatusMatrizCurricular.ATIVO,
        )
        matriz = await self.matriz_repository.create(session, matriz)
        return matriz, "created"

    async def _get_or_create_professor(self, session: AsyncSession) -> tuple[Professor, str]:
        professor = await self.professor_repository.get_by_email(session, self.DEMO_PROFESSOR_EMAIL)
        if professor is not None:
            return professor, "existing"
        professor = Professor(
            nome="Professor Demo",
            email=self.DEMO_PROFESSOR_EMAIL,
            telefone="11999990000",
            status=StatusProfessor.ATIVO,
        )
        professor = await self.professor_repository.create(session, professor)
        return professor, "created"

    async def _get_or_create_oferta_disciplina(
        self,
        session: AsyncSession,
        id_matriz_curricular: int,
        id_professor: int,
        id_periodo_letivo: int,
    ) -> tuple[OfertaDisciplina, str]:
        oferta = await self.oferta_repository.get_by_codigo_oferta(
            session=session,
            codigo_oferta=self.DEMO_OFERTA_CODIGO,
        )
        if oferta is not None:
            return oferta, "existing"
        oferta = OfertaDisciplina(
            id_matriz_curricular=id_matriz_curricular,
            id_professor=id_professor,
            id_periodo_letivo=id_periodo_letivo,
            codigo_oferta=self.DEMO_OFERTA_CODIGO,
            vagas_total=40,
            vagas_disponiveis=40,
            periodo=PeriodoOfertaDisciplina.NOTURNO,
            status=StatusOfertaDisciplina.ATIVO,
        )
        oferta = await self.oferta_repository.create(session, oferta)
        return oferta, "created"

    async def _get_or_create_aula(
        self,
        session: AsyncSession,
        id_oferta_disciplina: int,
    ) -> tuple[Aula, str]:
        aula = await self.aula_repository.get_by_oferta_data_assunto(
            session=session,
            id_oferta_disciplina=id_oferta_disciplina,
            data=date(2026, 3, 10),
            assunto="Introdução ao Banco de Dados",
        )
        if aula is not None:
            return aula, "existing"
        aula = Aula(
            id_oferta_disciplina=id_oferta_disciplina,
            data=date(2026, 3, 10),
            assunto="Introdução ao Banco de Dados",
            descricao="Aula de demonstração criada pelo seed do MVP.",
        )
        aula = await self.aula_repository.create(session, aula)
        return aula, "created"

    async def _get_or_create_avaliacao(
        self,
        session: AsyncSession,
        id_oferta_disciplina: int,
    ) -> tuple[Avaliacao, str]:
        avaliacao = await self.avaliacao_repository.get_by_oferta_and_nome(
            session=session,
            id_oferta_disciplina=id_oferta_disciplina,
            nome="Prova Demo P1",
        )
        if avaliacao is not None:
            return avaliacao, "existing"
        avaliacao = Avaliacao(
            id_oferta_disciplina=id_oferta_disciplina,
            nome="Prova Demo P1",
            tipo=TipoAvaliacao.PROVA,
            peso=Decimal("1.00"),
            data=date(2026, 4, 15),
        )
        avaliacao = await self.avaliacao_repository.create(session, avaliacao)
        return avaliacao, "created"

    async def _get_or_create_aluno(
        self,
        session: AsyncSession,
    ) -> tuple[Endereco, str, Aluno, str]:
        aluno = await self.aluno_repository.get_by_cpf(session, self.DEMO_ALUNO_CPF)
        if aluno is not None:
            endereco = await self.endereco_repository.get_by_id(session, aluno.id_endereco)
            return endereco, "existing", aluno, "existing"

        endereco = Endereco(
            rua="Rua do Aluno Demo",
            cep="04795000",
            numero="200",
            bairro="Zona Sul",
            estado="SP",
            cidade="São Paulo",
            complemento="Endereço de demonstração do aluno",
        )
        endereco = await self.endereco_repository.create(session, endereco)
        aluno = Aluno(
            id_endereco=endereco.id,
            nome="Aluno Demo",
            cpf=self.DEMO_ALUNO_CPF,
            data_nascimento=date(2000, 1, 15),
            telefone="11988880000",
            email=self.DEMO_ALUNO_EMAIL,
            status=StatusAluno.ATIVO,
        )
        aluno = await self.aluno_repository.create(session, aluno)
        return endereco, "created", aluno, "created"

    async def _get_or_create_usuario_aluno(
        self,
        session: AsyncSession,
        id_aluno: int,
    ) -> tuple[Usuario, str]:
        usuario = await self.usuario_repository.get_by_email(session, self.DEMO_ALUNO_EMAIL)
        if usuario is not None:
            return usuario, "existing"
        usuario = Usuario(
            id_aluno=id_aluno,
            id_professor=None,
            perfil=PerfilUsuario.ALUNO,
            status=StatusUsuario.ATIVO,
            email=self.DEMO_ALUNO_EMAIL,
            senha_hash=hash_password("Aluno@123456"),
        )
        usuario = await self.usuario_repository.create(session, usuario)
        return usuario, "created"

    async def _get_or_create_matricula_curso(
        self,
        session: AsyncSession,
        id_aluno: int,
        id_curso_unidade: int,
    ) -> tuple[MatriculaCurso, str]:
        matricula = await self.matricula_curso_repository.get_by_ra(session, self.DEMO_RA)
        if matricula is not None:
            return matricula, "existing"
        matricula = MatriculaCurso(
            id_aluno=id_aluno,
            id_curso_unidade=id_curso_unidade,
            ra=self.DEMO_RA,
            semestre_curso=1,
            periodo=PeriodoMatriculaCurso.NOTURNO,
            status=StatusMatriculaCurso.CURSANDO,
            ano_ingresso=2026,
            semestre_ingresso=1,
        )
        matricula = await self.matricula_curso_repository.create(session, matricula)
        return matricula, "created"

    async def _get_or_create_matricula_disciplina(
        self,
        session: AsyncSession,
        id_matricula_curso: int,
        oferta: OfertaDisciplina,
    ) -> tuple[MatriculaDisciplina, str]:
        matricula = await self.matricula_disciplina_repository.get_by_matricula_curso_and_oferta(
            session=session,
            id_matricula_curso=id_matricula_curso,
            id_oferta_disciplina=oferta.id,
        )
        if matricula is not None:
            return matricula, "existing"

        if oferta.vagas_disponiveis <= 0:
            raise ValueError("Oferta de disciplina demo sem vagas disponíveis para matrícula.")

        matricula = MatriculaDisciplina(
            id_matricula_curso=id_matricula_curso,
            id_oferta_disciplina=oferta.id,
            status=StatusMatriculaDisciplina.CURSANDO,
        )
        matricula = await self.matricula_disciplina_repository.create(session, matricula)
        oferta.vagas_disponiveis -= 1
        await self.oferta_repository.update(session, oferta)
        return matricula, "created"
