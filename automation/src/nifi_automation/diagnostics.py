"""Diagnostics helpers for inspecting NiFi state."""

from __future__ import annotations

from typing import Dict, List, Tuple

from .client import NiFiClient


def collect_invalid_processors(client: NiFiClient) -> List[Dict[str, object]]:
    """Return metadata for processors that NiFi reports as invalid."""

    invalid: List[Dict[str, object]] = []
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
        flow = data.get("processGroupFlow", {}).get("flow", {})

        for processor in flow.get("processors") or []:
            component = processor.get("component", {})
            status = component.get("validationStatus")
            if status not in {"VALID", "DISABLED"}:
                invalid.append(
                    {
                        "name": component.get("name"),
                        "id": component.get("id"),
                        "type": component.get("type"),
                        "path": "/".join(path),
                        "validationStatus": status,
                        "validationErrors": component.get("validationErrors") or [],
                        "bulletins": processor.get("bulletins") or [],
                    }
                )

        for child in flow.get("processGroups") or []:
            component = child.get("component", {})
            child_id = component.get("id")
            child_name = component.get("name", child_id)
            if child_id:
                stack.append((child_id, path + [child_name]))

    return invalid
