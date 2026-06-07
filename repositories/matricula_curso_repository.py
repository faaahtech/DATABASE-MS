from __future__ import annotations

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from models.matricula_curso import MatriculaCurso, StatusMatriculaCurso


class MatriculaCursoRepository:
    async def create(self, session: AsyncSession, matricula_curso: MatriculaCurso) -> MatriculaCurso:
        session.add(matricula_curso)
        await session.flush()
        return matricula_curso

    async def get_by_id(
        self,
        session: AsyncSession,
        id_matricula_curso: int,
    ) -> MatriculaCurso | None:
        return await session.get(MatriculaCurso, id_matricula_curso)

    async def get_by_ra(self, session: AsyncSession, ra: str) -> MatriculaCurso | None:
        statement = select(MatriculaCurso).where(MatriculaCurso.ra == ra.upper().strip())
        result = await session.exec(statement)
        return result.first()

    async def exists_by_ra(self, session: AsyncSession, ra: str) -> bool:
        statement = select(MatriculaCurso.id).where(MatriculaCurso.ra == ra.upper().strip()).limit(1)
        result = await session.exec(statement)
        return result.first() is not None

    async def list_by_aluno(
        self,
        session: AsyncSession,
        id_aluno: int,
        limit: int = 100,
        offset: int = 0,
    ) -> list[MatriculaCurso]:
        statement = (
            select(MatriculaCurso)
            .where(MatriculaCurso.id_aluno == id_aluno)
            .offset(offset)
            .limit(limit)
        )
        result = await session.exec(statement)
        return list(result.all())

    async def get_matricula_cursando_by_aluno(
        self,
        session: AsyncSession,
        id_aluno: int,
    ) -> MatriculaCurso | None:
        statement = (
            select(MatriculaCurso)
            .where(
                MatriculaCurso.id_aluno == id_aluno,
                MatriculaCurso.status == StatusMatriculaCurso.CURSANDO,
            )
            .order_by(MatriculaCurso.id.desc())
            .limit(1)
        )
        result = await session.exec(statement)
        return result.first()

    async def update(self, session: AsyncSession, matricula_curso: MatriculaCurso) -> MatriculaCurso:
        session.add(matricula_curso)
        await session.flush()
        return matricula_curso
