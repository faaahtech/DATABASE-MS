from sqlmodel import Field, SQLModel


class SeedEntityRead(SQLModel):
    id: int
    acao: str = Field(description="created ou existing")


class SeedBaseResponse(SQLModel):
    mensagem: str
    curso: SeedEntityRead
    endereco_unidade: SeedEntityRead
    unidade: SeedEntityRead
    curso_unidade: SeedEntityRead
    periodo_letivo: SeedEntityRead
    disciplinas: list[SeedEntityRead]
    matrizes_curriculares: list[SeedEntityRead] = Field(default_factory=list)
    professor: SeedEntityRead | None = None
    oferta_disciplina: SeedEntityRead | None = None
    aula: SeedEntityRead | None = None
    avaliacao: SeedEntityRead | None = None
    endereco_aluno: SeedEntityRead | None = None
    aluno: SeedEntityRead | None = None
    usuario_aluno: SeedEntityRead | None = None
    matricula_curso: SeedEntityRead | None = None
    matricula_disciplina: SeedEntityRead | None = None
