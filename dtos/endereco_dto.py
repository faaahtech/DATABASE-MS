from sqlmodel import SQLModel


class EnderecoCreate(SQLModel):
    rua: str
    cep: str
    numero: str
    bairro: str
    estado: str
    cidade: str
    complemento: str | None = None


class EnderecoRead(SQLModel):
    id: int
    rua: str
    cep: str
    numero: str
    bairro: str
    estado: str
    cidade: str
    complemento: str | None = None
