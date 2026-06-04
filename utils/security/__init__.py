"""Utilitários de segurança.

O projeto já possuía a pasta ``utils/security/``. Por isso, as funções
foram expostas neste ``__init__.py`` em vez de criar ``utils/security.py``.
Assim, imports como ``from utils.security import hash_password`` funcionam
sem alterar a organização existente.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
import hashlib
import hmac
import os
import secrets
from typing import Any

import jwt

try:
    from config.setting import settings
except Exception:  # pragma: no cover - fallback para execuções isoladas
    settings = None  # type: ignore[assignment]


_PASSWORD_HASH_ALGORITHM = "pbkdf2_sha256"
_DEFAULT_HASH_ITERATIONS = 390_000
_RECOVERY_TOKEN_BYTES = 32


def _get_setting_value(name: str, default: Any = None) -> Any:
    """Lê uma configuração do ambiente ou de ``config.setting.settings``."""
    env_value = os.getenv(name)
    if env_value not in (None, ""):
        return env_value

    if settings is not None and hasattr(settings, name):
        settings_value = getattr(settings, name)
        if settings_value not in (None, ""):
            return settings_value

    return default


def _get_secret_key() -> str:
    """Obtém a chave secreta para assinatura de tokens."""
    secret_key = (
        _get_setting_value("SECRET_KEY")
        or _get_setting_value("SECRET_HASH_CODE")
        or _get_setting_value("secret_hash_code")
    )

    if not secret_key:
        raise RuntimeError(
            "SECRET_KEY não configurada. Defina SECRET_KEY ou secret_hash_code no .env."
        )

    return str(secret_key)


def _get_algorithm() -> str:
    return str(_get_setting_value("ALGORITHM", "HS256"))


def _get_access_token_expire_minutes() -> int:
    raw_value = _get_setting_value("ACCESS_TOKEN_EXPIRE_MINUTES", 60)
    try:
        return int(raw_value)
    except (TypeError, ValueError):
        return 60


def hash_password(password: str) -> str:
    """Gera hash seguro de senha usando PBKDF2-HMAC-SHA256.

    Retorna no formato:
    ``pbkdf2_sha256$iteracoes$salt_hex$hash_hex``.
    """
    if not isinstance(password, str) or not password:
        raise ValueError("Senha é obrigatória.")

    salt = secrets.token_bytes(16)
    password_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        _DEFAULT_HASH_ITERATIONS,
    )

    return (
        f"{_PASSWORD_HASH_ALGORITHM}"
        f"${_DEFAULT_HASH_ITERATIONS}"
        f"${salt.hex()}"
        f"${password_hash.hex()}"
    )


def verify_password(password: str, password_hash: str) -> bool:
    """Valida senha pura contra hash gerado por ``hash_password``."""
    if not password or not password_hash:
        return False

    try:
        algorithm, iterations_raw, salt_hex, stored_hash_hex = password_hash.split("$", 3)
        if algorithm != _PASSWORD_HASH_ALGORITHM:
            return False

        iterations = int(iterations_raw)
        salt = bytes.fromhex(salt_hex)
        stored_hash = bytes.fromhex(stored_hash_hex)

        candidate_hash = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt,
            iterations,
        )

        return hmac.compare_digest(candidate_hash, stored_hash)
    except (ValueError, TypeError):
        return False


def create_access_token(payload: dict, expires_delta: timedelta | None = None) -> str:
    """Cria JWT de acesso a partir de um payload."""
    if not isinstance(payload, dict):
        raise ValueError("Payload do token deve ser um dicionário.")

    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=_get_access_token_expire_minutes())
    )

    token_payload = payload.copy()
    token_payload.update({"exp": expire, "iat": datetime.now(timezone.utc)})

    return jwt.encode(token_payload, _get_secret_key(), algorithm=_get_algorithm())


def decode_access_token(token: str) -> dict:
    """Decodifica e valida JWT de acesso."""
    if not token:
        raise ValueError("Token é obrigatório.")

    try:
        decoded = jwt.decode(token, _get_secret_key(), algorithms=[_get_algorithm()])
        return dict(decoded)
    except jwt.ExpiredSignatureError as exc:
        raise ValueError("Token expirado.") from exc
    except jwt.InvalidTokenError as exc:
        raise ValueError("Token inválido.") from exc


def generate_recovery_token() -> str:
    """Gera token opaco para recuperação de senha."""
    return secrets.token_urlsafe(_RECOVERY_TOKEN_BYTES)


def hash_token(token: str) -> str:
    """Gera hash de token opaco para armazenar recuperação sem salvar token puro."""
    if not token:
        raise ValueError("Token é obrigatório.")

    secret_key = _get_secret_key().encode("utf-8")
    digest = hmac.new(secret_key, token.encode("utf-8"), hashlib.sha256).hexdigest()
    return f"hmac_sha256${digest}"


def verify_token_hash(token: str, token_hash: str) -> bool:
    """Valida token opaco contra hash gerado por ``hash_token``."""
    if not token or not token_hash:
        return False

    try:
        expected_hash = hash_token(token)
        return hmac.compare_digest(expected_hash, token_hash)
    except ValueError:
        return False
