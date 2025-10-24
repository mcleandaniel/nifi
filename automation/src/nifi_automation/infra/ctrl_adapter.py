"""Controllers and processor scheduling adapters."""

from __future__ import annotations

import time
from typing import Dict, Iterable, Optional

from ..cleanup import stop_root_processors
from ..flow_builder import start_processors
from .nifi_client import NiFiClient

__all__ = [
    "enable_all_controllers",
    "disable_all_controllers",
    "start_all_processors",
    "stop_all_processors",
    "stop_tools_http_listeners",
]

POLL_INTERVAL = 0.5


def _list_root_controller_services(client: NiFiClient, *, include_inherited: bool = True) -> Iterable[Dict[str, object]]:
    response = client._client.get(
        "/flow/process-groups/root/controller-services",
        params={"includeInherited": str(include_inherited).lower()},
    )
    response.raise_for_status()
    return response.json().get("controllerServices") or []


def _wait_for_controller_state(
    client: NiFiClient,
    service_id: str,
    target_state: str,
    *,
    timeout: float = 60.0,
) -> None:
    deadline = time.time() + timeout
    while True:
        entity = client.get_controller_service(service_id)
        state = entity.get("component", {}).get("state")
        if state == target_state:
            return
        if time.time() > deadline:
            raise RuntimeError(f"Controller service {service_id} did not reach state {target_state} (state={state})")
        time.sleep(POLL_INTERVAL)


def enable_all_controllers(client: NiFiClient, *, timeout: float = 60.0) -> Dict[str, object]:
    """Enable every controller service defined at the root process group."""

    services = list(_list_root_controller_services(client))
    enabled: Dict[str, object] = {"count": 0, "services": []}
    for service in services:
        component = service.get("component") or {}
        service_id = component.get("id")
        state = component.get("state")
        if not service_id:
            continue
        name = (component.get("name") or "")
        if state == "ENABLED":
            continue
        # Skip enabling optional baseline SSL context until configured
        if name == "Workflow SSL":
            continue
        try:
            client.enable_controller_service(service_id)
            _wait_for_controller_state(client, service_id, "ENABLED", timeout=timeout)
            enabled["count"] += 1
            enabled["services"].append(service_id)
        except Exception:
            # Non-fatal: leave service as-is (likely invalid until truststore/params are set)
            continue
    return enabled


def disable_all_controllers(client: NiFiClient, *, timeout: float = 60.0) -> Dict[str, object]:
    """Disable every controller service defined at the root process group."""

    services = list(_list_root_controller_services(client))
    disabled: Dict[str, object] = {"count": 0, "services": []}
    for service in services:
        component = service.get("component") or {}
        service_id = component.get("id")
        state = component.get("state")
        if not service_id:
            continue
        if state == "DISABLED":
            continue
        client.disable_controller_service(service_id)
        _wait_for_controller_state(client, service_id, "DISABLED", timeout=timeout)
        disabled["count"] += 1
        disabled["services"].append(service_id)
    return disabled


def start_all_processors(client: NiFiClient, *, timeout: float = 30.0) -> Dict[str, object]:
    """Schedule the root process group to RUNNING and wait for processors to stabilize."""

    start_processors(client, root_pg_id="root", timeout=timeout)
    return {"scheduled": "RUNNING"}


def stop_all_processors(client: NiFiClient, *, timeout: float = 30.0) -> Dict[str, object]:
    """Schedule the root process group to STOPPED and wait for processors to halt."""

    stop_root_processors(client, timeout=timeout)
    return {"scheduled": "STOPPED"}


def stop_tools_http_listeners(client: NiFiClient) -> Dict[str, object]:
    """Stop any HandleHttpRequest processors inside root-level Tools_* process groups.

    This avoids port conflicts with regular workflow HTTP listeners (e.g., 18081).
    """
    stopped = {"count": 0, "processors": []}
    try:
        resp = client._client.get("/flow/process-groups/root")
        resp.raise_for_status()
        pgs = resp.json().get("processGroupFlow", {}).get("flow", {}).get("processGroups", []) or []
        for pg in pgs:
            comp = pg.get("component", {}) or {}
            pg_name = comp.get("name") or ""
            if not pg_name.startswith("Tools_"):
                continue
            pg_id = comp.get("id")
            if not pg_id:
                continue
            sub = client._client.get(f"/flow/process-groups/{pg_id}")
            sub.raise_for_status()
            flow = sub.json().get("processGroupFlow", {}).get("flow", {})
            for proc in flow.get("processors", []) or []:
                c = proc.get("component", {}) or {}
                if c.get("type") == "org.apache.nifi.processors.standard.HandleHttpRequest":
                    pid = c.get("id")
                    if not pid:
                        continue
                    try:
                        ent = client._client.get(f"/processors/{pid}").json()
                        rev = ent.get("revision", {})
                        client._client.put(f"/processors/{pid}/run-status", json={"revision": rev, "state": "STOPPED"}).raise_for_status()
                        stopped["count"] += 1
                        stopped["processors"].append(pid)
                    except Exception:
                        continue
    except Exception:
        return stopped
    return stopped
