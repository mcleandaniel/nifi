from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict

from nifi_automation.flow_builder import FlowSpec, ProcessGroupSpec, ProcessorSpec, ConnectionSpec, PortSpec
from nifi_automation.infra.diag_adapter import validate_topology_against_spec


class _Resp:
    def __init__(self, payload: Dict[str, Any]):
        self._payload = payload

    def json(self) -> Dict[str, Any]:
        return self._payload


class _FakeHttpClient:
    def __init__(self, flows_by_pg: Dict[str, Dict[str, Any]]):
        self._flows = flows_by_pg

    def get(self, path: str) -> _Resp:  # type: ignore[override]
        # Expect paths like '/flow/process-groups/<id>'
        if not path.startswith("/flow/process-groups/"):
            raise AssertionError(f"Unexpected GET path: {path}")
        pg_id = path.split("/")[-1]
        payload = {
            "processGroupFlow": {
                "flow": self._flows.get(pg_id, {}),
            }
        }
        return _Resp(payload)


class _FakeClient:
    def __init__(self, flows_by_pg: Dict[str, Dict[str, Any]], children_by_parent: Dict[str, Dict[str, str]]):
        self._client = _FakeHttpClient(flows_by_pg)
        self._children = children_by_parent  # parent_id -> {name: id}

    def find_child_process_group_by_name(self, parent_id: str, name: str) -> Dict[str, Any] | None:
        mapping = self._children.get(parent_id, {})
        child_id = mapping.get(name)
        if not child_id:
            return None
        return {"component": {"id": child_id, "name": name}}


def _mk_pg(name: str, processors: list[dict[str, Any]] | None = None,
           connections: list[dict[str, Any]] | None = None,
           in_ports: list[dict[str, Any]] | None = None,
           out_ports: list[dict[str, Any]] | None = None,
           child_groups: list[dict[str, Any]] | None = None) -> Dict[str, Any]:
    return {
        "processors": processors or [],
        "connections": connections or [],
        "inputPorts": in_ports or [],
        "outputPorts": out_ports or [],
        "processGroups": child_groups or [],
    }


def test_topology_validator_flags_missing_processors() -> None:
    # Spec: one child group with one processor expected
    child = ProcessGroupSpec(
        name="Foo",
        position=None,
        comments=None,
        processors=[
            ProcessorSpec(key="p1", name="P1", type="org.example.TypeA", position=None, properties={})
        ],
        connections=[],
        input_ports=[],
        output_ports=[],
    )
    spec = FlowSpec(root_group=ProcessGroupSpec(name="NiFi Flow", position=None, comments=None, child_groups=[child]))

    # Deployed: PG exists but has 0 processors
    flows = {
        "root": {"processGroups": [{"component": {"name": "Foo", "id": "pg-foo"}}]},
        "pg-foo": _mk_pg("Foo", processors=[]),
    }
    children = {"root": {"Foo": "pg-foo"}}
    client = _FakeClient(flows, children)

    result = validate_topology_against_spec(client, spec)  # type: ignore[arg-type]
    assert result["ok"] is False
    errors = {e["error"] for e in result["issues"]}
    assert "processors-missing" in errors


def test_topology_validator_flags_missing_connection() -> None:
    # Spec: two processors and a connection between them
    child = ProcessGroupSpec(
        name="Foo",
        position=None,
        comments=None,
        processors=[
            ProcessorSpec(key="p1", name="P1", type="TypeA", position=None, properties={}),
            ProcessorSpec(key="p2", name="P2", type="TypeB", position=None, properties={}),
        ],
        connections=[ConnectionSpec(name="P1->P2", source="p1", destination="p2", relationships=["success"])],
        input_ports=[],
        output_ports=[],
    )
    spec = FlowSpec(root_group=ProcessGroupSpec(name="NiFi Flow", position=None, comments=None, child_groups=[child]))

    # Deployed: both processors present but no connections
    flows = {
        "root": {"processGroups": [{"component": {"name": "Foo", "id": "pg-foo"}}]},
        "pg-foo": _mk_pg(
            "Foo",
            processors=[
                {"component": {"id": "proc-1", "name": "P1", "type": "TypeA"}},
                {"component": {"id": "proc-2", "name": "P2", "type": "TypeB"}},
            ],
            connections=[],
        ),
    }
    children = {"root": {"Foo": "pg-foo"}}
    client = _FakeClient(flows, children)

    result = validate_topology_against_spec(client, spec)  # type: ignore[arg-type]
    assert result["ok"] is False
    assert any(e["error"] == "connection-missing" for e in result["issues"])  # at least one


def test_topology_validator_flags_missing_ports() -> None:
    child = ProcessGroupSpec(
        name="Foo",
        position=None,
        comments=None,
        processors=[],
        connections=[],
        input_ports=[PortSpec(key="in1", name="IN", position=None)],
        output_ports=[PortSpec(key="out1", name="OUT", position=None)],
    )
    spec = FlowSpec(root_group=ProcessGroupSpec(name="NiFi Flow", position=None, comments=None, child_groups=[child]))

    flows = {
        "root": {"processGroups": [{"component": {"name": "Foo", "id": "pg-foo"}}]},
        "pg-foo": _mk_pg(
            "Foo",
            in_ports=[{"component": {"id": "port-in", "name": "IN"}}],
            out_ports=[],
        ),
    }
    children = {"root": {"Foo": "pg-foo"}}
    client = _FakeClient(flows, children)

    result = validate_topology_against_spec(client, spec)  # type: ignore[arg-type]
    assert result["ok"] is False
    errors = {e["error"] for e in result["issues"]}
    assert "output-port-missing" in errors


def test_topology_validator_flags_empty_group() -> None:
    # Spec defines a child group with no processors/ports/children
    empty = ProcessGroupSpec(
        name="EmptyGroup",
        position=None,
        comments=None,
        processors=[],
        connections=[],
        input_ports=[],
        output_ports=[],
    )
    spec = FlowSpec(root_group=ProcessGroupSpec(name="NiFi Flow", position=None, comments=None, child_groups=[empty]))

    # Deployed: group exists but is empty
    flows = {
        "root": {"processGroups": [{"component": {"name": "EmptyGroup", "id": "pg-empty"}}]},
        "pg-empty": _mk_pg("EmptyGroup"),
    }
    children = {"root": {"EmptyGroup": "pg-empty"}}
    client = _FakeClient(flows, children)

    result = validate_topology_against_spec(client, spec)  # type: ignore[arg-type]
    assert result["ok"] is False
    assert any(e["error"] == "empty-process-group" for e in result["issues"])  # flagged as empty
