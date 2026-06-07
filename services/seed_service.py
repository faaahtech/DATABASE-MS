from datetime import date, time
from decimal import Decimal

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from dtos.seed_dto import SeedBaseResponse, SeedEntityRead
from models.aluno import Aluno, StatusAluno
from models.aula import Aula
from models.avaliacao import Avaliacao, TipoAvaliacao
from models.base_conhecimento import (
    BaseConhecimento,
    CategoriaBaseConhecimento,
    StatusBaseConhecimento,
)
from models.calendario_academico import (
    CalendarioAcademico,
    StatusCalendarioAcademico,
    TipoCalendarioAcademico,
)
from models.curso import Curso, StatusCurso
from models.curso_unidade import (
    CursoUnidade,
    ModalidadeCursoUnidade,
    NivelCursoUnidade,
    StatusCursoUnidade,
)
from models.disciplina import Disciplina, StatusDisciplina
from models.endereco import Endereco
from models.horario_aula import DiaSemana, HorarioAula
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
    acadêmica mínima para testar calendário acadêmico, grade de aulas, matrícula,
    nota e presença pelo Swagger/Insomnia sem inserir registros manualmente.
    """

    DEMO_PROFESSOR_EMAIL = "prof.demo@fatec.sp.gov.br"
    DEMO_ALUNO_EMAIL = "aluno.demo@fatec.sp.gov.br"
    DEMO_ALUNO_CPF = "12345678909"
    DEMO_RA = "2026000001"

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
            curso_ads, curso_ads_acao = await self._get_or_create_curso(
                session=session,
                nome="Análise e Desenvolvimento de Sistemas",
                sigla="ADS",
                duracao_semestres=6,
            )
            curso_logistica, curso_logistica_acao = await self._get_or_create_curso(
                session=session,
                nome="Logística",
                sigla="LOG",
                duracao_semestres=6,
            )

            unidade_existente = await self.unidade_repository.get_by_nome(session, "Fatec Demo")
            if unidade_existente is not None:
                unidade = unidade_existente
                unidade_acao = "existing"
                endereco = await self.endereco_repository.get_by_id(session, unidade.id_endereco)
                endereco_acao = "existing"
            else:
                endereco, endereco_acao = await self._create_endereco_unidade(session)
                unidade, unidade_acao = await self._get_or_create_unidade(session, endereco.id)

            curso_unidade_ads, curso_unidade_ads_acao = await self._get_or_create_curso_unidade(
                session=session,
                id_curso=curso_ads.id,
                id_unidade=unidade.id,
            )
            curso_unidade_logistica, _ = await self._get_or_create_curso_unidade(
                session=session,
                id_curso=curso_logistica.id,
                id_unidade=unidade.id,
            )

            periodo, periodo_acao = await self._get_or_create_periodo_letivo(session)
            professor, professor_acao = await self._get_or_create_professor(session)

            calendario_acoes = await self._seed_calendario_academico_2026(
                session=session,
                id_unidade=unidade.id,
            )
            base_conhecimento_estagio_acoes = await self._seed_base_conhecimento_estagio_demo(
                session=session,
            )

            ads_disciplinas = await self._seed_disciplinas_e_matriz(
                session=session,
                id_curso_unidade=curso_unidade_ads.id,
                disciplinas=[
                    ("Banco de Dados", "BD001", 80, 1),
                    ("Engenharia de Software", "ES001", 80, 1),
                    ("Programação Web", "PW001", 80, 1),
                ],
            )

            logistica_disciplinas = await self._seed_disciplinas_e_matriz(
                session=session,
                id_curso_unidade=curso_unidade_logistica.id,
                disciplinas=[
                    ("Fundamentos de Logística", "LOG001", 80, 1),
                    ("Gestão de Estoques", "LOG002", 80, 1),
                    ("Transportes e Distribuição", "LOG003", 80, 1),
                ],
            )

            ofertas_ads = []
            for matriz, disciplina, _acao_disciplina, _acao_matriz, codigo_oferta in [
                (
                    ads_disciplinas[0][1],
                    ads_disciplinas[0][0],
                    ads_disciplinas[0][2],
                    ads_disciplinas[0][3],
                    "ADS-BD001-2026-1-NOTURNO",
                ),
                (
                    ads_disciplinas[1][1],
                    ads_disciplinas[1][0],
                    ads_disciplinas[1][2],
                    ads_disciplinas[1][3],
                    "ADS-ES001-2026-1-NOTURNO",
                ),
                (
                    ads_disciplinas[2][1],
                    ads_disciplinas[2][0],
                    ads_disciplinas[2][2],
                    ads_disciplinas[2][3],
                    "ADS-PW001-2026-1-NOTURNO",
                ),
            ]:
                oferta, oferta_acao = await self._get_or_create_oferta_disciplina(
                    session=session,
                    id_matriz_curricular=matriz.id,
                    id_professor=professor.id,
                    id_periodo_letivo=periodo.id,
                    codigo_oferta=codigo_oferta,
                )
                ofertas_ads.append((oferta, oferta_acao, disciplina))

            ofertas_logistica = []
            for matriz, disciplina, _acao_disciplina, _acao_matriz, codigo_oferta in [
                (
                    logistica_disciplinas[0][1],
                    logistica_disciplinas[0][0],
                    logistica_disciplinas[0][2],
                    logistica_disciplinas[0][3],
                    "LOG-LOG001-2026-1-NOTURNO",
                ),
                (
                    logistica_disciplinas[1][1],
                    logistica_disciplinas[1][0],
                    logistica_disciplinas[1][2],
                    logistica_disciplinas[1][3],
                    "LOG-LOG002-2026-1-NOTURNO",
                ),
                (
                    logistica_disciplinas[2][1],
                    logistica_disciplinas[2][0],
                    logistica_disciplinas[2][2],
                    logistica_disciplinas[2][3],
                    "LOG-LOG003-2026-1-NOTURNO",
                ),
            ]:
                oferta, oferta_acao = await self._get_or_create_oferta_disciplina(
                    session=session,
                    id_matriz_curricular=matriz.id,
                    id_professor=professor.id,
                    id_periodo_letivo=periodo.id,
                    codigo_oferta=codigo_oferta,
                )
                ofertas_logistica.append((oferta, oferta_acao, disciplina))

            await self._seed_horarios_aula(
                session=session,
                horarios=[
                    (ofertas_ads[0][0], DiaSemana.TERCA, time(19, 0), time(23, 0), "LAB-01"),
                    (ofertas_ads[1][0], DiaSemana.QUINTA, time(19, 0), time(23, 0), "B-203"),
                    (ofertas_ads[2][0], DiaSemana.SEXTA, time(19, 0), time(23, 0), "LAB-02"),
                    (ofertas_logistica[0][0], DiaSemana.SEGUNDA, time(19, 0), time(23, 0), "C-101"),
                    (ofertas_logistica[1][0], DiaSemana.QUARTA, time(19, 0), time(23, 0), "C-102"),
                    (ofertas_logistica[2][0], DiaSemana.SABADO, time(8, 0), time(12, 0), "C-103"),
                ],
            )

            aula, aula_acao = await self._get_or_create_aula(
                session=session,
                id_oferta_disciplina=ofertas_ads[0][0].id,
            )
            avaliacao, avaliacao_acao = await self._get_or_create_avaliacao(
                session=session,
                id_oferta_disciplina=ofertas_ads[0][0].id,
            )
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
                id_curso_unidade=curso_unidade_ads.id,
            )

            matriculas_disciplina = []
            for oferta, _oferta_acao, _disciplina in ofertas_ads:
                matricula_disciplina, matricula_disciplina_acao = await self._get_or_create_matricula_disciplina(
                    session=session,
                    id_matricula_curso=matricula_curso.id,
                    oferta=oferta,
                )
                matriculas_disciplina.append((matricula_disciplina, matricula_disciplina_acao))

        disciplinas = ads_disciplinas + logistica_disciplinas
        matrizes = [(item[1], item[3]) for item in disciplinas]
        primeira_matricula_disciplina, primeira_matricula_disciplina_acao = matriculas_disciplina[0]

        return SeedBaseResponse(
            mensagem=(
                "Seed base executado com sucesso. "
                f"Calendário acadêmico 2026: {len(calendario_acoes)} eventos processados. "
                f"Base de conhecimento de estágio: {len(base_conhecimento_estagio_acoes)} tópicos processados. "
                f"Curso adicional criado/validado: {curso_logistica.sigla} - {curso_logistica.nome}."
            ),
            curso=SeedEntityRead(id=curso_ads.id, acao=curso_ads_acao),
            endereco_unidade=SeedEntityRead(id=endereco.id, acao=endereco_acao),
            unidade=SeedEntityRead(id=unidade.id, acao=unidade_acao),
            curso_unidade=SeedEntityRead(id=curso_unidade_ads.id, acao=curso_unidade_ads_acao),
            periodo_letivo=SeedEntityRead(id=periodo.id, acao=periodo_acao),
            disciplinas=[
                SeedEntityRead(id=disciplina.id, acao=acao_disciplina)
                for disciplina, _matriz, acao_disciplina, _acao_matriz in disciplinas
            ],
            matrizes_curriculares=[
                SeedEntityRead(id=matriz.id, acao=acao_matriz)
                for matriz, acao_matriz in matrizes
            ],
            professor=SeedEntityRead(id=professor.id, acao=professor_acao),
            oferta_disciplina=SeedEntityRead(id=ofertas_ads[0][0].id, acao=ofertas_ads[0][1]),
            aula=SeedEntityRead(id=aula.id, acao=aula_acao),
            avaliacao=SeedEntityRead(id=avaliacao.id, acao=avaliacao_acao),
            endereco_aluno=SeedEntityRead(id=endereco_aluno.id, acao=endereco_aluno_acao),
            aluno=SeedEntityRead(id=aluno.id, acao=aluno_acao),
            usuario_aluno=SeedEntityRead(id=usuario_aluno.id, acao=usuario_aluno_acao),
            matricula_curso=SeedEntityRead(id=matricula_curso.id, acao=matricula_curso_acao),
            matricula_disciplina=SeedEntityRead(
                id=primeira_matricula_disciplina.id,
                acao=primeira_matricula_disciplina_acao,
            ),
        )

    async def _get_or_create_curso(
        self,
        session: AsyncSession,
        nome: str,
        sigla: str,
        duracao_semestres: int,
    ) -> tuple[Curso, str]:
        curso = await self.curso_repository.get_by_sigla(session, sigla)
        if curso is not None:
            return curso, "existing"
        curso = Curso(
            nome=nome,
            sigla=sigla,
            duracao_semestres=duracao_semestres,
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
            data_inicio=date(2026, 2, 4),
            data_fim=date(2026, 7, 4),
            status=StatusPeriodoLetivo.ATIVO,
        )
        periodo = await self.periodo_repository.create(session, periodo)
        return periodo, "created"

    async def _seed_disciplinas_e_matriz(
        self,
        session: AsyncSession,
        id_curso_unidade: int,
        disciplinas: list[tuple[str, str, int, int]],
    ) -> list[tuple[Disciplina, MatrizCurricular, str, str]]:
        resultado: list[tuple[Disciplina, MatrizCurricular, str, str]] = []
        for nome, codigo, carga_horaria, semestre_recomendado in disciplinas:
            disciplina, acao_disciplina = await self._get_or_create_disciplina(
                session=session,
                nome=nome,
                codigo=codigo,
                carga_horaria=carga_horaria,
            )
            matriz, acao_matriz = await self._get_or_create_matriz_curricular(
                session=session,
                id_curso_unidade=id_curso_unidade,
                id_disciplina=disciplina.id,
                semestre_recomendado=semestre_recomendado,
            )
            resultado.append((disciplina, matriz, acao_disciplina, acao_matriz))
        return resultado

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
        codigo_oferta: str,
    ) -> tuple[OfertaDisciplina, str]:
        oferta = await self.oferta_repository.get_by_codigo_oferta(
            session=session,
            codigo_oferta=codigo_oferta,
        )
        if oferta is not None:
            return oferta, "existing"
        oferta = OfertaDisciplina(
            id_matriz_curricular=id_matriz_curricular,
            id_professor=id_professor,
            id_periodo_letivo=id_periodo_letivo,
            codigo_oferta=codigo_oferta,
            vagas_total=40,
            vagas_disponiveis=40,
            periodo=PeriodoOfertaDisciplina.NOTURNO,
            status=StatusOfertaDisciplina.ATIVO,
        )
        oferta = await self.oferta_repository.create(session, oferta)
        return oferta, "created"

    async def _seed_horarios_aula(
        self,
        session: AsyncSession,
        horarios: list[tuple[OfertaDisciplina, DiaSemana, time, time, str]],
    ) -> list[tuple[HorarioAula, str]]:
        resultado: list[tuple[HorarioAula, str]] = []
        for oferta, dia_semana, hora_inicio, hora_fim, sala in horarios:
            horario, acao = await self._get_or_create_horario_aula(
                session=session,
                id_oferta_disciplina=oferta.id,
                dia_semana=dia_semana,
                hora_inicio=hora_inicio,
                hora_fim=hora_fim,
                sala=sala,
            )
            resultado.append((horario, acao))
        return resultado

    async def _get_or_create_horario_aula(
        self,
        session: AsyncSession,
        id_oferta_disciplina: int,
        dia_semana: DiaSemana,
        hora_inicio: time,
        hora_fim: time,
        sala: str,
    ) -> tuple[HorarioAula, str]:
        statement = select(HorarioAula).where(
            HorarioAula.id_oferta_disciplina == id_oferta_disciplina,
            HorarioAula.dia_semana == dia_semana,
            HorarioAula.hora_inicio == hora_inicio,
            HorarioAula.hora_fim == hora_fim,
            HorarioAula.sala == sala,
        )
        result = await session.exec(statement)
        horario = result.first()
        if horario is not None:
            return horario, "existing"

        horario = HorarioAula(
            id_oferta_disciplina=id_oferta_disciplina,
            dia_semana=dia_semana,
            hora_inicio=hora_inicio,
            hora_fim=hora_fim,
            sala=sala,
        )
        session.add(horario)
        await session.flush()
        return horario, "created"

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

    async def _seed_base_conhecimento_estagio_demo(
        self,
        session: AsyncSession,
    ) -> list[str]:
        topicos = self._base_conhecimento_estagio_demo_topicos()
        acoes: list[str] = []
        for topico in topicos:
            _base_conhecimento, acao = await self._get_or_create_base_conhecimento(
                session=session,
                titulo=topico["titulo"],
                pergunta_base=topico["pergunta_base"],
                resposta=topico["resposta"],
                tags=topico["tags"],
            )
            acoes.append(acao)
        return acoes

    async def _get_or_create_base_conhecimento(
        self,
        session: AsyncSession,
        titulo: str,
        pergunta_base: str,
        resposta: str,
        tags: list[str],
    ) -> tuple[BaseConhecimento, str]:
        statement = select(BaseConhecimento).where(
            BaseConhecimento.categoria == CategoriaBaseConhecimento.ESTAGIO,
            BaseConhecimento.titulo == titulo,
        )
        result = await session.exec(statement)
        base_conhecimento = result.first()
        if base_conhecimento is not None:
            return base_conhecimento, "existing"

        base_conhecimento = BaseConhecimento(
            titulo=titulo,
            categoria=CategoriaBaseConhecimento.ESTAGIO,
            pergunta_base=pergunta_base,
            resposta=resposta,
            tags=tags,
            status=StatusBaseConhecimento.ATIVO,
        )
        session.add(base_conhecimento)
        await session.flush()
        return base_conhecimento, "created"

    def _base_conhecimento_estagio_demo_topicos(self) -> list[dict]:
        return [
            {
                "titulo": "O que é estágio obrigatório",
                "pergunta_base": "O que é o estágio obrigatório e quando ele é necessário?",
                "resposta": (
                    "O estágio obrigatório é uma atividade prevista no projeto pedagógico do curso e pode ser exigido "
                    "para a conclusão da formação. Para a demo, a orientação é verificar com a coordenação do curso se "
                    "o estágio é obrigatório, qual carga horária deve ser cumprida e em qual etapa do curso ele pode ser iniciado."
                ),
                "tags": ["estagio", "obrigatorio", "curso", "coordenacao"],
            },
            {
                "titulo": "Estágio não obrigatório",
                "pergunta_base": "Posso fazer estágio mesmo quando ele não é obrigatório?",
                "resposta": (
                    "Sim. O estágio não obrigatório pode ser realizado como atividade complementar de formação profissional, "
                    "desde que esteja relacionado à área do curso e siga as exigências institucionais. Mesmo quando não é obrigatório, "
                    "ele deve possuir documentação regular e acompanhamento adequado."
                ),
                "tags": ["estagio", "nao obrigatorio", "atividade complementar"],
            },
            {
                "titulo": "Termo de compromisso de estágio",
                "pergunta_base": "O que é o termo de compromisso de estágio?",
                "resposta": (
                    "O termo de compromisso de estágio é o documento que formaliza a relação entre estudante, empresa concedente "
                    "e instituição de ensino. Para a demo, ele deve conter dados do aluno, dados da empresa, período do estágio, "
                    "carga horária, atividades previstas e assinaturas das partes envolvidas."
                ),
                "tags": ["estagio", "termo de compromisso", "documentacao"],
            },
            {
                "titulo": "Convênio com a empresa concedente",
                "pergunta_base": "A empresa precisa ter convênio com a faculdade para oferecer estágio?",
                "resposta": (
                    "Em geral, a empresa concedente precisa estar regularizada para receber estagiários e pode ser necessário possuir "
                    "convênio ou cadastro junto à instituição. Para fins de MVP, a assistente deve orientar o aluno a confirmar com a "
                    "secretaria ou coordenação se a empresa já possui cadastro ativo."
                ),
                "tags": ["estagio", "convenio", "empresa", "secretaria"],
            },
            {
                "titulo": "Plano de atividades do estágio",
                "pergunta_base": "Quais atividades posso realizar no estágio?",
                "resposta": (
                    "As atividades do estágio devem estar relacionadas ao curso do aluno e precisam constar no plano de atividades. "
                    "Esse plano ajuda a garantir que o estágio tenha finalidade educacional, evitando tarefas desconectadas da formação acadêmica."
                ),
                "tags": ["estagio", "plano de atividades", "atividades"],
            },
            {
                "titulo": "Carga horária do estágio",
                "pergunta_base": "Qual é a carga horária permitida para estágio?",
                "resposta": (
                    "A carga horária do estágio deve respeitar as regras acadêmicas e legais aplicáveis, sem prejudicar a frequência do aluno "
                    "nas aulas. Para a demo, a orientação padrão é verificar no regulamento do curso e validar a carga horária com a coordenação antes de assinar o termo."
                ),
                "tags": ["estagio", "carga horaria", "horario"],
            },
            {
                "titulo": "Supervisor de estágio",
                "pergunta_base": "Quem acompanha o estágio do aluno?",
                "resposta": (
                    "O estágio deve ser acompanhado por um supervisor na empresa e por um responsável acadêmico indicado pela instituição ou coordenação. "
                    "O supervisor da empresa orienta as atividades práticas, enquanto a instituição acompanha a aderência do estágio ao curso."
                ),
                "tags": ["estagio", "supervisor", "acompanhamento"],
            },
            {
                "titulo": "Relatório de estágio",
                "pergunta_base": "Preciso entregar relatório de estágio?",
                "resposta": (
                    "Sim, a entrega de relatório pode ser exigida para comprovar as atividades realizadas e a evolução do aluno. Para a demo, "
                    "a assistente deve orientar que o relatório descreva atividades executadas, período, carga horária e avaliação do aprendizado."
                ),
                "tags": ["estagio", "relatorio", "avaliacao"],
            },
            {
                "titulo": "Alteração ou rescisão do estágio",
                "pergunta_base": "O que fazer se o estágio for encerrado ou alterado?",
                "resposta": (
                    "Se houver encerramento, mudança de horário, alteração de atividades ou troca de empresa, o aluno deve comunicar a secretaria ou coordenação. "
                    "Dependendo do caso, pode ser necessário emitir termo aditivo, termo de rescisão ou novo termo de compromisso."
                ),
                "tags": ["estagio", "rescisao", "alteracao", "termo aditivo"],
            },
            {
                "titulo": "Dúvidas frequentes sobre assinatura de estágio",
                "pergunta_base": "Onde consigo ajuda para assinar documentos de estágio?",
                "resposta": (
                    "Para dúvidas sobre assinatura de documentos, o aluno deve procurar a secretaria acadêmica ou a coordenação do curso. "
                    "Na demo, a assistente pode orientar o aluno a separar o termo de compromisso, plano de atividades, dados da empresa e dados do supervisor antes de solicitar análise."
                ),
                "tags": ["estagio", "assinatura", "documentos", "duvidas frequentes"],
            },
        ]

    async def _seed_calendario_academico_2026(
        self,
        session: AsyncSession,
        id_unidade: int,
    ) -> list[str]:
        eventos = self._calendario_academico_2026_eventos()
        acoes: list[str] = []
        for evento in eventos:
            _calendario, acao = await self._get_or_create_calendario_academico(
                session=session,
                id_unidade=id_unidade,
                titulo=evento["titulo"],
                descricao=evento.get("descricao"),
                tipo=evento["tipo"],
                data_inicio=evento["data_inicio"],
                data_fim=evento.get("data_fim"),
                periodo=evento.get("periodo"),
            )
            acoes.append(acao)
        return acoes

    async def _get_or_create_calendario_academico(
        self,
        session: AsyncSession,
        id_unidade: int,
        titulo: str,
        descricao: str | None,
        tipo: TipoCalendarioAcademico,
        data_inicio: date,
        data_fim: date | None = None,
        periodo: int | None = None,
    ) -> tuple[CalendarioAcademico, str]:
        statement = select(CalendarioAcademico).where(
            CalendarioAcademico.id_unidade == id_unidade,
            CalendarioAcademico.titulo == titulo,
            CalendarioAcademico.data_inicio == data_inicio,
        )
        result = await session.exec(statement)
        calendario = result.first()
        if calendario is not None:
            return calendario, "existing"

        calendario = CalendarioAcademico(
            id_unidade=id_unidade,
            titulo=titulo,
            descricao=descricao,
            tipo=tipo,
            data_inicio=data_inicio,
            data_fim=data_fim,
            periodo=periodo,
            status=StatusCalendarioAcademico.ATIVO,
        )
        session.add(calendario)
        await session.flush()
        return calendario, "created"

    def _calendario_academico_2026_eventos(self) -> list[dict]:
        return [
            # Janeiro/2026
            {
                "titulo": "Confraternização Universal",
                "descricao": "Feriado Nacional.",
                "tipo": TipoCalendarioAcademico.FERIADO,
                "data_inicio": date(2026, 1, 1),
                "periodo": 1,
            },
            {
                "titulo": "Prazo final de validação dos dados dos alunos concluintes",
                "descricao": "Validação dos dados dos alunos concluintes do 2º semestre de 2025 no SIGA (Port. 07/2025).",
                "tipo": TipoCalendarioAcademico.PRAZO,
                "data_inicio": date(2026, 1, 5),
                "periodo": 1,
            },
            {
                "titulo": "Inscrições para vagas remanescentes e transferências",
                "descricao": "Período das inscrições para vagas remanescentes e transferências.",
                "tipo": TipoCalendarioAcademico.REMATRICULA,
                "data_inicio": date(2026, 1, 12),
                "data_fim": date(2026, 1, 16),
                "periodo": 1,
            },
            {
                "titulo": "Rematrícula de alunos veteranos",
                "descricao": "Período de rematrícula de alunos veteranos.",
                "tipo": TipoCalendarioAcademico.REMATRICULA,
                "data_inicio": date(2026, 1, 12),
                "data_fim": date(2026, 1, 18),
                "periodo": 1,
            },
            {
                "titulo": "Matrícula da 1ª Chamada - Vestibular",
                "descricao": "Período de matrícula da 1ª chamada do Vestibular.",
                "tipo": TipoCalendarioAcademico.REMATRICULA,
                "data_inicio": date(2026, 1, 20),
                "data_fim": date(2026, 1, 22),
                "periodo": 1,
            },
            {
                "titulo": "Matrícula da 1ª Chamada - Provão Paulista",
                "descricao": "Período de matrícula da 1ª chamada do Provão Paulista.",
                "tipo": TipoCalendarioAcademico.REMATRICULA,
                "data_inicio": date(2026, 1, 20),
                "data_fim": date(2026, 1, 22),
                "periodo": 1,
            },
            {
                "titulo": "Matrícula da 2ª Chamada - Vestibular",
                "descricao": "Período de matrícula da 2ª chamada do Vestibular.",
                "tipo": TipoCalendarioAcademico.REMATRICULA,
                "data_inicio": date(2026, 1, 27),
                "data_fim": date(2026, 1, 29),
                "periodo": 1,
            },
            {
                "titulo": "Matrícula da 2ª Chamada - Provão Paulista",
                "descricao": "Período de matrícula da 2ª chamada do Provão Paulista.",
                "tipo": TipoCalendarioAcademico.REMATRICULA,
                "data_inicio": date(2026, 1, 27),
                "data_fim": date(2026, 1, 29),
                "periodo": 1,
            },
            # Fevereiro/2026
            {
                "titulo": "Início do 1º Semestre de 2026",
                "descricao": "Início administrativo do 1º semestre de 2026.",
                "tipo": TipoCalendarioAcademico.EVENTO,
                "data_inicio": date(2026, 2, 4),
                "periodo": 1,
            },
            {
                "titulo": "Semana de Práticas e Atualização Pedagógica - 18ª SPAP",
                "descricao": "Semana de práticas e atualização pedagógica.",
                "tipo": TipoCalendarioAcademico.EVENTO,
                "data_inicio": date(2026, 2, 4),
                "data_fim": date(2026, 2, 7),
                "periodo": 1,
            },
            {
                "titulo": "Início das aulas do 1º Semestre Letivo de 2026",
                "descricao": "Início das aulas e recepção dos calouros.",
                "tipo": TipoCalendarioAcademico.EVENTO,
                "data_inicio": date(2026, 2, 9),
                "periodo": 1,
            },
            {
                "titulo": "Carnaval e Quarta-Feira de Cinzas",
                "descricao": "Não haverá aula - feriado e emenda.",
                "tipo": TipoCalendarioAcademico.FERIADO,
                "data_inicio": date(2026, 2, 14),
                "data_fim": date(2026, 2, 18),
                "periodo": 1,
            },
            {
                "titulo": "Prazo final de matrículas de veteranos para vagas remanescentes e transferências",
                "descricao": "Prazo final de matrículas de alunos veteranos para vagas remanescentes e transferências.",
                "tipo": TipoCalendarioAcademico.REMATRICULA,
                "data_inicio": date(2026, 2, 19),
                "periodo": 1,
            },
            {
                "titulo": "Prazo final de alterações de matrículas de veteranos",
                "descricao": "Prazo final de alterações de matrículas para acomodação de horários de alunos veteranos.",
                "tipo": TipoCalendarioAcademico.REMATRICULA,
                "data_inicio": date(2026, 2, 19),
                "periodo": 1,
            },
            {
                "titulo": "Prazo final de alterações de matrículas de ingressantes",
                "descricao": "Prazo final de alterações de matrículas de alunos ingressantes para acomodação de horários.",
                "tipo": TipoCalendarioAcademico.REMATRICULA,
                "data_inicio": date(2026, 2, 23),
                "periodo": 1,
            },
            {
                "titulo": "Inscrições para vagas remanescentes de 1º semestre",
                "descricao": "Período das inscrições para vagas remanescentes de 1º semestre.",
                "tipo": TipoCalendarioAcademico.REMATRICULA,
                "data_inicio": date(2026, 2, 23),
                "data_fim": date(2026, 2, 25),
                "periodo": 1,
            },
            {
                "titulo": "GTur Convida IV",
                "descricao": "Evento acadêmico GTur Convida IV.",
                "tipo": TipoCalendarioAcademico.EVENTO,
                "data_inicio": date(2026, 2, 23),
                "data_fim": date(2026, 2, 27),
                "periodo": 1,
            },
            {
                "titulo": "Prazo final de matrículas de ingressantes",
                "descricao": "Fechamento do sistema de matrícula remota.",
                "tipo": TipoCalendarioAcademico.REMATRICULA,
                "data_inicio": date(2026, 2, 28),
                "periodo": 1,
            },
            # Março/2026
            {
                "titulo": "Cancelamento de matrícula de veteranos sem declaração de interesse",
                "descricao": "Cancelamento de matrícula dos alunos veteranos que não declararam interesse pela manutenção de sua vaga.",
                "tipo": TipoCalendarioAcademico.TRANCAMENTO,
                "data_inicio": date(2026, 3, 2),
                "periodo": 1,
            },
            {
                "titulo": "Electronics Day",
                "descricao": "Evento acadêmico Electronics Day.",
                "tipo": TipoCalendarioAcademico.EVENTO,
                "data_inicio": date(2026, 3, 9),
                "periodo": 1,
            },
            {
                "titulo": "Prazo final para aproveitamento de estudos de ingressantes",
                "descricao": "Prazo para componentes curriculares ofertados a partir do segundo período letivo do curso.",
                "tipo": TipoCalendarioAcademico.PRAZO,
                "data_inicio": date(2026, 3, 25),
                "periodo": 1,
            },
            # Abril/2026
            {
                "titulo": "Paixão de Cristo - feriado e emenda",
                "descricao": "Não haverá aula - feriado e emenda.",
                "tipo": TipoCalendarioAcademico.FERIADO,
                "data_inicio": date(2026, 4, 3),
                "data_fim": date(2026, 4, 4),
                "periodo": 1,
            },
            {
                "titulo": "Páscoa",
                "descricao": "Páscoa.",
                "tipo": TipoCalendarioAcademico.FERIADO,
                "data_inicio": date(2026, 4, 5),
                "periodo": 1,
            },
            {
                "titulo": "EXPO EDIF",
                "descricao": "Evento acadêmico EXPO EDIF.",
                "tipo": TipoCalendarioAcademico.EVENTO,
                "data_inicio": date(2026, 4, 7),
                "data_fim": date(2026, 4, 10),
                "periodo": 1,
            },
            {
                "titulo": "Avaliação presencial EaD - P1",
                "descricao": "Avaliações presenciais do CST em Gestão Empresarial - EaD - P1.",
                "tipo": TipoCalendarioAcademico.PROVA,
                "data_inicio": date(2026, 4, 11),
                "periodo": 1,
            },
            {
                "titulo": "Prazo final para desistência de disciplina",
                "descricao": "Prazo final para desistência de disciplina de cursos semestrais.",
                "tipo": TipoCalendarioAcademico.PRAZO,
                "data_inicio": date(2026, 4, 17),
                "periodo": 1,
            },
            {
                "titulo": "Tiradentes - feriado e emenda",
                "descricao": "Não haverá aula - feriado e emenda.",
                "tipo": TipoCalendarioAcademico.FERIADO,
                "data_inicio": date(2026, 4, 20),
                "data_fim": date(2026, 4, 21),
                "periodo": 1,
            },
            {
                "titulo": "19ª STMA - Semana de Tecnologia e Meio Ambiente",
                "descricao": "Semana de Tecnologia e Meio Ambiente.",
                "tipo": TipoCalendarioAcademico.EVENTO,
                "data_inicio": date(2026, 4, 27),
                "data_fim": date(2026, 4, 30),
                "periodo": 1,
            },
            # Maio/2026
            {
                "titulo": "Dia do Trabalho - feriado e emenda",
                "descricao": "Não haverá aula - feriado e emenda.",
                "tipo": TipoCalendarioAcademico.FERIADO,
                "data_inicio": date(2026, 5, 1),
                "data_fim": date(2026, 5, 2),
                "periodo": 1,
            },
            {
                "titulo": "SIPAT",
                "descricao": "Semana Interna de Prevenção de Acidentes do Trabalho.",
                "tipo": TipoCalendarioAcademico.EVENTO,
                "data_inicio": date(2026, 5, 4),
                "data_fim": date(2026, 5, 8),
                "periodo": 1,
            },
            {
                "titulo": "Portas Abertas",
                "descricao": "Evento institucional Portas Abertas.",
                "tipo": TipoCalendarioAcademico.EVENTO,
                "data_inicio": date(2026, 5, 9),
                "periodo": 1,
            },
            {
                "titulo": "Prazo final de trancamento de matrículas de cursos semestrais",
                "descricao": "Exceto para alunos ingressantes.",
                "tipo": TipoCalendarioAcademico.TRANCAMENTO,
                "data_inicio": date(2026, 5, 13),
                "periodo": 1,
            },
            {
                "titulo": "Semana de Eventos do Secretariado",
                "descricao": "Semana de Eventos do Secretariado.",
                "tipo": TipoCalendarioAcademico.EVENTO,
                "data_inicio": date(2026, 5, 18),
                "data_fim": date(2026, 5, 22),
                "periodo": 1,
            },
            {
                "titulo": "III Simpósio Internacional de Paisagismo da FATEC-SP",
                "descricao": "Simpósio Internacional de Paisagismo.",
                "tipo": TipoCalendarioAcademico.EVENTO,
                "data_inicio": date(2026, 5, 25),
                "data_fim": date(2026, 5, 29),
                "periodo": 1,
            },
            # Junho/2026
            {
                "titulo": "Corpus Christi - feriado e emenda",
                "descricao": "Não haverá aula - feriado e emenda.",
                "tipo": TipoCalendarioAcademico.FERIADO,
                "data_inicio": date(2026, 6, 4),
                "data_fim": date(2026, 6, 6),
                "periodo": 1,
            },
            {
                "titulo": "Exame de rendimento de línguas estrangeiras",
                "descricao": "Período para aplicação de exame de rendimento de línguas estrangeiras.",
                "tipo": TipoCalendarioAcademico.PROVA,
                "data_inicio": date(2026, 6, 8),
                "data_fim": date(2026, 6, 20),
                "periodo": 1,
            },
            {
                "titulo": "XVI Semana de Turismo",
                "descricao": "Semana de Turismo.",
                "tipo": TipoCalendarioAcademico.EVENTO,
                "data_inicio": date(2026, 6, 9),
                "data_fim": date(2026, 6, 12),
                "periodo": 1,
            },
            {
                "titulo": "Festival Gastronômico",
                "descricao": "Mostra de Projetos de Eventos Gastronômicos das 16h às 18h.",
                "tipo": TipoCalendarioAcademico.EVENTO,
                "data_inicio": date(2026, 6, 11),
                "periodo": 1,
            },
            {
                "titulo": "Avaliação presencial EaD - P2",
                "descricao": "Avaliações presenciais do CST em Gestão Empresarial - EaD - P2.",
                "tipo": TipoCalendarioAcademico.PROVA,
                "data_inicio": date(2026, 6, 13),
                "periodo": 1,
            },
            {
                "titulo": "Prazo final para fechamento das disciplinas no SIGA",
                "descricao": "Prazo final para fechamento das disciplinas no SIGA dos cursos semestrais.",
                "tipo": TipoCalendarioAcademico.PRAZO,
                "data_inicio": date(2026, 6, 27),
                "periodo": 1,
            },
            {
                "titulo": "Término das aulas do 1º Semestre Letivo de 2026",
                "descricao": "Término das aulas do 1º Semestre Letivo de 2026.",
                "tipo": TipoCalendarioAcademico.EVENTO,
                "data_inicio": date(2026, 6, 27),
                "periodo": 1,
            },
            {
                "titulo": "Solicitação de revisão da média final",
                "descricao": "Período para solicitar revisão da média final de cursos semestrais via SIGA.",
                "tipo": TipoCalendarioAcademico.PRAZO,
                "data_inicio": date(2026, 6, 29),
                "data_fim": date(2026, 7, 1),
                "periodo": 1,
            },
            # Julho/2026
            {
                "titulo": "Divulgação de resultados de revisão da média final",
                "descricao": "Divulgação dos resultados de revisão da média final de cursos semestrais via SIGA.",
                "tipo": TipoCalendarioAcademico.PRAZO,
                "data_inicio": date(2026, 7, 2),
                "data_fim": date(2026, 7, 4),
                "periodo": 1,
            },
            {
                "titulo": "Encerramento do 1º Semestre de 2026",
                "descricao": "Encerramento do 1º Semestre de 2026.",
                "tipo": TipoCalendarioAcademico.EVENTO,
                "data_inicio": date(2026, 7, 4),
                "periodo": 1,
            },
            {
                "titulo": "Exames finais de cursos semestrais",
                "descricao": "Período de exames finais de cursos semestrais.",
                "tipo": TipoCalendarioAcademico.PROVA,
                "data_inicio": date(2026, 7, 6),
                "data_fim": date(2026, 7, 8),
                "periodo": 1,
            },
            {
                "titulo": "Revolução Constitucionalista",
                "descricao": "Feriado - Revolução Constitucionalista.",
                "tipo": TipoCalendarioAcademico.FERIADO,
                "data_inicio": date(2026, 7, 9),
                "periodo": 2,
            },
            {
                "titulo": "Recesso escolar",
                "descricao": "Período de recesso escolar.",
                "tipo": TipoCalendarioAcademico.EVENTO,
                "data_inicio": date(2026, 7, 10),
                "data_fim": date(2026, 7, 25),
                "periodo": 2,
            },
            {
                "titulo": "Rematrícula de alunos veteranos de cursos semestrais",
                "descricao": "Rematrícula de alunos veteranos de cursos semestrais.",
                "tipo": TipoCalendarioAcademico.REMATRICULA,
                "data_inicio": date(2026, 7, 13),
                "data_fim": date(2026, 7, 19),
                "periodo": 2,
            },
            {
                "titulo": "Início do 2º Semestre de 2026",
                "descricao": "Início do 2º Semestre de 2026.",
                "tipo": TipoCalendarioAcademico.EVENTO,
                "data_inicio": date(2026, 7, 27),
                "periodo": 2,
            },
            {
                "titulo": "Semana de Práticas e Atualização Pedagógica - 19ª SPAP",
                "descricao": "Semana de práticas e atualização pedagógica.",
                "tipo": TipoCalendarioAcademico.EVENTO,
                "data_inicio": date(2026, 7, 27),
                "data_fim": date(2026, 7, 31),
                "periodo": 2,
            },
            # Agosto/2026
            {
                "titulo": "Início das aulas do 2º Semestre Letivo de 2026",
                "descricao": "Início das aulas e recepção dos calouros.",
                "tipo": TipoCalendarioAcademico.EVENTO,
                "data_inicio": date(2026, 8, 3),
                "periodo": 2,
            },
            {
                "titulo": "GTur Convida V",
                "descricao": "Evento acadêmico GTur Convida V.",
                "tipo": TipoCalendarioAcademico.EVENTO,
                "data_inicio": date(2026, 8, 3),
                "data_fim": date(2026, 8, 7),
                "periodo": 2,
            },
            {
                "titulo": "Prazo final de validação dos dados dos concluintes",
                "descricao": "Validação dos dados dos alunos concluintes do 1º semestre de 2026 via SIGA.",
                "tipo": TipoCalendarioAcademico.PRAZO,
                "data_inicio": date(2026, 8, 5),
                "periodo": 2,
            },
            {
                "titulo": "Prazo final de matrículas de veteranos para vagas remanescentes e transferências",
                "descricao": "Prazo final de matrículas de alunos veteranos para vagas remanescentes e transferências.",
                "tipo": TipoCalendarioAcademico.REMATRICULA,
                "data_inicio": date(2026, 8, 10),
                "periodo": 2,
            },
            {
                "titulo": "Prazo final de alterações de matrículas de veteranos",
                "descricao": "Prazo final de alterações de matrículas de alunos veteranos para acomodação de horários.",
                "tipo": TipoCalendarioAcademico.REMATRICULA,
                "data_inicio": date(2026, 8, 10),
                "periodo": 2,
            },
            {
                "titulo": "Prazo final de alterações de matrículas de ingressantes",
                "descricao": "Prazo final de alterações de matrículas de alunos ingressantes para acomodação de horários.",
                "tipo": TipoCalendarioAcademico.REMATRICULA,
                "data_inicio": date(2026, 8, 17),
                "periodo": 2,
            },
            {
                "titulo": "Inscrições para vagas remanescentes de 1º semestre",
                "descricao": "Período das inscrições para vagas remanescentes de 1º semestre.",
                "tipo": TipoCalendarioAcademico.REMATRICULA,
                "data_inicio": date(2026, 8, 24),
                "data_fim": date(2026, 8, 26),
                "periodo": 2,
            },
            {
                "titulo": "Prazo final de matrículas de ingressantes",
                "descricao": "Fechamento do sistema de matrícula remota.",
                "tipo": TipoCalendarioAcademico.REMATRICULA,
                "data_inicio": date(2026, 8, 31),
                "periodo": 2,
            },
            # Setembro/2026
            {
                "titulo": "Independência do Brasil",
                "descricao": "Não haverá aula - Feriado - Independência do Brasil.",
                "tipo": TipoCalendarioAcademico.FERIADO,
                "data_inicio": date(2026, 9, 7),
                "periodo": 2,
            },
            {
                "titulo": "Prazo final de trancamento de matrículas de cursos anuais",
                "descricao": "Exceto para alunos ingressantes.",
                "tipo": TipoCalendarioAcademico.TRANCAMENTO,
                "data_inicio": date(2026, 9, 15),
                "periodo": 2,
            },
            {
                "titulo": "Welding Show",
                "descricao": "Feira de Equipamentos e Acessórios para Solda e Corte.",
                "tipo": TipoCalendarioAcademico.EVENTO,
                "data_inicio": date(2026, 9, 15),
                "data_fim": date(2026, 9, 17),
                "periodo": 2,
            },
            {
                "titulo": "II Expo Orquídeas da FATEC-SP",
                "descricao": "Evento II Expo Orquídeas da FATEC-SP.",
                "tipo": TipoCalendarioAcademico.EVENTO,
                "data_inicio": date(2026, 9, 24),
                "data_fim": date(2026, 9, 26),
                "periodo": 2,
            },
            # Outubro/2026
            {
                "titulo": "Preparo da faculdade para eleição - 1º turno",
                "descricao": "Preparação da faculdade para as eleições nacionais de 2026.",
                "tipo": TipoCalendarioAcademico.EVENTO,
                "data_inicio": date(2026, 10, 2),
                "data_fim": date(2026, 10, 3),
                "periodo": 2,
            },
            {
                "titulo": "Eleições Nacionais 2026 - 1º turno",
                "descricao": "Eleições Nacionais 2026 - 1º turno.",
                "tipo": TipoCalendarioAcademico.FERIADO,
                "data_inicio": date(2026, 10, 4),
                "periodo": 2,
            },
            {
                "titulo": "Avaliação presencial EaD - P1 - 2º semestre",
                "descricao": "Avaliações presenciais do CST em Gestão Empresarial - EaD - P1.",
                "tipo": TipoCalendarioAcademico.PROVA,
                "data_inicio": date(2026, 10, 5),
                "periodo": 2,
            },
            {
                "titulo": "Prazo final para desistência de disciplina - 2º semestre",
                "descricao": "Prazo final para desistência de disciplina de cursos semestrais.",
                "tipo": TipoCalendarioAcademico.PRAZO,
                "data_inicio": date(2026, 10, 6),
                "periodo": 2,
            },
            {
                "titulo": "27º Congresso de Tecnologia e 28º Simpósio de Iniciação Científica e Tecnológica",
                "descricao": "Congresso de Tecnologia e Simpósio de Iniciação Científica e Tecnológica.",
                "tipo": TipoCalendarioAcademico.EVENTO,
                "data_inicio": date(2026, 10, 5),
                "data_fim": date(2026, 10, 9),
                "periodo": 2,
            },
            {
                "titulo": "Nossa Senhora Aparecida",
                "descricao": "Não haverá aula - Feriado - Dia de Nossa Senhora Aparecida.",
                "tipo": TipoCalendarioAcademico.FERIADO,
                "data_inicio": date(2026, 10, 12),
                "periodo": 2,
            },
            {
                "titulo": "Dia do Professor",
                "descricao": "Não haverá aula - Dia do Professor.",
                "tipo": TipoCalendarioAcademico.FERIADO,
                "data_inicio": date(2026, 10, 15),
                "periodo": 2,
            },
            {
                "titulo": "Prazo final de trancamento de matrículas de cursos semestrais - 2º semestre",
                "descricao": "Exceto para alunos ingressantes.",
                "tipo": TipoCalendarioAcademico.TRANCAMENTO,
                "data_inicio": date(2026, 10, 29),
                "periodo": 2,
            },
            # Novembro/2026
            {
                "titulo": "Finados",
                "descricao": "Não haverá aula - Feriado - Dia de finados.",
                "tipo": TipoCalendarioAcademico.FERIADO,
                "data_inicio": date(2026, 11, 2),
                "periodo": 2,
            },
            {
                "titulo": "Semana de Eventos do Secretariado - 2º semestre",
                "descricao": "Semana de Eventos do Secretariado.",
                "tipo": TipoCalendarioAcademico.EVENTO,
                "data_inicio": date(2026, 11, 9),
                "data_fim": date(2026, 11, 13),
                "periodo": 2,
            },
            {
                "titulo": "Proclamação da República",
                "descricao": "Feriado - Proclamação da República.",
                "tipo": TipoCalendarioAcademico.FERIADO,
                "data_inicio": date(2026, 11, 15),
                "periodo": 2,
            },
            {
                "titulo": "Exame de rendimento de línguas estrangeiras - 2º semestre",
                "descricao": "Período para aplicação de exame de rendimento de línguas estrangeiras.",
                "tipo": TipoCalendarioAcademico.PROVA,
                "data_inicio": date(2026, 11, 16),
                "data_fim": date(2026, 11, 30),
                "periodo": 2,
            },
            {
                "titulo": "Consciência Negra - feriado e emenda",
                "descricao": "Não haverá aula - feriado e emenda - Dia da Consciência Negra.",
                "tipo": TipoCalendarioAcademico.FERIADO,
                "data_inicio": date(2026, 11, 20),
                "data_fim": date(2026, 11, 21),
                "periodo": 2,
            },
            {
                "titulo": "X Dia Mundial do Turismo",
                "descricao": "Evento X Dia Mundial do Turismo.",
                "tipo": TipoCalendarioAcademico.EVENTO,
                "data_inicio": date(2026, 11, 23),
                "data_fim": date(2026, 11, 27),
                "periodo": 2,
            },
            {
                "titulo": "Avaliação presencial EaD - P2 - 2º semestre",
                "descricao": "Avaliações presenciais do CST em Gestão Empresarial - EaD - P2.",
                "tipo": TipoCalendarioAcademico.PROVA,
                "data_inicio": date(2026, 11, 28),
                "periodo": 2,
            },
            # Dezembro/2026
            {
                "titulo": "Envio da chave aos professores para fechamento dos cursos",
                "descricao": "Envio da chave aos professores para fechamento dos cursos no SIGA.",
                "tipo": TipoCalendarioAcademico.PRAZO,
                "data_inicio": date(2026, 12, 4),
                "periodo": 2,
            },
            {
                "titulo": "Avaliação presencial EaD - Prova final - 2º semestre",
                "descricao": "Avaliações presenciais do CST em Gestão Empresarial - EaD - Prova final.",
                "tipo": TipoCalendarioAcademico.PROVA,
                "data_inicio": date(2026, 12, 5),
                "periodo": 2,
            },
            {
                "titulo": "Prazo final para entrega de médias finais e frequência",
                "descricao": "Prazo final para entrega de médias finais, conteúdos programáticos e frequência.",
                "tipo": TipoCalendarioAcademico.PRAZO,
                "data_inicio": date(2026, 12, 14),
                "periodo": 2,
            },
            {
                "titulo": "Término das aulas do 2º semestre letivo de 2026",
                "descricao": "Término das aulas do 2º semestre letivo de 2026.",
                "tipo": TipoCalendarioAcademico.EVENTO,
                "data_inicio": date(2026, 12, 14),
                "periodo": 2,
            },
            {
                "titulo": "Solicitação de revisão de médias finais",
                "descricao": "Período para solicitar revisão de médias finais via SIGA.",
                "tipo": TipoCalendarioAcademico.PRAZO,
                "data_inicio": date(2026, 12, 15),
                "data_fim": date(2026, 12, 17),
                "periodo": 2,
            },
            {
                "titulo": "Divulgação dos resultados de revisão de médias finais",
                "descricao": "Divulgação dos resultados de revisão de médias finais via SIGA.",
                "tipo": TipoCalendarioAcademico.PRAZO,
                "data_inicio": date(2026, 12, 18),
                "data_fim": date(2026, 12, 21),
                "periodo": 2,
            },
            {
                "titulo": "Encerramento do 2º Semestre de 2026",
                "descricao": "Encerramento do 2º Semestre de 2026.",
                "tipo": TipoCalendarioAcademico.EVENTO,
                "data_inicio": date(2026, 12, 21),
                "periodo": 2,
            },
            {
                "titulo": "Exames finais - 2º semestre",
                "descricao": "Período de exames finais.",
                "tipo": TipoCalendarioAcademico.PROVA,
                "data_inicio": date(2026, 12, 22),
                "data_fim": date(2026, 12, 23),
                "periodo": 2,
            },
            {
                "titulo": "Natal",
                "descricao": "Natal.",
                "tipo": TipoCalendarioAcademico.FERIADO,
                "data_inicio": date(2026, 12, 25),
                "periodo": 2,
            },
        ]
