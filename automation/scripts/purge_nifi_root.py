#!/usr/bin/env python3
"""Utility script to purge the NiFi root process group and controller services."""

from __future__ import annotations

import argparse
import sys
import time
from typing import Iterable

from nifi_automation.auth import obtain_access_token
from nifi_automation.client import NiFiClient
from nifi_automation.config import build_settings


CLIENT_ID = "nifi-automation"


def _drop_connection_queue(client: NiFiClient, connection_id: str, timeout: float = 60.0) -> None:
    """Request a FlowFile drop for the given connection and wait for completion."""

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
        status_payload = status.json() or {}
        drop_status = status_payload.get("dropRequest") or status_payload
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


def purge_process_group(client: NiFiClient, pg_id: str, *, delete_group: bool = False) -> None:
    """Recursively purge the specified process group."""

    response = client._client.get(f"/flow/process-groups/{pg_id}")
    response.raise_for_status()
    group_flow = response.json().get("processGroupFlow") or {}
    flow = group_flow.get("flow") or {}

    for child in flow.get("processGroups") or []:
        child_id = child.get("component", {}).get("id")
        if not child_id:
            continue
        purge_process_group(client, child_id, delete_group=True)

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

    for processor in flow.get("processors") or []:
        proc_id = processor.get("component", {}).get("id")
        if proc_id:
            _delete_processor(client, proc_id)

    if delete_group and pg_id != "root":
        client.delete_process_group_recursive(pg_id)


def purge_root(client: NiFiClient) -> None:
    purge_process_group(client, "root", delete_group=False)


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Purge the NiFi root process group and controller services.")
    parser.add_argument(
        "--timeout",
        type=float,
        default=60.0,
        help="Timeout (seconds) for queue drops and service disablement waits.",
    )
    args = parser.parse_args(list(argv) if argv is not None else None)

    settings = build_settings(None, None, None, False, 10.0)
    token = obtain_access_token(settings)

    with NiFiClient(settings, token) as client:
        purge_root(client)

    print("NiFi root purged successfully.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
