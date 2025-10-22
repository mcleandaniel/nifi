"""Diagnostic helpers for surfacing validation errors and repro commands."""

from __future__ import annotations

from typing import Any, Dict, List, Tuple, Mapping, Set

from ..diagnostics import _walk_process_groups, collect_invalid_ports, collect_invalid_processors
from .status_adapter import fetch_connections, fetch_processors
from .nifi_client import NiFiClient
from ..flow_builder import FlowSpec, load_flow_spec


def _collect_flow_bulletins(client: NiFiClient) -> list[dict[str, Any]]:
    bulletins: list[dict[str, Any]] = []
    for path, flow in _walk_process_groups(client):
        for b in flow.get("bulletins") or []:
            item = dict(b)
            item["path"] = "/".join(path)
            bulletins.append(item)
    return bulletins


def _collect_processor_bulletins(client: NiFiClient) -> list[dict[str, Any]]:
    bulletins: list[dict[str, Any]] = []
    for proc in fetch_processors(client).get("items", []):
        for b in proc.get("bulletins") or []:
            item = dict(b)
            item.setdefault("path", proc.get("path"))
            item.setdefault("sourceName", proc.get("name"))
            bulletins.append(item)
    return bulletins


def gather_validation_details(client: NiFiClient) -> Dict[str, Any]:
    """Return invalid component metadata plus bulletins and queue snapshots."""

    invalid_processors = collect_invalid_processors(client)
    invalid_ports = collect_invalid_ports(client)
    processor_bulletins = _collect_processor_bulletins(client)
    flow_bulletins = _collect_flow_bulletins(client)
    connections = fetch_connections(client).get("items", [])
    queued = [c for c in connections if int(c.get("queuedCount", 0)) or float(c.get("percentUseCount", 0.0))]

    return {
        "invalid_processors": invalid_processors,
        "invalid_ports": invalid_ports,
        "bulletins": {
            "processors": processor_bulletins,
            "process_groups": flow_bulletins,
        },
        "connections": {
            "blocked_or_nonempty": queued,
            "totals": {
                "all": len(connections),
                "nonempty": len(queued),
            },
        },
    }


# ----- Topology validation against a FlowSpec -----

def _get_pg_flow(client: NiFiClient, pg_id: str) -> Dict[str, Any]:
    return client._client.get(f"/flow/process-groups/{pg_id}").json().get("processGroupFlow", {}).get("flow", {})


def _count_pg_contents(client: NiFiClient, pg_id: str) -> Dict[str, int]:
    flow = _get_pg_flow(client, pg_id)
    return {
        "processors": len(flow.get("processors") or []),
        "connections": len(flow.get("connections") or []),
        "input_ports": len(flow.get("inputPorts") or []),
        "output_ports": len(flow.get("outputPorts") or []),
        "child_groups": len(flow.get("processGroups") or []),
    }


def _expected_counts(group) -> Dict[str, int]:
    return {
        "processors": len(group.processors),
        "connections": len(group.connections),
        "input_ports": len(group.input_ports),
        "output_ports": len(group.output_ports),
        "child_groups": len(group.child_groups),
    }


def _validate_group_recursive(
    client: NiFiClient, parent_pg_id: str, group, path: Tuple[str, ...], issues: List[Dict[str, Any]]
) -> None:
    # Locate child PG by name under the parent
    child = client.find_child_process_group_by_name(parent_pg_id, group.name)
    if child is None:
        issues.append(
            {
                "path": "/".join(path + (group.name,)),
                "error": "missing-process-group",
                "message": f"Process group '{group.name}' not found under '{path[-1] if path else 'root'}'",
            }
        )
        return
    child_id = child.get("component", {}).get("id") or child.get("id")
    flow = _get_pg_flow(client, child_id)
    counts_actual = {
        "processors": len(flow.get("processors") or []),
        "connections": len(flow.get("connections") or []),
        "input_ports": len(flow.get("inputPorts") or []),
        "output_ports": len(flow.get("outputPorts") or []),
        "child_groups": len(flow.get("processGroups") or []),
    }
    counts_expected = _expected_counts(group)

    # Processor presence check
    if counts_expected["processors"] > 0 and counts_actual["processors"] == 0:
        issues.append(
            {
                "path": "/".join(path + (group.name,)),
                "error": "processors-missing",
                "message": "Expected processors > 0 but found 0",
                "expected": counts_expected,
                "actual": counts_actual,
            }
        )

    # Empty process group check (no processors, ports, or children deployed)
    if (
        counts_actual["processors"] == 0
        and counts_actual["input_ports"] == 0
        and counts_actual["output_ports"] == 0
        and counts_actual["child_groups"] == 0
    ):
        issues.append(
            {
                "path": "/".join(path + (group.name,)),
                "error": "empty-process-group",
                "message": "No processors, ports, or child groups deployed",
                "expected": counts_expected,
                "actual": counts_actual,
            }
        )

    # Count mismatches for visibility (non-fatal unless all processors are missing)
    for key in ("processors", "connections", "input_ports", "output_ports", "child_groups"):
        if counts_expected[key] != counts_actual[key]:
            issues.append(
                {
                    "path": "/".join(path + (group.name,)),
                    "error": f"count-mismatch:{key}",
                    "message": f"{key} expected {counts_expected[key]} but found {counts_actual[key]}",
                    "expected": counts_expected,
                    "actual": counts_actual,
                }
            )

    # Presence checks: processors by (name,type)
    actual_procs: Set[Tuple[str, str]] = {
        (
            (item.get("component") or {}).get("name", ""),
            (item.get("component") or {}).get("type", ""),
        )
        for item in (flow.get("processors") or [])
    }

    for spec_proc in group.processors:
        pair = (spec_proc.name, spec_proc.type)
        if pair not in actual_procs:
            issues.append(
                {
                    "path": "/".join(path + (group.name,)),
                    "error": "processor-missing",
                    "message": f"Processor '{spec_proc.name}' ({spec_proc.type}) not found",
                    "expected": {"name": spec_proc.name, "type": spec_proc.type},
                }
            )

    # Presence checks: ports by name
    actual_in_ports = {
        (item.get("component") or {}).get("name") for item in (flow.get("inputPorts") or [])
    }
    actual_out_ports = {
        (item.get("component") or {}).get("name") for item in (flow.get("outputPorts") or [])
    }
    for spec_port in group.input_ports:
        if spec_port.name not in actual_in_ports:
            issues.append(
                {
                    "path": "/".join(path + (group.name,)),
                    "error": "input-port-missing",
                    "message": f"Input port '{spec_port.name}' not found",
                }
            )
    for spec_port in group.output_ports:
        if spec_port.name not in actual_out_ports:
            issues.append(
                {
                    "path": "/".join(path + (group.name,)),
                    "error": "output-port-missing",
                    "message": f"Output port '{spec_port.name}' not found",
                }
            )

    # Presence checks: connections by (source_name -> dest_name)
    # Build id->name map for processors and ports in this flow, plus immediate child
    # group ports used in cross-boundary connections.
    id_to_name: Dict[str, str] = {}
    for item in (flow.get("processors") or []):
        comp = item.get("component") or {}
        id_to_name[comp.get("id", "")] = comp.get("name", "")
    for item in (flow.get("inputPorts") or []):
        comp = item.get("component") or {}
        id_to_name[comp.get("id", "")] = comp.get("name", "")
    for item in (flow.get("outputPorts") or []):
        comp = item.get("component") or {}
        id_to_name[comp.get("id", "")] = comp.get("name", "")

    # Include child PG ports (parent->child and child->parent connections reference these IDs)
    for child_item in (flow.get("processGroups") or []):
        child_comp = child_item.get("component") or {}
        c_id = child_comp.get("id")
        if not c_id:
            continue
        child_flow = _get_pg_flow(client, c_id)
        for item in (child_flow.get("inputPorts") or []):
            comp = item.get("component") or {}
            id_to_name[comp.get("id", "")] = comp.get("name", "")
        for item in (child_flow.get("outputPorts") or []):
            comp = item.get("component") or {}
            id_to_name[comp.get("id", "")] = comp.get("name", "")

    actual_pairs: Set[Tuple[str, str]] = set()
    for conn in (flow.get("connections") or []):
        comp = conn.get("component") or {}
        src = (comp.get("source") or {}).get("id", "")
        dst = (comp.get("destination") or {}).get("id", "")
        actual_pairs.add((id_to_name.get(src, ""), id_to_name.get(dst, "")))

    # Map spec keys -> names for processors and ports
    key_to_name: Dict[str, str] = {p.key: p.name for p in group.processors}
    key_to_name.update({p.key: p.name for p in group.input_ports})
    key_to_name.update({p.key: p.name for p in group.output_ports})
    # Include immediate child groups' ports for cross-boundary connections
    for child_spec in group.child_groups:
        for port in child_spec.input_ports:
            key_to_name[port.key] = port.name
        for port in child_spec.output_ports:
            key_to_name[port.key] = port.name

    for conn in group.connections:
        src_name = key_to_name.get(conn.source, conn.source)
        dst_name = key_to_name.get(conn.destination, conn.destination)
        if (src_name, dst_name) not in actual_pairs:
            issues.append(
                {
                    "path": "/".join(path + (group.name,)),
                    "error": "connection-missing",
                    "message": f"Connection '{conn.name}' {src_name} -> {dst_name} not found",
                }
            )

    # Recurse into children
    for child_spec in group.child_groups:
        _validate_group_recursive(client, child_id, child_spec, path + (group.name,), issues)


def validate_topology_against_spec(client: NiFiClient, spec: FlowSpec) -> Dict[str, Any]:
    """Compare deployed NiFi topology under root against the provided spec.

    Returns a payload with an 'issues' list and a boolean 'ok'.
    """
    issues: List[Dict[str, Any]] = []
    root_id = "root"
    # Validate each top-level child group declared in the spec
    for child in spec.root_group.child_groups:
        _validate_group_recursive(client, root_id, child, (spec.root_group.name,), issues)

    # Mark ok=true only when no issues were found
    return {"ok": len(issues) == 0, "issues": issues}


def validate_deployed_topology(client: NiFiClient, spec_path) -> Dict[str, Any]:
    """Load spec at spec_path and validate deployed topology against it."""
    spec = load_flow_spec(spec_path)
    return validate_topology_against_spec(client, spec)
