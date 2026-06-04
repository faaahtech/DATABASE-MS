from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlmodel.ext.asyncio.session import AsyncSession

from dtos.presenca_dto import PresencaCreate, PresencaPorAlunoRead, PresencaRead, PresencaUpdate
from models.aula import Aula
from models.matricula_disciplina import MatriculaDisciplina
from models.presenca import Presenca
from repositories.aluno_repository import AlunoRepository
from repositories.presenca_repository import PresencaRepository


class PresencaService:
    def __init__(self) -> None:
        self.presenca_repository = PresencaRepository()
        self.aluno_repository = AlunoRepository()

    async def atribuir_presenca(self, session: AsyncSession, data: PresencaCreate) -> PresencaRead:
        presenca = Presenca(**data.model_dump())

        try:
            async with session.begin():
                matricula_disciplina = await session.get(MatriculaDisciplina, data.id_matricula_disciplina)
                if matricula_disciplina is None:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Matrícula em disciplina não encontrada.",
                    )

                aula = await session.get(Aula, data.id_aula)
                if aula is None:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Aula não encontrada.",
                    )

                if aula.id_oferta_disciplina != matricula_disciplina.id_oferta_disciplina:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="A aula informada não pertence à mesma oferta da matrícula em disciplina.",
                    )

                exists = await self.presenca_repository.exists_for_aula_and_matricula(
                    session=session,
                    id_aula=data.id_aula,
                    id_matricula_disciplina=data.id_matricula_disciplina,
                )
                if exists:
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail="Presença já atribuída para esta matrícula e aula.",
                    )

                presenca = await self.presenca_repository.create(session, presenca)
        except IntegrityError as exc:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Não foi possível atribuir presença por conflito de dados únicos.",
            ) from exc

        return self._to_read(presenca)

    async def update_presenca(
        self,
        session: AsyncSession,
        id_presenca: int,
        data: PresencaUpdate,
    ) -> PresencaRead:
        update_data = data.model_dump(exclude_unset=True)
        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Informe ao menos um campo para atualizar a presença.",
            )

        for field_name in ("id_matricula_disciplina", "id_aula", "presente"):
            if field_name in update_data and update_data[field_name] is None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"O campo {field_name} não pode ser nulo.",
                )

        try:
            async with session.begin():
                presenca = await self.presenca_repository.get_by_id(session, id_presenca)
                if presenca is None:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Presença não encontrada.",
                    )

                target_id_matricula_disciplina = update_data.get(
                    "id_matricula_disciplina",
                    presenca.id_matricula_disciplina,
                )
                target_id_aula = update_data.get("id_aula", presenca.id_aula)

                matricula_disciplina = await session.get(
                    MatriculaDisciplina,
                    target_id_matricula_disciplina,
                )
                if matricula_disciplina is None:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Matrícula em disciplina não encontrada.",
                    )

                aula = await session.get(Aula, target_id_aula)
                if aula is None:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Aula não encontrada.",
                    )

                if aula.id_oferta_disciplina != matricula_disciplina.id_oferta_disciplina:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="A aula informada não pertence à mesma oferta da matrícula em disciplina.",
                    )

                changed_pair = (
                    target_id_matricula_disciplina != presenca.id_matricula_disciplina
                    or target_id_aula != presenca.id_aula
                )
                if changed_pair:
                    exists = await self.presenca_repository.exists_for_aula_and_matricula(
                        session=session,
                        id_aula=target_id_aula,
                        id_matricula_disciplina=target_id_matricula_disciplina,
                        ignore_id_presenca=id_presenca,
                    )
                    if exists:
                        raise HTTPException(
                            status_code=status.HTTP_409_CONFLICT,
                            detail="Já existe presença atribuída para esta matrícula e aula.",
                        )

                if "id_matricula_disciplina" in update_data:
                    presenca.id_matricula_disciplina = target_id_matricula_disciplina
                if "id_aula" in update_data:
                    presenca.id_aula = target_id_aula
                if "presente" in update_data:
                    presenca.presente = update_data["presente"]
                if "justificativa" in update_data:
                    presenca.justificativa = update_data["justificativa"]

                presenca = await self.presenca_repository.update(session, presenca)
        except IntegrityError as exc:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Não foi possível atualizar presença por conflito de dados únicos.",
            ) from exc

        return self._to_read(presenca)

    async def consultar_presencas_por_aluno(
        self,
        session: AsyncSession,
        id_aluno: int,
        limit: int = 100,
        offset: int = 0,
    ) -> list[PresencaPorAlunoRead]:
        aluno = await self.aluno_repository.get_by_id(session, id_aluno)
        if aluno is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Aluno não encontrado.",
            )

        presencas = await self.presenca_repository.list_by_aluno_enriched(
            session=session,
            id_aluno=id_aluno,
            limit=limit,
            offset=offset,
        )
        return [self._to_por_aluno_read_from_row(row) for row in presencas]

    async def consultar_presencas_por_matricula_disciplina(
        self,
        session: AsyncSession,
        id_matricula_disciplina: int,
        limit: int = 100,
        offset: int = 0,
    ) -> list[PresencaRead]:
        matricula_disciplina = await session.get(MatriculaDisciplina, id_matricula_disciplina)
        if matricula_disciplina is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Matrícula em disciplina não encontrada.",
            )

        presencas = await self.presenca_repository.list_by_matricula_disciplina(
            session=session,
            id_matricula_disciplina=id_matricula_disciplina,
            limit=limit,
            offset=offset,
        )
        return [self._to_read(presenca) for presenca in presencas]

    def _to_read(self, presenca: Presenca) -> PresencaRead:
        return PresencaRead(
            id=presenca.id,
            id_matricula_disciplina=presenca.id_matricula_disciplina,
            id_aula=presenca.id_aula,
            presente=presenca.presente,
            justificativa=presenca.justificativa,
        )

    def _to_por_aluno_read(self, presenca: Presenca, id_aluno: int) -> PresencaPorAlunoRead:
        return PresencaPorAlunoRead(
            id=presenca.id,
            id_aluno=id_aluno,
            id_matricula_disciplina=presenca.id_matricula_disciplina,
            id_aula=presenca.id_aula,
            presente=presenca.presente,
            justificativa=presenca.justificativa,
        )

    def _to_por_aluno_read_from_row(self, row) -> PresencaPorAlunoRead:
        (
            id_presenca,
            id_aluno,
            id_matricula_disciplina,
            id_aula,
            presente,
            justificativa,
            data_aula,
            assunto_aula,
            id_oferta_disciplina,
            disciplina_nome,
            disciplina_codigo,
        ) = row
        return PresencaPorAlunoRead(
            id=id_presenca,
            id_aluno=id_aluno,
            id_matricula_disciplina=id_matricula_disciplina,
            id_aula=id_aula,
            presente=presente,
            justificativa=justificativa,
            data_aula=data_aula,
            assunto_aula=assunto_aula,
            id_oferta_disciplina=id_oferta_disciplina,
            disciplina_nome=disciplina_nome,
            disciplina_codigo=disciplina_codigo,
        )
