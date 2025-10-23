"""Deployment adapter bridging the app layer to existing flow builder logic."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

from ..controller_registry import ensure_root_controller_services
from ..flow_builder import FlowSpec, deploy_flow_from_file, load_flow_spec
from .nifi_client import NiFiClient


def _summarize_flow_spec(spec: FlowSpec) -> Dict[str, Any]:
    def count_processors(group) -> int:
        return len(group.processors) + sum(count_processors(child) for child in group.child_groups)

    def collect_group_names(group) -> List[str]:
        names = [group.name]
        for child in group.child_groups:
            names.extend(collect_group_names(child))
        return names

    root = spec.root_group
    def count_connections(group) -> int:
        return len(group.connections) + sum(count_connections(child) for child in group.child_groups)

    def count_input_ports(group) -> int:
        return len(group.input_ports) + sum(count_input_ports(child) for child in group.child_groups)

    def count_output_ports(group) -> int:
        return len(group.output_ports) + sum(count_output_ports(child) for child in group.child_groups)

    return {
        "root_group": root.name,
        "process_group_names": collect_group_names(root),
        "processors": count_processors(root),
        "connections": count_connections(root),
        "input_ports": count_input_ports(root),
        "output_ports": count_output_ports(root),
    }


def deploy_flow(client: NiFiClient, spec_path: Path, *, dry_run: bool = False) -> Dict[str, Any]:
    """Deploy the flow defined at *spec_path* and return deployment metadata."""

    resolved = spec_path if spec_path.is_absolute() else spec_path.resolve()
    spec = load_flow_spec(resolved)

    if dry_run:
        return {"dry_run": True, "summary": _summarize_flow_spec(spec)}

    service_map = ensure_root_controller_services(client)
    # Opportunistically map a pre-existing StandardSSLContextService named 'Workflow SSL'
    # to the alias key used in flow specs ('ssl-context'). This lets flows reference
    # an SSL Context Service created outside the manifest (e.g., by the trust CLI).
    try:
        resp = client._client.get(
            "/flow/process-groups/root/controller-services",
            params={"includeInherited": "false"},
        )
        resp.raise_for_status()
        for svc in resp.json().get("controllerServices") or []:
            comp = svc.get("component", {})
            if (
                comp.get("type") == "org.apache.nifi.ssl.StandardSSLContextService"
                and comp.get("name") == "Workflow SSL"
            ):
                service_map.setdefault("ssl-context", comp.get("id"))
                break
    except Exception:
        # Non-fatal; flows that reference 'ssl-context' will fail if the service is absent.
        pass
    process_group_id = deploy_flow_from_file(
        client,
        resolved,
        controller_service_map=service_map,
    )
    return {
        "dry_run": False,
        "process_group_id": process_group_id,
        "controller_services": service_map,
    }
