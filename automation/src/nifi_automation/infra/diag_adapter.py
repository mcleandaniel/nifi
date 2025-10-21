"""Diagnostic helpers for surfacing validation errors and repro commands."""

from __future__ import annotations

from typing import Any, Dict

from ..diagnostics import _walk_process_groups, collect_invalid_ports, collect_invalid_processors
from .status_adapter import fetch_connections, fetch_processors
from .nifi_client import NiFiClient


def _collect_flow_bulletins(client: NiFiClient) -> list[dict[str, Any]]:
    bulletins: list[dict[str, Any]] = []
    for path, flow in _walk_process_groups(client):
        for b in flow.get("bulletins") or []:
            item = dict(b)
            item["path"] = "/".join(path)
            bulletins.append(item)
    return bulletins


def _collect_processor_bulletins(client: NiFiClient) -> list[dict[str, Any]]:
    bulletins: list[dict[str, Any]] = []
    for proc in fetch_processors(client).get("items", []):
        for b in proc.get("bulletins") or []:
            item = dict(b)
            item.setdefault("path", proc.get("path"))
            item.setdefault("sourceName", proc.get("name"))
            bulletins.append(item)
    return bulletins


def gather_validation_details(client: NiFiClient) -> Dict[str, Any]:
    """Return invalid component metadata plus bulletins and queue snapshots."""

    invalid_processors = collect_invalid_processors(client)
    invalid_ports = collect_invalid_ports(client)
    processor_bulletins = _collect_processor_bulletins(client)
    flow_bulletins = _collect_flow_bulletins(client)
    connections = fetch_connections(client).get("items", [])
    queued = [c for c in connections if int(c.get("queuedCount", 0)) or float(c.get("percentUseCount", 0.0))]

    return {
        "invalid_processors": invalid_processors,
        "invalid_ports": invalid_ports,
        "bulletins": {
            "processors": processor_bulletins,
            "process_groups": flow_bulletins,
        },
        "connections": {
            "blocked_or_nonempty": queued,
            "totals": {
                "all": len(connections),
                "nonempty": len(queued),
            },
        },
    }
