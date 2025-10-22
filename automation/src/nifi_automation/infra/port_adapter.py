"""Port orchestration helpers (start/stop) for input/output ports."""

from __future__ import annotations

from typing import Dict

from .nifi_client import NiFiClient
from .status_adapter import fetch_ports


def start_all_ports(client: NiFiClient) -> Dict[str, int]:
    items = fetch_ports(client)["items"]
    count = 0
    for item in items:
        port_id = str(item.get("id") or "")
        port_type = str(item.get("portType") or "")
        if not port_id or not port_type:
            continue
        client._update_port_state(port_id, "INPUT_PORT" if port_type == "INPUT" else "OUTPUT_PORT", "RUNNING")
        count += 1
    return {"count": count}


def stop_all_ports(client: NiFiClient) -> Dict[str, int]:
    items = fetch_ports(client)["items"]
    count = 0
    for item in items:
        port_id = str(item.get("id") or "")
        port_type = str(item.get("portType") or "")
        if not port_id or not port_type:
            continue
        client._update_port_state(port_id, "INPUT_PORT" if port_type == "INPUT" else "OUTPUT_PORT", "STOPPED")
        count += 1
    return {"count": count}

