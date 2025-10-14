"""Configuration models for NiFi REST automation."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional

from pydantic import AnyHttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict


_ENV_PATH = Path(__file__).resolve().parents[3] / ".env"


class AuthSettings(BaseSettings):
    """Authentication and HTTP client settings.

    Environment variables use the ``NIFI_`` prefix, for example ``NIFI_BASE_URL``.
    An optional ``.env`` file in the project directory is also supported.
    """

    model_config = SettingsConfigDict(
        env_prefix="NIFI_",
        env_file=str(_ENV_PATH),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    base_url: AnyHttpUrl
    username: str
    password: str
    verify_ssl: bool = True
    timeout: float = 10.0

    def merged(self, **overrides: Any) -> "AuthSettings":
        """Return a copy with overrides applied, ignoring ``None`` values."""

        payload: Dict[str, Any] = {k: v for k, v in overrides.items() if v is not None}
        if not payload:
            return self
        return self.model_copy(update=payload)


def build_settings(
    base_url: Optional[str],
    username: Optional[str],
    password: Optional[str],
    verify_ssl: Optional[bool],
    timeout: float,
) -> AuthSettings:
    """Construct settings using environment defaults and CLI overrides."""

    settings = AuthSettings()
    overrides: Dict[str, Any] = {
        "base_url": base_url,
        "username": username,
        "password": password,
        "verify_ssl": verify_ssl,
        "timeout": timeout,
    }
    return settings.merged(**overrides)
