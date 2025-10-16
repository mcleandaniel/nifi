"""Utilities for introspecting NiFi controller service metadata via REST."""

from __future__ import annotations

import itertools
import json
from typing import Any, Dict, Iterable, List, Sequence
from urllib.parse import quote

from .client import NiFiClient


def _fetch_controller_service_types(client: NiFiClient) -> Sequence[Dict[str, Any]]:
    response = client._client.get("/flow/controller-service-types")
    response.raise_for_status()
    service_types = response.json().get("controllerServiceTypes") or []
    # Sort for deterministic output (group, artifact, type)
    return sorted(
        service_types,
        key=lambda item: (
            (item.get("bundle") or {}).get("group") or "",
            (item.get("bundle") or {}).get("artifact") or "",
            item.get("type") or "",
        ),
    )


def _fetch_controller_service_definition(
    client: NiFiClient,
    *,
    bundle_group: str,
    bundle_artifact: str,
    bundle_version: str,
    type_name: str,
) -> Dict[str, Any]:
    encoded_type = quote(type_name, safe="")
    path = (
        f"/flow/controller-service-definition/"
        f"{bundle_group}/{bundle_artifact}/{bundle_version}/{encoded_type}"
    )
    response = client._client.get(path)
    response.raise_for_status()
    return response.json() or {}


def _canonical_allowable_values(descriptor: Dict[str, Any]) -> List[Dict[str, Any]]:
    allowed: List[Dict[str, Any]] = []
    for item in descriptor.get("allowableValues") or []:
        allowable = item.get("allowableValue") or {}
        allowed.append(
            {
                "value": allowable.get("value"),
                "displayName": allowable.get("displayName"),
                "description": allowable.get("description"),
            }
        )
    return allowed


def _summarise_required_properties(descriptors: Dict[str, Any]) -> List[Dict[str, Any]]:
    required: List[Dict[str, Any]] = []
    for key, descriptor in descriptors.items():
        if not descriptor.get("required"):
            continue
        required.append(
            {
                "name": descriptor.get("name") or key,
                "displayName": descriptor.get("displayName"),
                "description": descriptor.get("description"),
                "defaultValue": descriptor.get("defaultValue"),
                "allowableValues": _canonical_allowable_values(descriptor),
                "identifiesControllerService": descriptor.get("identifiesControllerService"),
                "sensitive": bool(descriptor.get("sensitive")),
                "supportsExpressionLanguage": bool(descriptor.get("supportsEl")),
                "expressionLanguageScope": descriptor.get("expressionLanguageScope"),
            }
        )
    return sorted(required, key=lambda item: item["name"] or "")


def collect_controller_service_requirements(client: NiFiClient) -> List[Dict[str, Any]]:
    """Return metadata for every controller service type describing required properties."""

    results: List[Dict[str, Any]] = []
    for service in _fetch_controller_service_types(client):
        bundle = service.get("bundle") or {}
        type_name = service.get("type") or ""
        definition = _fetch_controller_service_definition(
            client,
            bundle_group=bundle.get("group") or "",
            bundle_artifact=bundle.get("artifact") or "",
            bundle_version=bundle.get("version") or "",
            type_name=type_name,
        )
        controller_service = definition.get("controllerService") or {}
        descriptors: Dict[str, Any] = controller_service.get("propertyDescriptors") or {}
        if not descriptors:
            descriptors = definition.get("propertyDescriptors") or {}
        required_props = _summarise_required_properties(descriptors)
        results.append(
            {
                "type": type_name,
                "bundle": bundle,
                "description": service.get("description"),
                "requiredProperties": required_props,
            }
        )
    return results


def format_requirements_as_markdown(requirements: Iterable[Dict[str, Any]]) -> str:
    """Render the collected requirements as Markdown."""

    sections: List[str] = []
    for entry in requirements:
        bundle = entry.get("bundle") or {}
        header = (
            f"### `{entry.get('type')}`  \n"
            f"*Bundle:* {bundle.get('group')}/{bundle.get('artifact')}:{bundle.get('version')}\n\n"
        )
        description = entry.get("description") or ""
        if description:
            header += f"{description}\n\n"

        required_props = entry.get("requiredProperties") or []
        if not required_props:
            sections.append(header + "_No required properties._\n")
            continue

        lines = [
            "| Property (canonical) | Display Name | Default | Allowable Values | Notes |",
            "| --- | --- | --- | --- | --- |",
        ]
        for prop in required_props:
            allowable = prop.get("allowableValues") or []
            allowed_text = (
                "<br>".join(
                    f"`{item.get('value')}` ({item.get('displayName')})"
                    for item in allowable
                    if item.get("value") or item.get("displayName")
                )
                or "—"
            )
            notes: List[str] = []
            if prop.get("identifiesControllerService"):
                notes.append(
                    f"Identifies `{prop['identifiesControllerService']}` controller service"
                )
            if prop.get("supportsExpressionLanguage"):
                scope = prop.get("expressionLanguageScope") or "Unknown scope"
                notes.append(f"Supports Expression Language ({scope})")
            if prop.get("sensitive"):
                notes.append("Sensitive")
            if prop.get("description"):
                notes.append(prop["description"])

            lines.append(
                "| {name} | {display} | {default} | {allowed} | {notes} |".format(
                    name=f"`{prop.get('name')}`",
                    display=prop.get("displayName") or "—",
                    default=(
                        f"`{prop.get('defaultValue')}`"
                        if prop.get("defaultValue") is not None
                        else "—"
                    ),
                    allowed=allowed_text,
                    notes="<br>".join(notes) if notes else "—",
                )
            )

        sections.append(header + "\n".join(lines) + "\n")

    return "\n".join(sections)


def format_requirements_as_json(requirements: Iterable[Dict[str, Any]]) -> str:
    """Render the collected requirements as pretty-printed JSON."""

    return json.dumps(list(requirements), indent=2, sort_keys=True)
