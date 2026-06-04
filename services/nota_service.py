from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlmodel.ext.asyncio.session import AsyncSession

from dtos.nota_dto import NotaCreate, NotaPorAlunoRead, NotaRead, NotaUpdate
from models.avaliacao import Avaliacao
from models.matricula_disciplina import MatriculaDisciplina
from models.nota import Nota
from repositories.aluno_repository import AlunoRepository
from repositories.nota_repository import NotaRepository


class NotaService:
    def __init__(self) -> None:
        self.nota_repository = NotaRepository()
        self.aluno_repository = AlunoRepository()

    async def atribuir_nota(self, session: AsyncSession, data: NotaCreate) -> NotaRead:
        self._validate_valor_nota(data.valor)

        nota = Nota(**data.model_dump())

        try:
            async with session.begin():
                matricula_disciplina = await session.get(MatriculaDisciplina, data.id_matricula_disciplina)
                if matricula_disciplina is None:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Matrícula em disciplina não encontrada.",
                    )

                avaliacao = await session.get(Avaliacao, data.id_avaliacao)
                if avaliacao is None:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Avaliação não encontrada.",
                    )

                if avaliacao.id_oferta_disciplina != matricula_disciplina.id_oferta_disciplina:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="A avaliação informada não pertence à mesma oferta da matrícula em disciplina.",
                    )

                exists = await self.nota_repository.exists_for_avaliacao_and_matricula(
                    session=session,
                    id_avaliacao=data.id_avaliacao,
                    id_matricula_disciplina=data.id_matricula_disciplina,
                )
                if exists:
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail="Nota já atribuída para esta matrícula e avaliação.",
                    )

                nota = await self.nota_repository.create(session, nota)
        except IntegrityError as exc:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Não foi possível atribuir nota por conflito de dados únicos.",
            ) from exc

        return self._to_read(nota)

    async def update_nota(
        self,
        session: AsyncSession,
        id_nota: int,
        data: NotaUpdate,
    ) -> NotaRead:
        update_data = data.model_dump(exclude_unset=True)
        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Informe ao menos um campo para atualizar a nota.",
            )

        if "valor" in update_data:
            if update_data["valor"] is None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="O valor da nota não pode ser nulo.",
                )
            self._validate_valor_nota(update_data["valor"])

        for field_name in ("id_avaliacao", "id_matricula_disciplina"):
            if field_name in update_data and update_data[field_name] is None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"O campo {field_name} não pode ser nulo.",
                )

        try:
            async with session.begin():
                nota = await self.nota_repository.get_by_id(session, id_nota)
                if nota is None:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Nota não encontrada.",
                    )

                target_id_avaliacao = update_data.get("id_avaliacao", nota.id_avaliacao)
                target_id_matricula_disciplina = update_data.get(
                    "id_matricula_disciplina",
                    nota.id_matricula_disciplina,
                )

                avaliacao = await session.get(Avaliacao, target_id_avaliacao)
                if avaliacao is None:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Avaliação não encontrada.",
                    )

                matricula_disciplina = await session.get(
                    MatriculaDisciplina,
                    target_id_matricula_disciplina,
                )
                if matricula_disciplina is None:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Matrícula em disciplina não encontrada.",
                    )

                if avaliacao.id_oferta_disciplina != matricula_disciplina.id_oferta_disciplina:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="A avaliação informada não pertence à mesma oferta da matrícula em disciplina.",
                    )

                changed_pair = (
                    target_id_avaliacao != nota.id_avaliacao
                    or target_id_matricula_disciplina != nota.id_matricula_disciplina
                )
                if changed_pair:
                    exists = await self.nota_repository.exists_for_avaliacao_and_matricula(
                        session=session,
                        id_avaliacao=target_id_avaliacao,
                        id_matricula_disciplina=target_id_matricula_disciplina,
                        ignore_id_nota=id_nota,
                    )
                    if exists:
                        raise HTTPException(
                            status_code=status.HTTP_409_CONFLICT,
                            detail="Já existe nota atribuída para esta matrícula e avaliação.",
                        )

                if "id_avaliacao" in update_data:
                    nota.id_avaliacao = target_id_avaliacao
                if "id_matricula_disciplina" in update_data:
                    nota.id_matricula_disciplina = target_id_matricula_disciplina
                if "valor" in update_data:
                    nota.valor = update_data["valor"]

                nota = await self.nota_repository.update(session, nota)
        except IntegrityError as exc:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Não foi possível atualizar nota por conflito de dados únicos.",
            ) from exc

        return self._to_read(nota)

    async def consultar_notas_por_aluno(
        self,
        session: AsyncSession,
        id_aluno: int,
        limit: int = 100,
        offset: int = 0,
    ) -> list[NotaPorAlunoRead]:
        aluno = await self.aluno_repository.get_by_id(session, id_aluno)
        if aluno is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Aluno não encontrado.",
            )

        notas = await self.nota_repository.list_by_aluno_enriched(
            session=session,
            id_aluno=id_aluno,
            limit=limit,
            offset=offset,
        )
        return [self._to_por_aluno_read_from_row(row) for row in notas]

    async def consultar_notas_por_matricula_disciplina(
        self,
        session: AsyncSession,
        id_matricula_disciplina: int,
        limit: int = 100,
        offset: int = 0,
    ) -> list[NotaRead]:
        matricula_disciplina = await session.get(MatriculaDisciplina, id_matricula_disciplina)
        if matricula_disciplina is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Matrícula em disciplina não encontrada.",
            )

        notas = await self.nota_repository.list_by_matricula_disciplina(
            session=session,
            id_matricula_disciplina=id_matricula_disciplina,
            limit=limit,
            offset=offset,
        )
        return [self._to_read(nota) for nota in notas]

    def _validate_valor_nota(self, valor: Decimal) -> None:
        if valor < Decimal("0") or valor > Decimal("10"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A nota deve estar entre 0 e 10.",
            )

    def _to_read(self, nota: Nota) -> NotaRead:
        return NotaRead(
            id=nota.id,
            id_avaliacao=nota.id_avaliacao,
            id_matricula_disciplina=nota.id_matricula_disciplina,
            valor=nota.valor,
        )

    def _to_por_aluno_read(self, nota: Nota, id_aluno: int) -> NotaPorAlunoRead:
        return NotaPorAlunoRead(
            id=nota.id,
            id_aluno=id_aluno,
            id_avaliacao=nota.id_avaliacao,
            id_matricula_disciplina=nota.id_matricula_disciplina,
            valor=nota.valor,
        )

    def _to_por_aluno_read_from_row(self, row) -> NotaPorAlunoRead:
        (
            id_nota,
            id_aluno,
            id_avaliacao,
            id_matricula_disciplina,
            valor,
            avaliacao_nome,
            avaliacao_data,
            id_oferta_disciplina,
            disciplina_nome,
            disciplina_codigo,
        ) = row
        return NotaPorAlunoRead(
            id=id_nota,
            id_aluno=id_aluno,
            id_avaliacao=id_avaliacao,
            id_matricula_disciplina=id_matricula_disciplina,
            valor=valor,
            avaliacao_nome=avaliacao_nome,
            avaliacao_data=avaliacao_data,
            id_oferta_disciplina=id_oferta_disciplina,
            disciplina_nome=disciplina_nome,
            disciplina_codigo=disciplina_codigo,
        )
