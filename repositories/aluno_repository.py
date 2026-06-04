from __future__ import annotations

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from models.aluno import Aluno
from models.matricula_curso import MatriculaCurso


class AlunoRepository:
    async def create(self, session: AsyncSession, aluno: Aluno) -> Aluno:
        session.add(aluno)
        await session.flush()
        return aluno

    async def get_by_id(self, session: AsyncSession, id_aluno: int) -> Aluno | None:
        return await session.get(Aluno, id_aluno)

    async def get_by_ra(self, session: AsyncSession, ra: str) -> Aluno | None:
        statement = (
            select(Aluno)
            .join(MatriculaCurso, MatriculaCurso.id_aluno == Aluno.id)
            .where(MatriculaCurso.ra == ra)
        )
        result = await session.exec(statement)
        return result.first()

    async def get_by_cpf(self, session: AsyncSession, cpf: str) -> Aluno | None:
        statement = select(Aluno).where(Aluno.cpf == cpf.strip())
        result = await session.exec(statement)
        return result.first()

    async def list(
        self,
        session: AsyncSession,
        limit: int = 100,
        offset: int = 0,
    ) -> list[Aluno]:
        statement = select(Aluno).offset(offset).limit(limit)
        result = await session.exec(statement)
        return list(result.all())

    async def exists_by_ra(self, session: AsyncSession, ra: str) -> bool:
        statement = select(MatriculaCurso.id).where(MatriculaCurso.ra == ra).limit(1)
        result = await session.exec(statement)
        return result.first() is not None

    async def exists_by_cpf(self, session: AsyncSession, cpf: str) -> bool:
        statement = select(Aluno.id).where(Aluno.cpf == cpf).limit(1)
        result = await session.exec(statement)
        return result.first() is not None
