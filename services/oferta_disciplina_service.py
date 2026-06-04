from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlmodel.ext.asyncio.session import AsyncSession

from dtos.oferta_disciplina_dto import OfertaDisciplinaCreate, OfertaDisciplinaRead, OfertaDisciplinaUpdate
from models.matriz_curricular import MatrizCurricular
from models.oferta_disciplina import OfertaDisciplina
from models.periodo_letivo import PeriodoLetivo
from models.professor import Professor
from repositories.curso_unidade_repository import CursoUnidadeRepository
from repositories.disciplina_repository import DisciplinaRepository
from repositories.oferta_disciplina_repository import OfertaDisciplinaRepository


class OfertaDisciplinaService:
    def __init__(self) -> None:
        self.oferta_disciplina_repository = OfertaDisciplinaRepository()
        self.curso_unidade_repository = CursoUnidadeRepository()
        self.disciplina_repository = DisciplinaRepository()

    async def create_oferta_disciplina(
        self,
        session: AsyncSession,
        data: OfertaDisciplinaCreate,
    ) -> OfertaDisciplinaRead:
        codigo_oferta = self._normalize_codigo_oferta(data.codigo_oferta)
        self._validate_vagas(data.vagas_total, data.vagas_disponiveis)
        oferta_disciplina = OfertaDisciplina(**{**data.model_dump(), "codigo_oferta": codigo_oferta})

        try:
            async with session.begin():
                await self._validate_matriz_curricular_exists(session, data.id_matriz_curricular)
                await self._validate_professor_exists(session, data.id_professor)
                await self._validate_periodo_letivo_exists(session, data.id_periodo_letivo)

                if await self.oferta_disciplina_repository.exists_by_codigo_oferta(session, codigo_oferta):
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail="Já existe oferta de disciplina com este código.",
                    )

                oferta_disciplina = await self.oferta_disciplina_repository.create(session, oferta_disciplina)
        except IntegrityError as exc:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Não foi possível criar oferta de disciplina por conflito de dados.",
            ) from exc

        return self._to_read(oferta_disciplina)

    async def get_oferta_disciplina_by_id(
        self,
        session: AsyncSession,
        id_oferta_disciplina: int,
    ) -> OfertaDisciplinaRead:
        oferta_disciplina = await self.oferta_disciplina_repository.get_by_id(session, id_oferta_disciplina)
        if oferta_disciplina is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Oferta de disciplina não encontrada.")
        return self._to_read(oferta_disciplina)

    async def list_ofertas_by_periodo_letivo(
        self,
        session: AsyncSession,
        id_periodo_letivo: int,
        limit: int = 100,
        offset: int = 0,
    ) -> list[OfertaDisciplinaRead]:
        await self._validate_periodo_letivo_exists(session, id_periodo_letivo)
        ofertas = await self.oferta_disciplina_repository.list_by_periodo_letivo(
            session=session,
            id_periodo_letivo=id_periodo_letivo,
            limit=limit,
            offset=offset,
        )
        return [self._to_read(oferta) for oferta in ofertas]

    async def list_ofertas_by_curso_unidade(
        self,
        session: AsyncSession,
        id_curso_unidade: int,
        limit: int = 100,
        offset: int = 0,
    ) -> list[OfertaDisciplinaRead]:
        curso_unidade = await self.curso_unidade_repository.get_by_id(session, id_curso_unidade)
        if curso_unidade is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="CursoUnidade não encontrado.")
        ofertas = await self.oferta_disciplina_repository.list_by_curso_unidade(
            session=session,
            id_curso_unidade=id_curso_unidade,
            limit=limit,
            offset=offset,
        )
        return [self._to_read(oferta) for oferta in ofertas]

    async def list_ofertas_by_disciplina(
        self,
        session: AsyncSession,
        id_disciplina: int,
        limit: int = 100,
        offset: int = 0,
    ) -> list[OfertaDisciplinaRead]:
        disciplina = await self.disciplina_repository.get_by_id(session, id_disciplina)
        if disciplina is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Disciplina não encontrada.")
        ofertas = await self.oferta_disciplina_repository.list_by_disciplina(
            session=session,
            id_disciplina=id_disciplina,
            limit=limit,
            offset=offset,
        )
        return [self._to_read(oferta) for oferta in ofertas]

    async def update_oferta_disciplina(
        self,
        session: AsyncSession,
        id_oferta_disciplina: int,
        data: OfertaDisciplinaUpdate,
    ) -> OfertaDisciplinaRead:
        try:
            async with session.begin():
                oferta_disciplina = await self.oferta_disciplina_repository.get_by_id(session, id_oferta_disciplina)
                if oferta_disciplina is None:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Oferta de disciplina não encontrada.",
                    )

                update_data = data.model_dump(exclude_unset=True)

                if "codigo_oferta" in update_data and update_data["codigo_oferta"] is not None:
                    novo_codigo = self._normalize_codigo_oferta(update_data["codigo_oferta"])
                    existente = await self.oferta_disciplina_repository.get_by_codigo_oferta(session, novo_codigo)
                    if existente is not None and existente.id != id_oferta_disciplina:
                        raise HTTPException(
                            status_code=status.HTTP_409_CONFLICT,
                            detail="Já existe outra oferta de disciplina com este código.",
                        )
                    update_data["codigo_oferta"] = novo_codigo

                if "id_matriz_curricular" in update_data and update_data["id_matriz_curricular"] is not None:
                    await self._validate_matriz_curricular_exists(session, update_data["id_matriz_curricular"])
                if "id_professor" in update_data and update_data["id_professor"] is not None:
                    await self._validate_professor_exists(session, update_data["id_professor"])
                if "id_periodo_letivo" in update_data and update_data["id_periodo_letivo"] is not None:
                    await self._validate_periodo_letivo_exists(session, update_data["id_periodo_letivo"])

                novo_vagas_total = update_data.get("vagas_total", oferta_disciplina.vagas_total)
                novo_vagas_disponiveis = update_data.get("vagas_disponiveis", oferta_disciplina.vagas_disponiveis)
                self._validate_vagas(novo_vagas_total, novo_vagas_disponiveis)

                for field, value in update_data.items():
                    setattr(oferta_disciplina, field, value)

                oferta_disciplina = await self.oferta_disciplina_repository.update(session, oferta_disciplina)
        except IntegrityError as exc:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Não foi possível atualizar oferta de disciplina por conflito de dados.",
            ) from exc

        return self._to_read(oferta_disciplina)

    async def _validate_matriz_curricular_exists(self, session: AsyncSession, id_matriz_curricular: int) -> None:
        matriz_curricular = await session.get(MatrizCurricular, id_matriz_curricular)
        if matriz_curricular is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Matriz curricular não encontrada.")

    async def _validate_professor_exists(self, session: AsyncSession, id_professor: int) -> None:
        professor = await session.get(Professor, id_professor)
        if professor is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Professor não encontrado.")

    async def _validate_periodo_letivo_exists(self, session: AsyncSession, id_periodo_letivo: int) -> None:
        periodo_letivo = await session.get(PeriodoLetivo, id_periodo_letivo)
        if periodo_letivo is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Período letivo não encontrado.")

    def _normalize_codigo_oferta(self, codigo_oferta: str) -> str:
        if not isinstance(codigo_oferta, str) or not codigo_oferta.strip():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Código da oferta é obrigatório.")
        return codigo_oferta.strip().upper()

    def _validate_vagas(self, vagas_total: int, vagas_disponiveis: int) -> None:
        if vagas_total < 0:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Vagas totais deve ser maior ou igual a zero.")
        if vagas_disponiveis < 0:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Vagas disponíveis deve ser maior ou igual a zero.")
        if vagas_disponiveis > vagas_total:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Vagas disponíveis não pode ser maior que vagas totais.",
            )

    def _to_read(self, oferta_disciplina: OfertaDisciplina) -> OfertaDisciplinaRead:
        return OfertaDisciplinaRead(
            id=oferta_disciplina.id,
            id_matriz_curricular=oferta_disciplina.id_matriz_curricular,
            id_professor=oferta_disciplina.id_professor,
            id_periodo_letivo=oferta_disciplina.id_periodo_letivo,
            codigo_oferta=oferta_disciplina.codigo_oferta,
            vagas_total=oferta_disciplina.vagas_total,
            vagas_disponiveis=oferta_disciplina.vagas_disponiveis,
            periodo=oferta_disciplina.periodo,
            status=oferta_disciplina.status,
        )
