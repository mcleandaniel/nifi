"""Status collection adapters for processors, controllers, connections, and ports."""

from __future__ import annotations

from typing import Any, Dict, Iterable, List

from ..diagnostics import _walk_process_groups
from .nifi_client import NiFiClient

__all__ = [
    "fetch_processors",
    "fetch_controllers",
    "fetch_connections",
    "fetch_ports",
]


def _path_to_string(path: Iterable[str]) -> str:
    return "/".join(path)


def fetch_processors(client: NiFiClient) -> Dict[str, Any]:
    items: List[Dict[str, Any]] = []
    for path, flow in _walk_process_groups(client):
        for entity in flow.get("processors") or []:
            component = entity.get("component", {})
            items.append(
                {
                    "id": component.get("id"),
                    "name": component.get("name"),
                    "path": _path_to_string(path),
                    "state": component.get("state"),
                    "validationStatus": component.get("validationStatus"),
                    "validationErrors": component.get("validationErrors") or [],
                    "bulletins": entity.get("bulletins") or [],
                }
            )
    return {"items": items}


def fetch_controllers(client: NiFiClient) -> Dict[str, Any]:
    response = client._client.get(
        "/flow/process-groups/root/controller-services",
        params={"includeInherited": "true"},
    )
    response.raise_for_status()
    services = response.json().get("controllerServices") or []
    items: List[Dict[str, Any]] = []
    for service in services:
        component = service.get("component", {})
        breadcrumb = service.get("breadcrumb", {}).get("breadcrumb", {}).get("name")
        items.append(
            {
                "id": component.get("id"),
                "name": component.get("name"),
                "path": breadcrumb or "root",
                "state": component.get("state"),
                "validationStatus": component.get("validationStatus"),
                "validationErrors": component.get("validationErrors") or [],
            }
        )
    return {"items": items}


def _parse_int(value: Any) -> int:
    try:
        return int(str(value).replace(",", "").strip())
    except (TypeError, ValueError):  # pragma: no cover - defensive
        return 0


def _parse_float(value: Any) -> float:
    try:
        return float(str(value).strip())
    except (TypeError, ValueError):  # pragma: no cover - defensive
        return 0.0


def fetch_connections(client: NiFiClient) -> Dict[str, Any]:
    items: List[Dict[str, Any]] = []
    for path, flow in _walk_process_groups(client):
        for entity in flow.get("connections") or []:
            component = entity.get("component", {})
            snapshot = (entity.get("status") or {}).get("aggregateSnapshot") or {}
            items.append(
                {
                    "id": component.get("id"),
                    "name": component.get("name"),
                    "path": _path_to_string(path),
                    "queuedCount": _parse_int(snapshot.get("queuedCount")),
                    "queuedBytes": _parse_int(snapshot.get("queuedBytes")),
                    "percentUseCount": _parse_float(snapshot.get("percentUseCount")),
                    "percentUseBytes": _parse_float(snapshot.get("percentUseBytes")),
                    "backpressureObjectThreshold": _parse_int(snapshot.get("backPressureObjectThreshold")),
                    "backpressureDataSizeThreshold": snapshot.get("backPressureDataSizeThreshold"),
                }
            )
    return {"items": items}


def fetch_ports(client: NiFiClient) -> Dict[str, Any]:
    """Return combined input/output ports with their run state."""

    items: List[Dict[str, Any]] = []
    for path, flow in _walk_process_groups(client):
        for entity in flow.get("inputPorts") or []:
            comp = entity.get("component", {})
            items.append(
                {
                    "id": comp.get("id"),
                    "name": comp.get("name"),
                    "path": _path_to_string(path),
                    "state": comp.get("state"),
                    "portType": "INPUT",
                    "validationStatus": comp.get("validationStatus"),
                    "validationErrors": comp.get("validationErrors") or [],
                }
            )
        for entity in flow.get("outputPorts") or []:
            comp = entity.get("component", {})
            items.append(
                {
                    "id": comp.get("id"),
                    "name": comp.get("name"),
                    "path": _path_to_string(path),
                    "state": comp.get("state"),
                    "portType": "OUTPUT",
                    "validationStatus": comp.get("validationStatus"),
                    "validationErrors": comp.get("validationErrors") or [],
                }
            )
    return {"items": items}
