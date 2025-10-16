#!/usr/bin/env python3
"""Provision JsonTreeReader and JsonRecordSetWriter services and report their state."""

import os
from typing import Dict

from nifi_automation.auth import obtain_access_token
from nifi_automation.client import NiFiClient
from nifi_automation.config import build_settings
from nifi_automation.controller_registry import (
    clear_manifest_service_ids,
    ensure_root_controller_services,
)


def purge_root(client: NiFiClient) -> None:
    flow = client._client.get("/flow/process-groups/root").json()["processGroupFlow"]["flow"]

    for child in flow.get("processGroups", []) or []:
        client.delete_process_group_recursive(child["component"]["id"])

    for processor in flow.get("processors", []) or []:
        proc_id = processor["component"]["id"]
        revision = processor.get("revision") or {}
        body = {"revision": revision, "component": {"id": proc_id, "state": "STOPPED"}}
        client._client.put(f"/processors/{proc_id}", json=body).raise_for_status()

    for service in flow.get("controllerServices", []) or []:
        component = service.get("component", {})
        service_id = component.get("id")
        if not service_id:
            continue
        client.disable_controller_service(service_id)
        client.delete_controller_service(service_id)


def main() -> None:
    os.environ.setdefault("RUN_NIFI_INTEGRATION", "1")
    settings = build_settings(None, None, None, False, 10.0)
    token = obtain_access_token(settings)

    with NiFiClient(settings, token) as client:
        purge_root(client)
        clear_manifest_service_ids()
        service_map: Dict[str, str] = ensure_root_controller_services(client)

        for key, service_id in service_map.items():
            entity = client.get_controller_service(service_id)
            component = entity.get("component", {})
            print(f"Service: {component.get('name')} ({component.get('type')})")
            print(f"  Manifest key: {key}")
            print(f"  State: {component.get('state')}")
            validation_errors = component.get("validationErrors") or []
            if validation_errors:
                print("  Validation errors:")
                for err in validation_errors:
                    print(f"    - {err}")
            else:
                print("  Validation errors: none")
            print("  Properties:")
            for prop_key, value in (component.get("properties") or {}).items():
                print(f"    {prop_key}: {value}")
            print()


if __name__ == "__main__":
    main()
