from datetime import date
from decimal import Decimal


def validate_positive_int(value: int, field_name: str) -> int:
    if value <= 0:
        raise ValueError(f"{field_name} deve ser maior que zero.")
    return value


def validate_semestre_letivo(semestre: int) -> int:
    if semestre not in (1, 2):
        raise ValueError("Semestre letivo deve ser 1 ou 2.")
    return semestre


def validate_periodo_letivo_datas(data_inicio: date, data_fim: date) -> None:
    if data_fim <= data_inicio:
        raise ValueError("A data final do período letivo deve ser maior que a data inicial.")


def validate_nota_valor(valor: Decimal) -> Decimal:
    if valor < 0 or valor > 10:
        raise ValueError("Nota deve estar entre 0 e 10.")
    return valor
