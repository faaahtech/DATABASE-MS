from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from models.avaliacao import Avaliacao
from models.disciplina import Disciplina
from models.matricula_curso import MatriculaCurso
from models.matricula_disciplina import MatriculaDisciplina
from models.matriz_curricular import MatrizCurricular
from models.nota import Nota
from models.oferta_disciplina import OfertaDisciplina


class NotaRepository:
    async def create(self, session: AsyncSession, nota: Nota) -> Nota:
        session.add(nota)
        await session.flush()
        return nota

    async def get_by_id(self, session: AsyncSession, id_nota: int) -> Nota | None:
        return await session.get(Nota, id_nota)

    async def list_by_aluno(
        self,
        session: AsyncSession,
        id_aluno: int,
        limit: int = 100,
        offset: int = 0,
    ) -> list[Nota]:
        statement = (
            select(Nota)
            .join(
                MatriculaDisciplina,
                MatriculaDisciplina.id == Nota.id_matricula_disciplina,
            )
            .join(
                MatriculaCurso,
                MatriculaCurso.id == MatriculaDisciplina.id_matricula_curso,
            )
            .where(MatriculaCurso.id_aluno == id_aluno)
            .offset(offset)
            .limit(limit)
        )
        result = await session.exec(statement)
        return list(result.all())

    async def list_by_aluno_enriched(
        self,
        session: AsyncSession,
        id_aluno: int,
        limit: int = 100,
        offset: int = 0,
    ):
        statement = (
            select(
                Nota.id,
                MatriculaCurso.id_aluno,
                Nota.id_avaliacao,
                Nota.id_matricula_disciplina,
                Nota.valor,
                Avaliacao.nome,
                Avaliacao.data,
                MatriculaDisciplina.id_oferta_disciplina,
                Disciplina.nome,
                Disciplina.codigo,
            )
            .join(
                MatriculaDisciplina,
                MatriculaDisciplina.id == Nota.id_matricula_disciplina,
            )
            .join(
                MatriculaCurso,
                MatriculaCurso.id == MatriculaDisciplina.id_matricula_curso,
            )
            .join(
                Avaliacao,
                Avaliacao.id == Nota.id_avaliacao,
            )
            .join(
                OfertaDisciplina,
                OfertaDisciplina.id == MatriculaDisciplina.id_oferta_disciplina,
            )
            .join(
                MatrizCurricular,
                MatrizCurricular.id == OfertaDisciplina.id_matriz_curricular,
            )
            .join(
                Disciplina,
                Disciplina.id == MatrizCurricular.id_disciplina,
            )
            .where(MatriculaCurso.id_aluno == id_aluno)
            .offset(offset)
            .limit(limit)
        )
        result = await session.exec(statement)
        return list(result.all())

    async def list_by_matricula_disciplina(
        self,
        session: AsyncSession,
        id_matricula_disciplina: int,
        limit: int = 100,
        offset: int = 0,
    ) -> list[Nota]:
        statement = (
            select(Nota)
            .where(Nota.id_matricula_disciplina == id_matricula_disciplina)
            .offset(offset)
            .limit(limit)
        )
        result = await session.exec(statement)
        return list(result.all())

    async def update(self, session: AsyncSession, nota: Nota) -> Nota:
        session.add(nota)
        await session.flush()
        await session.refresh(nota)
        return nota

    async def exists_for_avaliacao_and_matricula(
        self,
        session: AsyncSession,
        id_avaliacao: int,
        id_matricula_disciplina: int,
        ignore_id_nota: int | None = None,
    ) -> bool:
        statement = select(Nota.id).where(
            Nota.id_avaliacao == id_avaliacao,
            Nota.id_matricula_disciplina == id_matricula_disciplina,
        )
        if ignore_id_nota is not None:
            statement = statement.where(Nota.id != ignore_id_nota)
        statement = statement.limit(1)
        result = await session.exec(statement)
        return result.first() is not None
