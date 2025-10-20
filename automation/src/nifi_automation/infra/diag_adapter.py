"""Diagnostic helpers for surfacing validation errors and repro commands."""

from __future__ import annotations

from typing import Any, Dict

from ..diagnostics import collect_invalid_ports, collect_invalid_processors
from .nifi_client import NiFiClient


def gather_validation_details(client: NiFiClient) -> Dict[str, Any]:
    """Return invalid component metadata for troubleshooting."""

    return {
        "invalid_processors": collect_invalid_processors(client),
        "invalid_ports": collect_invalid_ports(client),
    }
