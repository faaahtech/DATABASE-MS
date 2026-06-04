"""Geração de protocolos únicos para solicitações e atendimentos."""

from __future__ import annotations

from datetime import datetime, timezone
import re
import secrets


_PREFIX_PATTERN = re.compile(r"[^A-Z0-9]")


def generate_protocol(prefix: str = "SOL") -> str:
    """Gera protocolo legível com prefixo, data e trecho aleatório.

    Exemplo: ``SOL-20260602-A1B2C3D4``.
    """
    normalized_prefix = str(prefix or "SOL").strip().upper()
    normalized_prefix = _PREFIX_PATTERN.sub("", normalized_prefix)[:10] or "SOL"

    date_part = datetime.now(timezone.utc).strftime("%Y%m%d")
    random_part = secrets.token_hex(4).upper()

    return f"{normalized_prefix}-{date_part}-{random_part}"
