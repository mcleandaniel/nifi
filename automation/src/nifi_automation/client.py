"""Thin HTTP client for NiFi REST interactions."""

from __future__ import annotations

from contextlib import AbstractContextManager
from typing import Any, Dict, List, Optional

import httpx

from .config import AuthSettings


class NiFiClient(AbstractContextManager["NiFiClient"]):
    """Context manager wrapper around ``httpx.Client`` with NiFi helpers."""

    def __init__(self, settings: AuthSettings, token: str):
        headers = {"Authorization": f"Bearer {token}"}
        verify_flag = settings.verify_ssl
        if isinstance(verify_flag, str):
            verify_flag = verify_flag.lower() not in {"false", "0", "no", "off"}
        self._client = httpx.Client(
            base_url=str(settings.base_url),
            verify=verify_flag,
            timeout=settings.timeout,
            headers=headers,
        )
        self._bundle_cache: Dict[str, Dict[str, str]] = {}

    def get_root_flow(self) -> Dict[str, Any]:
        response = self._client.get("/flow/process-groups/root")
        response.raise_for_status()
        return response.json()

    def find_child_process_group_by_name(self, parent_id: str, name: str) -> Optional[Dict[str, Any]]:
        response = self._client.get(f"/flow/process-groups/{parent_id}")
        response.raise_for_status()
        flow = response.json().get("processGroupFlow", {}).get("flow", {})
        for item in flow.get("processGroups", []) or []:
            component = item.get("component", {})
            if component.get("name") == name:
                return item
        return None

    def get_process_group(self, pg_id: str) -> Dict[str, Any]:
        response = self._client.get(f"/process-groups/{pg_id}")
        response.raise_for_status()
        return response.json()

    def create_process_group(self, parent_id: str, name: str, position: tuple[float, float]) -> Dict[str, Any]:
        body = {
            "revision": {"version": 0},
            "component": {
                "name": name,
                "position": {"x": position[0], "y": position[1]},
            },
        }
        response = self._client.post(f"/process-groups/{parent_id}/process-groups", json=body)
        response.raise_for_status()
        return response.json()["component"]

    def delete_process_group(self, pg_id: str, version: int) -> None:
        params = {"version": str(version), "clientId": "nifi-automation", "recursive": "true"}
        response = self._client.delete(f"/process-groups/{pg_id}", params=params)
        response.raise_for_status()

    def _resolve_bundle(self, type_name: str) -> Dict[str, str]:
        if type_name in self._bundle_cache:
            return self._bundle_cache[type_name]
        response = self._client.get("/flow/processor-types")
        response.raise_for_status()
        processor_types = response.json().get("processorTypes", [])
        for item in processor_types:
            if item.get("type") == type_name:
                bundle = item.get("bundle")
                if not bundle:
                    break
                self._bundle_cache[type_name] = bundle
                return bundle
        raise ValueError(f"Processor type not found: {type_name}")

    def create_processor(
        self,
        parent_id: str,
        name: str,
        type_name: str,
        position: tuple[float, float],
        properties: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        bundle = self._resolve_bundle(type_name)
        body = {
            "revision": {"version": 0},
            "component": {
                "name": name,
                "type": type_name,
                "bundle": bundle,
                "position": {"x": position[0], "y": position[1]},
                "config": {
                    "properties": properties or {},
                    "schedulingPeriod": "0 sec",
                    "schedulingStrategy": "TIMER_DRIVEN",
                },
            },
        }
        response = self._client.post(f"/process-groups/{parent_id}/processors", json=body)
        response.raise_for_status()
        return response.json()["component"]

    def update_processor_autoterminate(self, processor_id: str, relationships: List[str]) -> None:
        entity = self._client.get(f"/processors/{processor_id}").json()
        revision = entity.get("revision", {})
        component = entity.get("component", {})
        existing = component.get("config", {}).get("autoTerminatedRelationships") or []
        updated = sorted(set(existing) | set(relationships))
        body = {
            "revision": revision,
            "component": {
                "id": processor_id,
                "config": {"autoTerminatedRelationships": updated},
            },
        }
        response = self._client.put(f"/processors/{processor_id}", json=body)
        response.raise_for_status()

    def create_connection(
        self,
        parent_id: str,
        name: str,
        source_id: str,
        destination_id: str,
        relationships: List[str],
    ) -> Dict[str, Any]:
        body = {
            "revision": {"version": 0},
            "component": {
                "name": name,
                "source": {
                    "id": source_id,
                    "type": "PROCESSOR",
                    "groupId": parent_id,
                },
                "destination": {
                    "id": destination_id,
                    "type": "PROCESSOR",
                    "groupId": parent_id,
                },
                "selectedRelationships": relationships,
                "flowFileExpiration": "0 sec",
                "backPressureObjectThreshold": 10000,
                "backPressureDataSizeThreshold": "1 GB",
                "loadBalanceStrategy": "DO_NOT_LOAD_BALANCE",
                "loadBalancePartitionAttribute": "",
                "loadBalanceCompression": "DO_NOT_COMPRESS",
                "bendPoints": [],
            },
        }
        response = self._client.post(f"/process-groups/{parent_id}/connections", json=body)
        response.raise_for_status()
        return response.json()["component"]

    def close(self) -> None:
        self._client.close()

    def __exit__(self, exc_type, exc, tb) -> Optional[bool]:  # pragma: no cover - trivial
        self.close()
        return None
