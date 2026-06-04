from collections.abc import Callable
from typing import Any, TypeVar

from fastapi import HTTPException, status

T = TypeVar("T")


def validate_or_400(func: Callable[..., T], *args: Any, **kwargs: Any) -> T:
    """Executa validações de utils e converte ValueError em HTTP 400."""
    try:
        return func(*args, **kwargs)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
