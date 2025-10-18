"""Thin HTTP client for NiFi REST interactions."""

from __future__ import annotations

import time
from contextlib import AbstractContextManager
from typing import Any, Dict, List, Optional
from urllib.parse import quote

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
        self._processor_metadata_cache: Dict[str, Dict[str, Any]] = {}
        self._controller_service_bundle_cache: Dict[str, Dict[str, str]] = {}

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

    def delete_process_group_recursive(self, pg_id: str) -> None:
        # Attempt to stop components before deletion to avoid conflicts
        try:
            self._client.put(f"/flow/process-groups/{pg_id}", json={"id": pg_id, "state": "STOPPED"}).raise_for_status()
        except httpx.HTTPStatusError:
            pass
        for _ in range(5):
            entity = self.get_process_group(pg_id)
            revision = entity.get("revision", {})
            version = revision.get("version")
            if version is None:
                raise RuntimeError(f"Unable to determine revision for process group {pg_id}")
            try:
                self.delete_process_group(pg_id, version)
                return
            except httpx.HTTPStatusError as exc:
                if exc.response.status_code != 409:
                    raise
                time.sleep(0.5)
        # Final attempt, let exception propagate if it still fails
        entity = self.get_process_group(pg_id)
        revision = entity.get("revision", {})
        version = revision.get("version")
        self.delete_process_group(pg_id, version)

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

    def get_processor_metadata(self, type_name: str) -> Dict[str, Any]:
        bundle = self._resolve_bundle(type_name)
        bundle_group = bundle.get("group")
        bundle_artifact = bundle.get("artifact")
        bundle_version = bundle.get("version")
        cache_key = f"{type_name}|{bundle_group}|{bundle_artifact}|{bundle_version}"
        if cache_key in self._processor_metadata_cache:
            return self._processor_metadata_cache[cache_key]
        encoded_type = quote(type_name, safe="")
        path = f"/flow/processor-definition/{bundle_group}/{bundle_artifact}/{bundle_version}/{encoded_type}"
        response = self._client.get(path)
        response.raise_for_status()
        data = response.json()
        self._processor_metadata_cache[cache_key] = data
        return data

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

    def _resolve_controller_service_bundle(
        self,
        type_name: str,
        bundle_hint: Optional[Dict[str, str]] = None,
    ) -> Dict[str, str]:
        if bundle_hint:
            bundle = {
                "group": bundle_hint.get("group"),
                "artifact": bundle_hint.get("artifact"),
                "version": bundle_hint.get("version"),
            }
            if all(bundle.values()):
                self._controller_service_bundle_cache[type_name] = bundle
                return bundle
        if type_name in self._controller_service_bundle_cache:
            return self._controller_service_bundle_cache[type_name]
        response = self._client.get("/flow/controller-service-types")
        response.raise_for_status()
        service_types = response.json().get("controllerServiceTypes", [])
        for item in service_types:
            if item.get("type") == type_name:
                bundle = item.get("bundle")
                if bundle:
                    self._controller_service_bundle_cache[type_name] = bundle
                    return bundle
        raise ValueError(f"Controller service type not found: {type_name}")

    def create_controller_service(
        self,
        parent_id: str,
        name: str,
        type_name: str,
        bundle: Optional[Dict[str, str]] = None,
        properties: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        resolved_bundle = self._resolve_controller_service_bundle(type_name, bundle)
        body = {
            "revision": {"version": 0},
            "component": {
                "name": name,
                "type": type_name,
                "bundle": resolved_bundle,
                "parentGroupId": parent_id,
                "properties": properties or {},
            },
        }
        response = self._client.post(f"/process-groups/{parent_id}/controller-services", json=body)
        response.raise_for_status()
        return response.json()["component"]

    def get_controller_service(self, service_id: str) -> Dict[str, Any]:
        response = self._client.get(f"/controller-services/{service_id}")
        response.raise_for_status()
        return response.json()

    def enable_controller_service(self, service_id: str) -> None:
        entity = self.get_controller_service(service_id)
        revision = entity.get("revision") or {}
        body = {
            "revision": revision,
            "state": "ENABLED",
        }
        response = self._client.put(f"/controller-services/{service_id}/run-status", json=body)
        response.raise_for_status()

    def disable_controller_service(self, service_id: str) -> None:
        entity = self.get_controller_service(service_id)
        revision = entity.get("revision") or {}
        body = {
            "revision": revision,
            "state": "DISABLED",
        }
        response = self._client.put(f"/controller-services/{service_id}/run-status", json=body)
        response.raise_for_status()

    def delete_controller_service(self, service_id: str) -> None:
        entity = self.get_controller_service(service_id)
        revision = entity.get("revision") or {}
        version = revision.get("version")
        params = {"version": str(version), "clientId": "nifi-automation"}
        response = self._client.delete(f"/controller-services/{service_id}", params=params)
        response.raise_for_status()

    def get_controller_service_candidates(
        self,
        api_type: str,
        api_bundle: Optional[Dict[str, str]] = None,
    ) -> List[Dict[str, Any]]:
        params: Dict[str, str] = {"serviceType": api_type}
        if api_bundle:
            if api_bundle.get("group"):
                params["serviceBundleGroup"] = api_bundle["group"]
            if api_bundle.get("artifact"):
                params["serviceBundleArtifact"] = api_bundle["artifact"]
            if api_bundle.get("version"):
                params["serviceBundleVersion"] = api_bundle["version"]
        response = self._client.get("/flow/controller-service-types", params=params)
        response.raise_for_status()
        return response.json().get("controllerServiceTypes", [])

    def get_controller_service_definition(
        self,
        bundle: Dict[str, str],
        type_name: str,
    ) -> Dict[str, Any]:
        group = bundle.get("group")
        artifact = bundle.get("artifact")
        version = bundle.get("version")
        encoded_type = quote(type_name, safe="")
        path = f"/flow/controller-service-definition/{group}/{artifact}/{version}/{encoded_type}"
        response = self._client.get(path)
        response.raise_for_status()
        return response.json()

    def close(self) -> None:
        self._client.close()

    def __exit__(self, exc_type, exc, tb) -> Optional[bool]:  # pragma: no cover - trivial
        self.close()
        return None
