"""Purge helpers exposing graceful root teardown semantics."""

from __future__ import annotations

import time
from typing import Any, Dict, Optional

import httpx

from ..cleanup import (
    disable_root_controller_services,
    purge_root_process_group,
    stop_root_processors,
)
from .nifi_client import NiFiClient

DROP_POLL_INTERVAL = 0.5
DROP_TIMEOUT = 120.0

__all__ = ["truncate_connections", "graceful_purge"]


def _drop_connection_queue(client: NiFiClient, connection_id: str) -> None:
    response = client._client.post(f"/flowfile-queues/{connection_id}/drop-requests")
    if response.status_code in {404, 409}:
        return
    response.raise_for_status()
    data = response.json() or {}
    drop = data.get("dropRequest") or data
    drop_id = drop.get("id")
    if not drop_id:
        return

    deadline = time.time() + DROP_TIMEOUT
    while True:
        status = client._client.get(f"/flowfile-queues/{connection_id}/drop-requests/{drop_id}")
        if status.status_code == 404:
            break
        status.raise_for_status()
        payload = status.json() or {}
        drop_info = payload.get("dropRequest") or payload
        if drop_info.get("finished") or drop_info.get("state") == "FINISHED":
            break
        if time.time() > deadline:
            raise RuntimeError(f"Timed out truncating queue for connection {connection_id}")
        time.sleep(DROP_POLL_INTERVAL)

    client._client.delete(f"/flowfile-queues/{connection_id}/drop-requests/{drop_id}").raise_for_status()


def _truncate_root_connections(client: NiFiClient) -> Dict[str, Any]:
    truncated: Dict[str, Any] = {"count": 0, "connections": []}
    flow_resp = client._client.get("/flow/process-groups/root")
    flow_resp.raise_for_status()
    flow = flow_resp.json().get("processGroupFlow", {}).get("flow", {}) or {}
    for connection in flow.get("connections") or []:
        component = connection.get("component", {})
        connection_id = component.get("id")
        if not connection_id:
            continue
        try:
            _drop_connection_queue(client, connection_id)
        except httpx.HTTPStatusError as exc:  # pragma: no cover - network handled live
            truncated.setdefault("errors", []).append({"id": connection_id, "error": str(exc)})
            continue
        truncated["count"] += 1
        truncated["connections"].append(connection_id)
    return truncated


def truncate_connections(client: NiFiClient) -> Dict[str, Any]:
    """Drop all FlowFiles from root-level connections without deleting flows."""

    return _truncate_root_connections(client)


def graceful_purge(client: NiFiClient, *, truncate: bool = True) -> Dict[str, Any]:
    """Perform a graceful purge of the NiFi root process group."""

    stop_root_processors(client)
    disable_root_controller_services(client)
    truncate_info: Optional[Dict[str, Any]] = None
    if truncate:
        truncate_info = _truncate_root_connections(client)
    purge_root_process_group(client)
    return {
        "stopped_processors": True,
        "disabled_controller_services": True,
        "truncated_connections": truncate_info,
        "purged": True,
    }
