"""Controller service manifest management."""

from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.parse import quote

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


class ControllerServiceProvisioningError(RuntimeError):
    """Raised when controller services cannot be provisioned as specified."""


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


def _fetch_service_descriptors(client: NiFiClient, entry: ControllerServiceEntry) -> Dict[str, Any]:
    bundle = entry.bundle
    if not bundle:
        response = client._client.get("/flow/controller-service-types")
        response.raise_for_status()
        for item in response.json().get("controllerServiceTypes", []):
            if item.get("type") == entry.type:
                bundle = item.get("bundle")
                break
    if not bundle:
        return {}

    encoded_type = quote(entry.type, safe="")
    path = (
        f"/flow/controller-service-definition/"
        f"{bundle.get('group')}/{bundle.get('artifact')}/{bundle.get('version')}/{encoded_type}"
    )
    response = client._client.get(path)
    response.raise_for_status()
    definition = response.json() or {}
    return definition.get("propertyDescriptors") or {}


def _slug(text: Optional[str]) -> Optional[str]:
    if text is None:
        return None
    return "".join(ch.lower() for ch in text if ch.isalnum())


def _normalise_properties(
    properties: Dict[str, str],
    descriptors: Dict[str, Any],
    *,
    prefer_display: bool = False,
) -> Dict[str, str]:
    """Map arbitrary manifest keys onto NiFi's descriptor keys (usually display names)."""

    if not properties:
        return {}

    alias_map: Dict[str, tuple[str, Dict[str, Any]]] = {}
    for descriptor_key, descriptor in (descriptors or {}).items():
        target_key = descriptor_key
        display_name = descriptor.get("displayName")
        if prefer_display and display_name:
            target_key = display_name
        aliases = {
            descriptor_key,
            descriptor.get("name"),
            display_name,
            _slug(descriptor_key),
            _slug(descriptor.get("name")),
            _slug(display_name),
        }
        for alias in filter(None, aliases):
            alias_map[alias] = (target_key, descriptor)

    normalised: Dict[str, str] = {}
    unknown: List[str] = []
    for raw_key, raw_value in properties.items():
        mapping = alias_map.get(raw_key) or alias_map.get(_slug(raw_key))
        if not mapping:
            unknown.append(raw_key)
            continue
        target_key, descriptor = mapping
        value = raw_value
        for item in descriptor.get("allowableValues") or []:
            allowable = item.get("allowableValue") or {}
            if raw_value == allowable.get("displayName"):
                value = allowable.get("value")
                break
        normalised[target_key] = value

    if unknown:
        unknown_keys = ", ".join(sorted(set(unknown)))
        raise ControllerServiceProvisioningError(
            f"Manifest references unknown controller service properties: {unknown_keys}"
        )
    return normalised


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
    if existing:
        names = ", ".join(sorted(component.get("component", {}).get("name", "<unknown>") for component in existing))
        raise ControllerServiceProvisioningError(
            f"Expected clean NiFi root with no controller services; found: {names or '<unknown>'}. "
            "Purge the instance before provisioning."
        )

    key_to_id: Dict[str, str] = {}
    manifest_updated = False

    for entry in entries:
        descriptors = _fetch_service_descriptors(client, entry)
        normalised_props = _normalise_properties(entry.properties, descriptors)
        service = client.create_controller_service(
            parent_id="root",
            name=entry.name,
            type_name=entry.type,
            bundle=entry.bundle,
            properties=normalised_props,
        )
        entry.id = service["id"]
        manifest_updated = True

        service_id = service["id"]
        key_to_id[entry.key] = service_id

        if entry.auto_enable:
            client.enable_controller_service(service_id)
            _wait_for_state(client, service_id, "ENABLED")
        else:
            _wait_for_state(client, service_id, "DISABLED")

        entity = client.get_controller_service(service_id)
        validation_errors = entity.get("component", {}).get("validationErrors") or []
        if validation_errors:
            raise ControllerServiceProvisioningError(
                f"Controller service {entry.name} ({service_id}) invalid after provisioning: {validation_errors}"
            )

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


def _wait_for_state(client: NiFiClient, service_id: str, expected_state: str, timeout: float = 30.0) -> None:
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


def _wait_for_stable_state(client: NiFiClient, service_id: str, timeout: float = 30.0) -> str:
    deadline = time.time() + timeout
    while True:
        entity = client.get_controller_service(service_id)
        state = entity["component"].get("state")
        if state not in {"ENABLING", "DISABLING"}:
            return state
        if time.time() > deadline:
            return state
        time.sleep(0.2)
