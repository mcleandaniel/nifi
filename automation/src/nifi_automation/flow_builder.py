"""Utilities for deploying flows from declarative specifications."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional, Set, Tuple

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


@dataclass
class ControllerServiceRequirement:
    processor_key: str
    property_name: str
    service_type: str
    bundle: Optional[Dict[str, str]]


@dataclass
class PreparedProcessor:
    spec: ProcessorSpec
    properties: Dict[str, str]
    auto_terminate: List[str]
    service_requirements: List[ControllerServiceRequirement]
    metadata: Dict[str, Any]


class FlowDeploymentError(RuntimeError):
    """Raised when a flow specification cannot be deployed."""


def _ensure_position(raw: Optional[Iterable[float]], fallback_x: float) -> Tuple[float, float]:
    if raw is None:
        return float(fallback_x), 0.0
    coords = list(raw)
    if len(coords) != 2:
        raise FlowDeploymentError(f"Invalid position coordinates: {raw}")
    return float(coords[0]), float(coords[1])


def _normalize_property_value(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value.strip()
    return str(value)


def _slug(text: Optional[str]) -> Optional[str]:
    if text is None:
        return None
    return "".join(ch.lower() for ch in text if ch.isalnum())


def _build_property_alias_map(descriptors: Mapping[str, Any]) -> Dict[str, str]:
    alias_map: Dict[str, str] = {}
    for key, descriptor in (descriptors or {}).items():
        if not descriptor:
            continue
        aliases = {
            key,
            key.lower() if isinstance(key, str) else key,
            descriptor.get("name"),
            descriptor.get("displayName"),
        }
        slug_inputs = set(filter(None, aliases))
        aliases |= {_slug(item) for item in slug_inputs}
        for alias in filter(None, aliases):
            alias_str = alias if isinstance(alias, str) else str(alias)
            alias_lower = alias_str.lower()
            if alias_lower not in alias_map:
                alias_map[alias_lower] = key
    return alias_map


def _normalize_allowable_value(
    processor_name: str,
    property_name: str,
    value: str,
    allowable: Iterable[Mapping[str, Any]],
) -> str:
    if not value:
        return value
    normalized = value.strip()
    for option in allowable:
        opt_value = option.get("value")
        opt_display = option.get("displayName")
        if normalized == opt_value or normalized == opt_display:
            return opt_value or normalized
    choices = ", ".join(filter(None, {str(option.get("value") or option.get("displayName")) for option in allowable}))
    raise FlowDeploymentError(
        f"Processor '{processor_name}' property '{property_name}' value '{normalized}' is invalid; "
        f"expected one of: {choices or '<<none>>'}"
    )


def validate_and_normalize_properties(
    processor_name: str,
    processor_type: str,
    properties: Mapping[str, Any],
    descriptors: Mapping[str, Any],
    supports_dynamic_properties: bool,
) -> Dict[str, str]:
    normalized: Dict[str, str] = {}
    descriptors = descriptors or {}
    alias_map = _build_property_alias_map(descriptors)
    seen_canonical: Set[str] = set()

    for key, raw_value in properties.items():
        lookup_key = key if isinstance(key, str) else str(key)
        descriptor_key = alias_map.get(lookup_key.lower())
        descriptor = descriptors.get(descriptor_key) if descriptor_key else descriptors.get(lookup_key)
        value = _normalize_property_value(raw_value)
        canonical_key = descriptor_key or lookup_key
        if descriptor is None:
            if supports_dynamic_properties:
                normalized[lookup_key] = value
                continue
            raise FlowDeploymentError(
                f"Processor '{processor_name}' ({processor_type}) does not define property '{key}'"
            )
        allowable = descriptor.get("allowableValues") or []
        if allowable:
            value = _normalize_allowable_value(processor_name, key, value, allowable)
        if canonical_key in seen_canonical:
            raise FlowDeploymentError(
                f"Processor '{processor_name}' ({processor_type}) has multiple definitions for property '{canonical_key}'"
            )
        seen_canonical.add(canonical_key)
        normalized[canonical_key] = value

    for key, descriptor in descriptors.items():
        if not descriptor:
            continue
        required = descriptor.get("required")
        default = descriptor.get("defaultValue")
        value = normalized.get(key, "")
        if required and not value and not default:
            if descriptor.get("typeProvidedByValue"):
                continue
            raise FlowDeploymentError(
                f"Processor '{processor_name}' ({processor_type}) missing required property '{key}'"
            )

    return normalized


def determine_controller_service_requirements(
    processor_key: str,
    descriptors: Mapping[str, Any],
    properties: Mapping[str, str],
) -> List[ControllerServiceRequirement]:
    requirements: List[ControllerServiceRequirement] = []
    for prop_name, descriptor in (descriptors or {}).items():
        if not descriptor:
            continue
        current = properties.get(prop_name, "")
        if current:
            continue
        service_info = descriptor.get("typeProvidedByValue")
        if not service_info:
            continue
        service_type = service_info.get("type")
        if not service_type:
            continue
        bundle = None
        if all(service_info.get(part) for part in ("group", "artifact", "version")):
            bundle = {
                "group": service_info.get("group"),
                "artifact": service_info.get("artifact"),
                "version": service_info.get("version"),
            }
        requirements.append(
            ControllerServiceRequirement(
                processor_key=processor_key,
                property_name=prop_name,
                service_type=service_type,
                bundle=bundle,
            )
        )
    return requirements


def compute_auto_terminate_relationships(
    processor_name: str,
    specified: Iterable[str],
    relationships: Iterable[Mapping[str, Any]],
    connected_relationships: Set[str],
    supports_dynamic_relationships: bool = False,
) -> List[str]:
    specified = list(specified or [])
    relationship_map = {
        (rel.get("name") or "").lower(): rel.get("name")
        for rel in relationships or []
        if rel.get("name")
    }
    known_relationships = set(relationship_map.values())
    result: Set[str] = set()

    for rel in specified:
        canonical = relationship_map.get(rel.lower())
        if canonical is None:
            if supports_dynamic_relationships:
                canonical = rel
            else:
                raise FlowDeploymentError(
                    f"Processor '{processor_name}' references unknown relationship '{rel}' in auto_terminate"
                )
        if canonical in connected_relationships:
            raise FlowDeploymentError(
                f"Processor '{processor_name}' cannot auto-terminate relationship '{rel}' because it is connected"
            )
        result.add(canonical)

    for descriptor in relationships or []:
        name = descriptor.get("name")
        if not name or name in connected_relationships:
            continue
        result.add(name)

    return sorted(result)


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

    def __init__(
        self,
        client: NiFiClient,
        spec: FlowSpec,
        controller_service_map: Optional[Mapping[str, str]] = None,
    ):
        self.client = client
        self.spec = spec
        self.controller_service_map = dict(controller_service_map or {})

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

        prepared_processors = self._prepare_processors()
        self._apply_controller_service_mappings(prepared_processors, self.controller_service_map)

        processor_id_map: Dict[str, str] = {}
        for prepared in prepared_processors:
            spec = prepared.spec
            created = self.client.create_processor(
                parent_id=pg_id,
                name=spec.name,
                type_name=spec.type,
                position=spec.position,
                properties=prepared.properties,
            )
            processor_id_map[spec.key] = created["id"]
            if prepared.auto_terminate:
                self.client.update_processor_autoterminate(created["id"], prepared.auto_terminate)

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

    def _prepare_processors(self) -> List[PreparedProcessor]:
        metadata_by_key: Dict[str, Dict[str, Any]] = {}
        for proc in self.spec.processors:
            metadata_by_key[proc.key] = self.client.get_processor_metadata(proc.type)

        connections_usage = self._collect_connection_usage(metadata_by_key)

        prepared: List[PreparedProcessor] = []
        for proc in self.spec.processors:
            metadata = metadata_by_key[proc.key]
            descriptors = metadata.get("propertyDescriptors") or {}
            normalized = validate_and_normalize_properties(
                processor_name=proc.name,
                processor_type=proc.type,
                properties=proc.properties,
                descriptors=descriptors,
                supports_dynamic_properties=bool(metadata.get("supportsDynamicProperties")),
            )
            requirements = determine_controller_service_requirements(proc.key, descriptors, normalized)
            auto_terminate = compute_auto_terminate_relationships(
                processor_name=proc.name,
                specified=self.spec.auto_terminate.get(proc.key, []),
                relationships=metadata.get("supportedRelationships") or metadata.get("relationships") or [],
                connected_relationships=connections_usage.get(proc.key, set()),
                supports_dynamic_relationships=bool(metadata.get("supportsDynamicRelationships")),
            )
            prepared.append(
                PreparedProcessor(
                    spec=proc,
                    properties=dict(normalized),
                    auto_terminate=auto_terminate,
                    service_requirements=requirements,
                    metadata=metadata,
                )
            )
        return prepared

    def _collect_connection_usage(
        self,
        metadata_by_key: Mapping[str, Mapping[str, Any]],
    ) -> Dict[str, Set[str]]:
        usage: Dict[str, Set[str]] = {proc.key: set() for proc in self.spec.processors}
        for conn in self.spec.connections:
            metadata = metadata_by_key.get(conn.source)
            if metadata is None:
                raise FlowDeploymentError(
                    f"Connection '{conn.name}' references unknown processor '{conn.source}'"
                )
            relationships = metadata.get("supportedRelationships") or metadata.get("relationships") or []
            relationship_map = {
                (rel.get("name") or "").lower(): rel.get("name")
                for rel in relationships
                if rel.get("name")
            }
            supports_dynamic = bool(metadata.get("supportsDynamicRelationships"))
            for rel in conn.relationships:
                canonical = relationship_map.get(rel.lower())
                if canonical is None:
                    if supports_dynamic:
                        canonical = rel
                    else:
                        raise FlowDeploymentError(
                            f"Connection '{conn.name}' references unknown relationship '{rel}' "
                            f"on processor '{conn.source}'"
                        )
                usage.setdefault(conn.source, set()).add(canonical)
        return usage

    def _apply_controller_service_mappings(
        self,
        prepared_processors: Iterable[PreparedProcessor],
        controller_service_id_map: Mapping[str, str],
    ) -> None:
        if not controller_service_id_map:
            return
        for prepared in prepared_processors:
            for prop, value in list(prepared.properties.items()):
                if value in controller_service_id_map:
                    prepared.properties[prop] = controller_service_id_map[value]


def deploy_flow_from_file(
    client: NiFiClient,
    path: Path,
    controller_service_map: Optional[Mapping[str, str]] = None,
) -> str:
    spec = load_flow_spec(path)
    deployer = FlowDeployer(client, spec, controller_service_map=controller_service_map)
    return deployer.deploy()
