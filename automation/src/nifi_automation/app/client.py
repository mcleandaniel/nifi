"""Utilities for opening NiFi client sessions from CLI configuration."""

from __future__ import annotations

from contextlib import contextmanager
from typing import Iterator

import httpx

from ..auth import AuthenticationError, obtain_access_token
from ..config import build_settings
from ..infra.nifi_client import NiFiClient
from .errors import HTTPError
from .models import AppConfig


@contextmanager
def open_client(config: AppConfig) -> Iterator[NiFiClient]:
    """Yield a configured :class:`NiFiClient` using CLI/app configuration."""

    settings = build_settings(
        config.base_url,
        config.username,
        config.password,
        verify_ssl=None,
        timeout=config.timeout_seconds,
    )
    token = config.token
    try:
        if not token:
            token = obtain_access_token(settings)
    except AuthenticationError as exc:  # pragma: no cover - network dependent
        raise HTTPError(str(exc)) from exc

    try:
        with NiFiClient.from_settings(settings, token) as client:  # type: ignore[arg-type]
            yield client
    except httpx.HTTPError as exc:  # pragma: no cover - network dependent
        raise HTTPError(str(exc)) from exc
