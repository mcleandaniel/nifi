"""Utilities for deploying flows from declarative specifications."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

import yaml

from .client import NiFiClient


@dataclass
class ProcessorSpec:
    key: str
    name: str
    type: str
    position: Tuple[float, float]
    properties: Dict[str, str]


@dataclass
class ConnectionSpec:
    name: str
    source: str
    destination: str
    relationships: List[str]


@dataclass
class FlowSpec:
    process_group_name: str
    process_group_position: Tuple[float, float]
    processors: List[ProcessorSpec]
    connections: List[ConnectionSpec]
    auto_terminate: Dict[str, List[str]]


class FlowDeploymentError(RuntimeError):
    """Raised when a flow specification cannot be deployed."""


def _ensure_position(raw: Optional[Iterable[float]], fallback_x: float) -> Tuple[float, float]:
    if raw is None:
        return float(fallback_x), 0.0
    coords = list(raw)
    if len(coords) != 2:
        raise FlowDeploymentError(f"Invalid position coordinates: {raw}")
    return float(coords[0]), float(coords[1])


def load_flow_spec(path: Path) -> FlowSpec:
    data = yaml.safe_load(path.read_text())
    if not isinstance(data, dict):
        raise FlowDeploymentError("Flow specification must be a mapping")

    pg_info = data.get("process_group") or {}
    name = pg_info.get("name")
    if not name:
        raise FlowDeploymentError("process_group.name is required")
    pg_position = _ensure_position(pg_info.get("position"), 0.0)

    processors_data = data.get("processors") or []
    if not processors_data:
        raise FlowDeploymentError("At least one processor must be defined")

    processors: List[ProcessorSpec] = []
    seen_ids: set[str] = set()
    for idx, item in enumerate(processors_data):
        if not isinstance(item, dict):
            raise FlowDeploymentError("Processor definitions must be mappings")
        key = item.get("id")
        if not key:
            raise FlowDeploymentError("Processor missing 'id'")
        if key in seen_ids:
            raise FlowDeploymentError(f"Duplicate processor id: {key}")
        seen_ids.add(key)
        proc = ProcessorSpec(
            key=key,
            name=item.get("name", key),
            type=item.get("type"),
            position=_ensure_position(item.get("position"), idx * 400.0),
            properties=item.get("properties") or {},
        )
        if not proc.type:
            raise FlowDeploymentError(f"Processor {key} missing 'type'")
        processors.append(proc)

    auto_terminate = data.get("auto_terminate") or {}
    connections_data = data.get("connections") or []
    connections: List[ConnectionSpec] = []
    for item in connections_data:
        if not isinstance(item, dict):
            raise FlowDeploymentError("Connections must be mappings")
        source = item.get("source")
        destination = item.get("destination")
        if source not in seen_ids or destination not in seen_ids:
            raise FlowDeploymentError(
                f"Connection references unknown processors: {source} -> {destination}"
            )
        relationships = item.get("relationships") or ["success"]
        connections.append(
            ConnectionSpec(
                name=item.get("name", f"{source}-to-{destination}"),
                source=source,
                destination=destination,
                relationships=list(relationships),
            )
        )

    return FlowSpec(
        process_group_name=name,
        process_group_position=pg_position,
        processors=processors,
        connections=connections,
        auto_terminate={key: list(value) for key, value in auto_terminate.items()}
    )


class FlowDeployer:
    """Deploys flow specifications using the NiFi REST API."""

    def __init__(self, client: NiFiClient, spec: FlowSpec):
        self.client = client
        self.spec = spec

    def deploy(self) -> str:
        """Create the process group and all processors/connections. Returns the new PG ID."""

        root_pg_id = "root"
        existing = self.client.find_child_process_group_by_name(root_pg_id, self.spec.process_group_name)
        if existing:
            self._delete_existing(existing)

        pg = self.client.create_process_group(
            parent_id=root_pg_id,
            name=self.spec.process_group_name,
            position=self.spec.process_group_position,
        )
        pg_id = pg["id"]

        processor_id_map: Dict[str, str] = {}
        for proc in self.spec.processors:
            created = self.client.create_processor(
                parent_id=pg_id,
                name=proc.name,
                type_name=proc.type,
                position=proc.position,
                properties=proc.properties,
            )
            processor_id_map[proc.key] = created["id"]
            auto = self.spec.auto_terminate.get(proc.key)
            if auto:
                self.client.update_processor_autoterminate(created["id"], auto)

        for conn in self.spec.connections:
            self.client.create_connection(
                parent_id=pg_id,
                name=conn.name,
                source_id=processor_id_map[conn.source],
                destination_id=processor_id_map[conn.destination],
                relationships=conn.relationships,
            )

        return pg_id

    def _delete_existing(self, pg_entity: Dict[str, object]) -> None:
        component = pg_entity.get("component", {})
        revision = pg_entity.get("revision", {})
        pg_id = component.get("id")
        if not pg_id:
            return
        version = revision.get("version")
        if version is None:
            # fetch full entity to obtain revision
            entity = self.client.get_process_group(pg_id)
            revision = entity.get("revision", {})
            version = revision.get("version")
        if version is None:
            raise FlowDeploymentError("Unable to determine revision for existing process group")
        self.client.delete_process_group(pg_id, version)


def deploy_flow_from_file(client: NiFiClient, path: Path) -> str:
    spec = load_flow_spec(path)
    deployer = FlowDeployer(client, spec)
    return deployer.deploy()
