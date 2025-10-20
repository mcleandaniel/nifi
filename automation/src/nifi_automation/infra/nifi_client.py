"""Adapter shim for constructing NiFi clients used by the app layer."""

from __future__ import annotations

from typing import Any

from ..client import NiFiClient as _NiFiClient
from ..config import AuthSettings


class NiFiClient(_NiFiClient):  # pragma: no cover - placeholder subclass
    """Thin alias to the existing client until additional adaptation is required."""

    @classmethod
    def from_settings(cls, settings: AuthSettings, token: str) -> "NiFiClient":
        return cls(settings, token)
