from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlmodel.ext.asyncio.session import AsyncSession

from dtos.aula_dto import AulaCreate, AulaRead, AulaUpdate
from models.aula import Aula
from repositories.aula_repository import AulaRepository
from repositories.oferta_disciplina_repository import OfertaDisciplinaRepository


class AulaService:
    def __init__(self) -> None:
        self.aula_repository = AulaRepository()
        self.oferta_disciplina_repository = OfertaDisciplinaRepository()

    async def create_aula(self, session: AsyncSession, data: AulaCreate) -> AulaRead:
        assunto = self._normalize_assunto(data.assunto)
        aula = Aula(**{**data.model_dump(), "assunto": assunto})

        try:
            async with session.begin():
                await self._validate_oferta_disciplina_exists(session, data.id_oferta_disciplina)
                exists = await self.aula_repository.exists_by_oferta_data_assunto(
                    session=session,
                    id_oferta_disciplina=data.id_oferta_disciplina,
                    data=data.data,
                    assunto=assunto,
                )
                if exists:
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail="Já existe aula para esta oferta, data e assunto.",
                    )

                aula = await self.aula_repository.create(session, aula)
        except IntegrityError as exc:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Não foi possível criar aula por conflito de dados únicos.",
            ) from exc

        return self._to_read(aula)

    async def get_aula_by_id(self, session: AsyncSession, id_aula: int) -> AulaRead:
        aula = await self.aula_repository.get_by_id(session, id_aula)
        if aula is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Aula não encontrada.")
        return self._to_read(aula)

    async def list_aulas_by_oferta_disciplina(
        self,
        session: AsyncSession,
        id_oferta_disciplina: int,
        limit: int = 100,
        offset: int = 0,
    ) -> list[AulaRead]:
        await self._validate_oferta_disciplina_exists(session, id_oferta_disciplina)
        aulas = await self.aula_repository.list_by_oferta_disciplina(
            session=session,
            id_oferta_disciplina=id_oferta_disciplina,
            limit=limit,
            offset=offset,
        )
        return [self._to_read(aula) for aula in aulas]

    async def update_aula(self, session: AsyncSession, id_aula: int, data: AulaUpdate) -> AulaRead:
        try:
            async with session.begin():
                aula = await self.aula_repository.get_by_id(session, id_aula)
                if aula is None:
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Aula não encontrada.")

                update_data = data.model_dump(exclude_unset=True)

                if "id_oferta_disciplina" in update_data and update_data["id_oferta_disciplina"] is not None:
                    await self._validate_oferta_disciplina_exists(session, update_data["id_oferta_disciplina"])

                if "assunto" in update_data and update_data["assunto"] is not None:
                    update_data["assunto"] = self._normalize_assunto(update_data["assunto"])

                novo_id_oferta_disciplina = update_data.get("id_oferta_disciplina", aula.id_oferta_disciplina)
                nova_data = update_data.get("data", aula.data)
                novo_assunto = update_data.get("assunto", aula.assunto)

                existente = await self.aula_repository.get_by_oferta_data_assunto(
                    session=session,
                    id_oferta_disciplina=novo_id_oferta_disciplina,
                    data=nova_data,
                    assunto=novo_assunto,
                )
                if existente is not None and existente.id != id_aula:
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail="Já existe outra aula para esta oferta, data e assunto.",
                    )

                for field, value in update_data.items():
                    setattr(aula, field, value)

                aula = await self.aula_repository.update(session, aula)
        except IntegrityError as exc:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Não foi possível atualizar aula por conflito de dados únicos.",
            ) from exc

        return self._to_read(aula)

    async def _validate_oferta_disciplina_exists(self, session: AsyncSession, id_oferta_disciplina: int) -> None:
        oferta_disciplina = await self.oferta_disciplina_repository.get_by_id(session, id_oferta_disciplina)
        if oferta_disciplina is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Oferta de disciplina não encontrada.")

    def _normalize_assunto(self, assunto: str) -> str:
        if not isinstance(assunto, str) or not assunto.strip():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Assunto da aula é obrigatório.")
        return assunto.strip()

    def _to_read(self, aula: Aula) -> AulaRead:
        return AulaRead(
            id=aula.id,
            id_oferta_disciplina=aula.id_oferta_disciplina,
            data=aula.data,
            assunto=aula.assunto,
            descricao=aula.descricao,
        )
