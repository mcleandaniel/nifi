"""Describe helpers for processor/controller types using live NiFi metadata."""

from __future__ import annotations

import sys
from typing import Any, Dict, List

from .client import open_client
from .errors import BadInputError
from .models import AppConfig, CommandResult


def _simplify_descriptors(descriptors: Dict[str, Any]) -> List[Dict[str, Any]]:
    items: List[Dict[str, Any]] = []
    for key, desc in (descriptors or {}).items():
        display = desc.get("displayName") or desc.get("name") or key
        allowable = []
        for opt in desc.get("allowableValues") or []:
            av = opt.get("allowableValue") or {}
            name = av.get("displayName") or av.get("value")
            if name is None:
                name = opt.get("displayName") or opt.get("value")
            if name is not None:
                allowable.append(name)
        items.append(
            {
                "key": key,
                "displayName": display,
                "required": bool(desc.get("required")),
                "default": desc.get("defaultValue"),
                "sensitive": bool(desc.get("sensitive")),
                "allowable": allowable,
                "supportsExpressionLanguage": bool(desc.get("supportsEl")),
            }
        )
    items.sort(key=lambda d: (not d.get("required", False), str(d.get("displayName") or "")))
    return items


def describe_processor(*, config: AppConfig) -> CommandResult:
    """Return the canonical property list for a processor type."""

    proc_type = config.proc_type
    if not proc_type:
        raise BadInputError("--type is required for 'describe processors'")

    with open_client(config) as client:
        meta = client.get_processor_metadata(proc_type)
    descriptors = meta.get("propertyDescriptors") or {}
    simplified = _simplify_descriptors(descriptors)
    return CommandResult(
        message=f"{proc_type}: {len(simplified)} properties",
        data={"type": proc_type, "properties": simplified},
    )

