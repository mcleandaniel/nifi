"""Diagnostics helpers for inspecting NiFi state."""

from __future__ import annotations

from typing import Dict, Iterable, Iterator, List, Tuple

from .client import NiFiClient


def _walk_process_groups(client: NiFiClient) -> Iterator[Tuple[List[str], Dict[str, object]]]:
    stack: List[Tuple[str, List[str]]] = []
    root_entity = client._client.get("/flow/process-groups/root")
    root_entity.raise_for_status()
    root_json = root_entity.json()
    root_name = (
        root_json.get("processGroupFlow", {})
        .get("breadcrumb", {})
        .get("breadcrumb", {})
        .get("name", "root")
    )
    stack.append(("root", [root_name]))

    while stack:
        pg_id, path = stack.pop()
        entity = client._client.get(f"/flow/process-groups/{pg_id}")
        entity.raise_for_status()
        data = entity.json() or {}
        flow = data.get("processGroupFlow", {}).get("flow", {}) or {}

        yield path, flow

        for child in flow.get("processGroups") or []:
            component = child.get("component", {})
            child_id = component.get("id")
            child_name = component.get("name", child_id)
            if child_id:
                stack.append((child_id, path + [child_name]))


def _collect_invalid_components(
    elements: Iterable[Dict[str, object]],
    path: List[str],
) -> List[Dict[str, object]]:
    invalid: List[Dict[str, object]] = []
    for element in elements or []:
        component = element.get("component", {})
        status = component.get("validationStatus")
        errors = component.get("validationErrors") or []
        if status in {"VALID", "DISABLED"}:
            continue
        if status is None and not errors:
            continue
            invalid.append(
                {
                    "name": component.get("name"),
                    "id": component.get("id"),
                    "type": component.get("type"),
                    "path": "/".join(path),
                    "validationStatus": status,
                    "validationErrors": errors,
                    "bulletins": element.get("bulletins") or [],
                }
            )
    return invalid


def collect_invalid_processors(client: NiFiClient) -> List[Dict[str, object]]:
    """Return metadata for processors that NiFi reports as invalid."""

    invalid: List[Dict[str, object]] = []
    for path, flow in _walk_process_groups(client):
        invalid.extend(_collect_invalid_components(flow.get("processors") or [], path))
    return invalid


def collect_invalid_ports(client: NiFiClient) -> List[Dict[str, object]]:
    """Return metadata for input/output ports that NiFi reports as invalid."""

    invalid: List[Dict[str, object]] = []
    for path, flow in _walk_process_groups(client):
        invalid.extend(_collect_invalid_components(flow.get("inputPorts") or [], path))
        invalid.extend(_collect_invalid_components(flow.get("outputPorts") or [], path))
    return invalid
