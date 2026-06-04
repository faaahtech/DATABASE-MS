"""Validadores simples usados pelas camadas de service/controller."""

from __future__ import annotations

import re
from typing import Any


_EMAIL_PATTERN = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")
_NON_DIGIT_PATTERN = re.compile(r"\D+")


def validate_email(email: str) -> str:
    """Valida e normaliza e-mail."""
    if not isinstance(email, str) or not email.strip():
        raise ValueError("E-mail é obrigatório.")

    normalized_email = email.strip().lower()

    if not _EMAIL_PATTERN.match(normalized_email):
        raise ValueError("E-mail inválido.")

    return normalized_email


def validate_password_strength(password: str) -> None:
    """Valida força mínima de senha.

    Regra simples para MVP:
    - mínimo de 8 caracteres;
    - pelo menos uma letra;
    - pelo menos um número.
    """
    if not isinstance(password, str) or not password:
        raise ValueError("Senha é obrigatória.")

    if len(password) < 8:
        raise ValueError("Senha deve ter pelo menos 8 caracteres.")

    if not any(char.isalpha() for char in password):
        raise ValueError("Senha deve conter pelo menos uma letra.")

    if not any(char.isdigit() for char in password):
        raise ValueError("Senha deve conter pelo menos um número.")


def validate_required_id(value: Any, field_name: str) -> int:
    """Valida ID obrigatório e positivo."""
    if value is None:
        raise ValueError(f"{field_name} é obrigatório.")

    try:
        parsed_value = int(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{field_name} deve ser um número inteiro.") from exc

    if parsed_value <= 0:
        raise ValueError(f"{field_name} deve ser maior que zero.")

    return parsed_value


def only_digits(value: str) -> str:
    """Remove caracteres não numéricos."""
    if value is None:
        return ""
    return _NON_DIGIT_PATTERN.sub("", str(value))


def validate_cpf(cpf: str) -> str:
    """Valida CPF com dígitos verificadores e retorna apenas números."""
    digits = only_digits(cpf)

    if len(digits) != 11:
        raise ValueError("CPF deve conter 11 dígitos.")

    if digits == digits[0] * 11:
        raise ValueError("CPF inválido.")

    def _calculate_digit(base: str) -> str:
        total = sum(int(digit) * weight for digit, weight in zip(base, range(len(base) + 1, 1, -1)))
        remainder = (total * 10) % 11
        return "0" if remainder == 10 else str(remainder)

    first_digit = _calculate_digit(digits[:9])
    second_digit = _calculate_digit(digits[:9] + first_digit)

    if digits[-2:] != first_digit + second_digit:
        raise ValueError("CPF inválido.")

    return digits


def validate_ra(ra: str) -> str:
    """Valida RA de forma simples para o MVP.

    O model atual armazena RA em ``MatriculaCurso.ra``. Como o padrão oficial
    da instituição pode variar, a validação aqui apenas exige conteúdo
    alfanumérico com tamanho razoável.
    """
    if not isinstance(ra, str) or not ra.strip():
        raise ValueError("RA é obrigatório.")

    normalized_ra = ra.strip().upper()

    if not re.fullmatch(r"[A-Z0-9.-]{3,30}", normalized_ra):
        raise ValueError("RA inválido.")

    return normalized_ra


def validate_semestre(semestre: int) -> int:
    """Valida semestre acadêmico em faixa comum para cursos superiores."""
    try:
        parsed_semestre = int(semestre)
    except (TypeError, ValueError) as exc:
        raise ValueError("Semestre deve ser um número inteiro.") from exc

    if parsed_semestre < 1 or parsed_semestre > 12:
        raise ValueError("Semestre deve estar entre 1 e 12.")

    return parsed_semestre
