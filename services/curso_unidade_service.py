from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlmodel.ext.asyncio.session import AsyncSession

from dtos.curso_unidade_dto import CursoUnidadeCreate, CursoUnidadeListItem, CursoUnidadeRead
from models.curso_unidade import CursoUnidade
from repositories.curso_repository import CursoRepository
from repositories.curso_unidade_repository import CursoUnidadeRepository
from repositories.unidade_repository import UnidadeRepository


class CursoUnidadeService:
    def __init__(self) -> None:
        self.curso_repository = CursoRepository()
        self.unidade_repository = UnidadeRepository()
        self.curso_unidade_repository = CursoUnidadeRepository()

    async def create_curso_unidade(
        self,
        session: AsyncSession,
        data: CursoUnidadeCreate,
    ) -> CursoUnidadeRead:
        curso_unidade = CursoUnidade(**data.model_dump())

        try:
            async with session.begin():
                curso = await self.curso_repository.get_by_id(session, data.id_curso)
                if curso is None:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Curso não encontrado.",
                    )

                unidade = await self.unidade_repository.get_by_id(session, data.id_unidade)
                if unidade is None:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Unidade não encontrada.",
                    )

                exists = await self.curso_unidade_repository.exists_by_curso_and_unidade(
                    session=session,
                    id_curso=data.id_curso,
                    id_unidade=data.id_unidade,
                    nivel=data.nivel,
                    modalidade=data.modalidade,
                )
                if exists:
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail="Este curso_unidade já existe para curso, unidade, nível e modalidade informados.",
                    )

                curso_unidade = await self.curso_unidade_repository.create(session, curso_unidade)
        except IntegrityError as exc:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Não foi possível criar curso_unidade por conflito de dados únicos.",
            ) from exc

        return self._to_read(curso_unidade)

    async def get_curso_unidade_by_id(
        self,
        session: AsyncSession,
        id_curso_unidade: int,
    ) -> CursoUnidadeRead:
        curso_unidade = await self.curso_unidade_repository.get_by_id(session, id_curso_unidade)
        if curso_unidade is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Curso_unidade não encontrado.",
            )
        return self._to_read(curso_unidade)

    async def list_curso_unidade(
        self,
        session: AsyncSession,
        limit: int = 100,
        offset: int = 0,
    ) -> list[CursoUnidadeListItem]:
        itens = await self.curso_unidade_repository.list(session, limit=limit, offset=offset)
        return [self._to_list_item(item) for item in itens]

    def _to_read(self, curso_unidade: CursoUnidade) -> CursoUnidadeRead:
        return CursoUnidadeRead(
            id=curso_unidade.id,
            id_curso=curso_unidade.id_curso,
            id_unidade=curso_unidade.id_unidade,
            nivel=curso_unidade.nivel,
            modalidade=curso_unidade.modalidade,
            status=curso_unidade.status,
        )

    def _to_list_item(self, curso_unidade: CursoUnidade) -> CursoUnidadeListItem:
        return CursoUnidadeListItem(
            id=curso_unidade.id,
            id_curso=curso_unidade.id_curso,
            id_unidade=curso_unidade.id_unidade,
            nivel=curso_unidade.nivel,
            modalidade=curso_unidade.modalidade,
            status=curso_unidade.status,
        )
