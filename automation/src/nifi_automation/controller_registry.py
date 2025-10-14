"""Controller service manifest management."""

from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

from .client import NiFiClient


MANIFEST_PATH = (
    Path(__file__).resolve().parents[2] / "manifest" / "controller-services.json"
)


@dataclass
class ControllerServiceEntry:
    key: str
    name: str
    type: str
    properties: Dict[str, str] = field(default_factory=dict)
    auto_enable: bool = True
    bundle: Optional[Dict[str, str]] = None
    id: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ControllerServiceEntry":
        return cls(
            key=data["key"],
            name=data["name"],
            type=data["type"],
            properties=data.get("properties") or {},
            auto_enable=bool(data.get("auto_enable", True)),
            bundle=data.get("bundle"),
            id=data.get("id"),
        )

    def to_dict(self) -> Dict[str, Any]:
        payload: Dict[str, Any] = {
            "key": self.key,
            "name": self.name,
            "type": self.type,
        }
        if self.properties:
            payload["properties"] = self.properties
        if not self.auto_enable:
            payload["auto_enable"] = self.auto_enable
        if self.bundle:
            payload["bundle"] = self.bundle
        if self.id:
            payload["id"] = self.id
        return payload


def _load_manifest_entries() -> List[ControllerServiceEntry]:
    if not MANIFEST_PATH.exists():
        MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
        with MANIFEST_PATH.open("w", encoding="utf-8") as fp:
            json.dump({"controller_services": []}, fp, indent=2)
    with MANIFEST_PATH.open("r", encoding="utf-8") as fp:
        data = json.load(fp) or {}
    entries = data.get("controller_services") or []
    return [ControllerServiceEntry.from_dict(item) for item in entries]


def _save_manifest_entries(entries: List[ControllerServiceEntry]) -> None:
    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    payload = {"controller_services": [entry.to_dict() for entry in entries]}
    with MANIFEST_PATH.open("w", encoding="utf-8") as fp:
        json.dump(payload, fp, indent=2)


def ensure_root_controller_services(client: NiFiClient) -> Dict[str, str]:
    """Ensure all manifest controller services exist at the NiFi root PG.

    Returns a mapping of manifest keys to NiFi controller service IDs.
    """

    entries = _load_manifest_entries()
    if not entries:
        return {}

    response = client._client.get(
        "/flow/process-groups/root/controller-services",
        params={"includeInherited": "false"},
    )
    response.raise_for_status()
    existing = response.json().get("controllerServices") or []
    existing_by_id = {item["id"]: item for item in existing}
    existing_by_name = {item["component"]["name"]: item for item in existing}

    key_to_id: Dict[str, str] = {}
    manifest_updated = False

    for entry in entries:
        service_component: Optional[Dict[str, Any]] = None
        if entry.id and entry.id in existing_by_id:
            service_component = existing_by_id[entry.id]["component"]
        elif entry.name in existing_by_name:
            service_component = existing_by_name[entry.name]["component"]
            entry.id = service_component["id"]
            manifest_updated = True

        if service_component is None:
            service = client.create_controller_service(
                parent_id="root",
                name=entry.name,
                type_name=entry.type,
                bundle=entry.bundle,
                properties=entry.properties,
            )
            entry.id = service["id"]
            manifest_updated = True
            service_component = service
        else:
            service_entity = client.get_controller_service(service_component["id"])
            current_state = service_entity["component"].get("state")
            if current_state in {"ENABLING", "DISABLING"}:
                current_state = _wait_for_stable_state(client, service_component["id"])
            desired_properties = entry.properties or {}
            current_props = service_entity["component"].get("properties") or {}
            if desired_properties and desired_properties != current_props:
                reenable_after_update = current_state == "ENABLED"
                if reenable_after_update:
                    client.disable_controller_service(service_component["id"])
                    _wait_for_state(client, service_component["id"], "DISABLED")
                    service_entity = client.get_controller_service(service_component["id"])
                update_body = {
                    "revision": service_entity["revision"],
                    "component": {
                        "id": service_component["id"],
                        "properties": desired_properties,
                    },
                }
                client._client.put(
                    f"/controller-services/{service_component['id']}",
                    json=update_body,
                ).raise_for_status()
                if reenable_after_update:
                    client.enable_controller_service(service_component["id"])

        service_id = entry.id
        key_to_id[entry.key] = service_id

        expected_state = "ENABLED" if entry.auto_enable else "DISABLED"
        entity = client.get_controller_service(service_id)
        current_state = entity["component"].get("state")
        if current_state in {"ENABLING", "DISABLING"}:
            current_state = _wait_for_stable_state(client, service_id)
        if expected_state == "ENABLED" and current_state != "ENABLED":
            client.enable_controller_service(service_id)
            _wait_for_state(client, service_id, "ENABLED")
        elif expected_state != "ENABLED" and current_state == "ENABLED":
            client.disable_controller_service(service_id)
            _wait_for_state(client, service_id, "DISABLED")
        else:
            if current_state != expected_state:
                _wait_for_state(client, service_id, expected_state)

    if manifest_updated:
        _save_manifest_entries(entries)

    return key_to_id


def clear_manifest_service_ids() -> None:
    """Remove cached NiFi UUIDs from the manifest entries."""

    entries = _load_manifest_entries()
    changed = False
    for entry in entries:
        if entry.id is not None:
            entry.id = None
            changed = True
    if changed:
        _save_manifest_entries(entries)


def _wait_for_state(client: NiFiClient, service_id: str, expected_state: str, timeout: float = 5.0) -> None:
    deadline = time.time() + timeout
    while True:
        entity = client.get_controller_service(service_id)
        state = entity["component"].get("state")
        if state == expected_state:
            return
        if time.time() > deadline:
            raise RuntimeError(
                f"Controller service {service_id} did not reach state {expected_state}; current state {state}"
            )
        time.sleep(0.2)


def _wait_for_stable_state(client: NiFiClient, service_id: str, timeout: float = 5.0) -> str:
    deadline = time.time() + timeout
    while True:
        entity = client.get_controller_service(service_id)
        state = entity["component"].get("state")
        if state not in {"ENABLING", "DISABLING"}:
            return state
        if time.time() > deadline:
            return state
        time.sleep(0.2)
