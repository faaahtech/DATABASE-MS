from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from models.aula import Aula
from models.disciplina import Disciplina
from models.matricula_curso import MatriculaCurso
from models.matricula_disciplina import MatriculaDisciplina
from models.matriz_curricular import MatrizCurricular
from models.oferta_disciplina import OfertaDisciplina
from models.presenca import Presenca


class PresencaRepository:
    async def create(self, session: AsyncSession, presenca: Presenca) -> Presenca:
        session.add(presenca)
        await session.flush()
        return presenca

    async def get_by_id(self, session: AsyncSession, id_presenca: int) -> Presenca | None:
        return await session.get(Presenca, id_presenca)

    async def list_by_aluno(
        self,
        session: AsyncSession,
        id_aluno: int,
        limit: int = 100,
        offset: int = 0,
    ) -> list[Presenca]:
        statement = (
            select(Presenca)
            .join(
                MatriculaDisciplina,
                MatriculaDisciplina.id == Presenca.id_matricula_disciplina,
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
                Presenca.id,
                MatriculaCurso.id_aluno,
                Presenca.id_matricula_disciplina,
                Presenca.id_aula,
                Presenca.presente,
                Presenca.justificativa,
                Aula.data,
                Aula.assunto,
                MatriculaDisciplina.id_oferta_disciplina,
                Disciplina.nome,
                Disciplina.codigo,
            )
            .join(
                MatriculaDisciplina,
                MatriculaDisciplina.id == Presenca.id_matricula_disciplina,
            )
            .join(
                MatriculaCurso,
                MatriculaCurso.id == MatriculaDisciplina.id_matricula_curso,
            )
            .join(
                Aula,
                Aula.id == Presenca.id_aula,
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
    ) -> list[Presenca]:
        statement = (
            select(Presenca)
            .where(Presenca.id_matricula_disciplina == id_matricula_disciplina)
            .offset(offset)
            .limit(limit)
        )
        result = await session.exec(statement)
        return list(result.all())

    async def update(self, session: AsyncSession, presenca: Presenca) -> Presenca:
        session.add(presenca)
        await session.flush()
        await session.refresh(presenca)
        return presenca

    async def exists_for_aula_and_matricula(
        self,
        session: AsyncSession,
        id_aula: int,
        id_matricula_disciplina: int,
        ignore_id_presenca: int | None = None,
    ) -> bool:
        statement = select(Presenca.id).where(
            Presenca.id_aula == id_aula,
            Presenca.id_matricula_disciplina == id_matricula_disciplina,
        )
        if ignore_id_presenca is not None:
            statement = statement.where(Presenca.id != ignore_id_presenca)
        statement = statement.limit(1)
        result = await session.exec(statement)
        return result.first() is not None
