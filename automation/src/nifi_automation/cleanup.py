"""Reusable helpers for stopping, disabling, and purging NiFi root resources."""

from __future__ import annotations

import time
from typing import Dict, Iterable, Tuple

import httpx

from .client import NiFiClient

CLIENT_ID = "nifi-automation"

__all__ = [
    "stop_root_processors",
    "disable_root_controller_services",
    "purge_process_group",
    "purge_root_process_group",
]


def stop_root_processors(client: NiFiClient, *, timeout: float = 30.0) -> None:
    """Schedule the root process group to STOPPED and wait until all processors halt."""

    client.schedule_process_group("root", "STOPPED")
    deadline = time.time() + timeout
    while True:
        response = client._client.get("/flow/process-groups/root")
        response.raise_for_status()
        flow = response.json().get("processGroupFlow", {}).get("flow", {}) or {}
        processors = flow.get("processors") or []
        states = {proc.get("component", {}).get("state") for proc in processors if proc.get("component")}
        if not states or states <= {"STOPPED", "DISABLED"}:
            return
        if time.time() > deadline:
            raise RuntimeError(f"Processors still active: {states}")
        time.sleep(0.2)


def disable_root_controller_services(client: NiFiClient, *, timeout: float = 30.0) -> None:
    """Disable all controller services defined at the root process group."""

    response = client._client.get(
        "/flow/process-groups/root/controller-services",
        params={"includeInherited": "false"},
    )
    response.raise_for_status()
    services = response.json().get("controllerServices") or []
    for service in services:
        component = service.get("component") or {}
        service_id = component.get("id")
        if not service_id:
            continue
        # Retry disable to tolerate 409 revision/state conflicts
        for attempt in range(6):
            try:
                client.disable_controller_service(service_id)
                break
            except httpx.HTTPStatusError as exc:
                if exc.response is not None and exc.response.status_code == 409 and attempt < 5:
                    time.sleep(0.5)
                    continue
                raise
        deadline = time.time() + timeout
        while True:
            entity = client.get_controller_service(service_id)
            state = entity.get("component", {}).get("state")
            if state == "DISABLED":
                break
            if time.time() > deadline:
                raise RuntimeError(f"Controller service {service_id} stuck in state {state}")
            time.sleep(0.2)


def _drop_connection_queue(client: NiFiClient, connection_id: str, timeout: float = 60.0) -> None:
    response = client._client.post(f"/flowfile-queues/{connection_id}/drop-requests")
    if response.status_code in {404, 409}:
        return
    response.raise_for_status()
    payload = response.json() or {}
    drop = payload.get("dropRequest") or payload
    drop_id = drop.get("id")
    if not drop_id:
        return

    deadline = time.time() + timeout
    while True:
        status = client._client.get(f"/flowfile-queues/{connection_id}/drop-requests/{drop_id}")
        if status.status_code == 404:
            break
        status.raise_for_status()
        drop_status = (status.json() or {}).get("dropRequest") or {}
        if drop_status.get("finished") or drop_status.get("state") == "FINISHED":
            break
        if time.time() > deadline:
            raise RuntimeError(f"Timed out dropping FlowFile queue for connection {connection_id}")
        time.sleep(0.5)

    client._client.delete(f"/flowfile-queues/{connection_id}/drop-requests/{drop_id}").raise_for_status()


def _delete_connection(client: NiFiClient, connection_id: str) -> None:
    entity = client._client.get(f"/connections/{connection_id}")
    if entity.status_code == 404:
        return
    entity.raise_for_status()
    revision = entity.json().get("revision") or {}
    params = {"version": revision.get("version", 0), "clientId": CLIENT_ID}
    client._client.delete(f"/connections/{connection_id}", params=params).raise_for_status()


def _stop_processor(client: NiFiClient, processor_id: str) -> None:
    entity = client._client.get(f"/processors/{processor_id}")
    if entity.status_code == 404:
        return
    entity.raise_for_status()
    processor = entity.json()
    revision = processor.get("revision") or {}
    body = {"revision": revision, "component": {"id": processor_id, "state": "STOPPED"}}
    client._client.put(f"/processors/{processor_id}", json=body).raise_for_status()
    deadline = time.time() + 30.0
    while True:
        status_resp = client._client.get(f"/processors/{processor_id}")
        if status_resp.status_code == 404:
            return
        status_resp.raise_for_status()
        state = status_resp.json().get("component", {}).get("state")
        if state == "STOPPED":
            return
        if time.time() > deadline:
            raise RuntimeError(f"Processor {processor_id} did not stop within timeout (state={state})")
        time.sleep(0.2)


def _delete_processor(client: NiFiClient, processor_id: str) -> None:
    entity = client._client.get(f"/processors/{processor_id}")
    if entity.status_code == 404:
        return
    entity.raise_for_status()
    revision = entity.json().get("revision") or {}
    params = {"version": revision.get("version", 0), "clientId": CLIENT_ID}
    client._client.delete(f"/processors/{processor_id}", params=params).raise_for_status()


def _disable_and_delete_service(client: NiFiClient, service_id: str) -> None:
    try:
        client.disable_controller_service(service_id)
    except Exception:
        pass
    deadline = time.time() + 60.0
    while True:
        entity = client.get_controller_service(service_id)
        state = entity.get("component", {}).get("state")
        if state == "DISABLED":
            break
        if time.time() > deadline:
            raise RuntimeError(f"Controller service {service_id} did not disable within timeout (state={state})")
        time.sleep(0.5)

    revision = entity.get("revision") or {}
    params = {"version": revision.get("version", 0), "clientId": CLIENT_ID}
    client._client.delete(f"/controller-services/{service_id}", params=params).raise_for_status()


def _disable_port(client: NiFiClient, port_id: str, port_type: str, timeout: float = 30.0) -> None:
    path = "/input-ports" if port_type == "INPUT_PORT" else "/output-ports"
    client._update_port_state(port_id, port_type, "DISABLED")
    deadline = time.time() + timeout
    while True:
        entity = client._client.get(f"{path}/{port_id}")
        if entity.status_code == 404:
            return
        entity.raise_for_status()
        state = entity.json().get("component", {}).get("state")
        if state == "DISABLED":
            return
        if time.time() > deadline:
            raise RuntimeError(f"Port {port_id} did not disable within timeout (state={state})")
        time.sleep(0.2)


def _delete_port_with_retry(client: NiFiClient, port_id: str, port_type: str, retries: int = 5) -> None:
    path = "/input-ports" if port_type == "INPUT_PORT" else "/output-ports"
    for attempt in range(retries):
        entity = client._client.get(f"{path}/{port_id}")
        if entity.status_code == 404:
            return
        entity.raise_for_status()
        revision = entity.json().get("revision") or {}
        params = {"version": revision.get("version", 0), "clientId": CLIENT_ID}
        response = client._client.delete(f"{path}/{port_id}", params=params)
        if response.status_code == 404:
            return
        try:
            response.raise_for_status()
            return
        except httpx.HTTPStatusError as exc:
            if exc.response is not None and exc.response.status_code == 409 and attempt < retries - 1:
                time.sleep(0.5)
                continue
            raise


def purge_process_group(client: NiFiClient, pg_id: str, *, delete_group: bool = False) -> None:
    response = client._client.get(f"/flow/process-groups/{pg_id}")
    response.raise_for_status()
    group_flow = response.json().get("processGroupFlow") or {}
    flow = group_flow.get("flow") or {}

    # Delete labels first (cosmetic components)
    for label in flow.get("labels") or []:
        comp = label.get("component", {})
        label_id = comp.get("id")
        if label_id:
            try:
                entity = client._client.get(f"/labels/{label_id}")
                if entity.status_code != 404:
                    entity.raise_for_status()
                    revision = entity.json().get("revision") or {}
                    params = {"version": revision.get("version", 0), "clientId": CLIENT_ID}
                    client._client.delete(f"/labels/{label_id}", params=params).raise_for_status()
            except Exception:
                pass

    for processor in flow.get("processors") or []:
        proc_id = processor.get("component", {}).get("id")
        if proc_id:
            _stop_processor(client, proc_id)

    for connection in flow.get("connections") or []:
        conn_id = connection.get("component", {}).get("id")
        if not conn_id:
            continue
        _drop_connection_queue(client, conn_id)
        _delete_connection(client, conn_id)

    services_resp = client._client.get(
        f"/flow/process-groups/{pg_id}/controller-services",
        params={"includeInherited": "false"},
    )
    services_resp.raise_for_status()
    for service in services_resp.json().get("controllerServices") or []:
        service_id = service.get("component", {}).get("id")
        if service_id:
            _disable_and_delete_service(client, service_id)

    for port in flow.get("inputPorts") or []:
        component = port.get("component", {})
        port_id = component.get("id")
        if port_id:
            _disable_port(client, port_id, "INPUT_PORT")
            _delete_port_with_retry(client, port_id, "INPUT_PORT")

    for port in flow.get("outputPorts") or []:
        component = port.get("component", {})
        port_id = component.get("id")
        if port_id:
            _disable_port(client, port_id, "OUTPUT_PORT")
            _delete_port_with_retry(client, port_id, "OUTPUT_PORT")

    for processor in flow.get("processors") or []:
        proc_id = processor.get("component", {}).get("id")
        if proc_id:
            _delete_processor(client, proc_id)

    for child in flow.get("processGroups") or []:
        child_id = child.get("component", {}).get("id")
        if child_id:
            purge_process_group(client, child_id, delete_group=True)

    if delete_group and pg_id != "root":
        client.delete_process_group_recursive(pg_id)


def purge_root_process_group(client: NiFiClient) -> None:
    purge_process_group(client, "root", delete_group=False)
