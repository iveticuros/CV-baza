"""Application-layer encryption for PII columns (Fernet)."""
from __future__ import annotations

from typing import Any

from cryptography.fernet import Fernet, InvalidToken
from sqlalchemy import String, TypeDecorator


def _fernet_from_key(key: str) -> Fernet:
    return Fernet(key.strip().encode("utf-8"))


class EncryptedString(TypeDecorator):
    """Stores strings as Fernet tokens in a VARCHAR/Text column."""

    impl = String
    cache_ok = True

    def __init__(self, length: int = 2048, **kw: Any) -> None:
        super().__init__(length, **kw)

    def process_bind_param(self, value: str | None, dialect: Any) -> str | None:
        if value is None:
            return None
        from ..config import settings

        f = _fernet_from_key(settings.PII_ENCRYPTION_KEY)
        return f.encrypt(value.encode("utf-8")).decode("utf-8")

    def process_result_value(self, value: str | None, dialect: Any) -> str | None:
        if value is None:
            return None
        from ..config import settings

        f = _fernet_from_key(settings.PII_ENCRYPTION_KEY)
        try:
            return f.decrypt(value.encode("utf-8")).decode("utf-8")
        except InvalidToken:
            return value
