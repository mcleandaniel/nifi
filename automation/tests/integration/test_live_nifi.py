import json
import os
import time
from pathlib import Path
from typing import Iterable

import pytest

from nifi_automation.auth import obtain_access_token
from nifi_automation.config import build_settings
from nifi_automation.client import NiFiClient
from nifi_automation.controller_registry import (
    MANIFEST_PATH,
    clear_manifest_service_ids,
    ensure_root_controller_services,
)
from nifi_automation.diagnostics import (
    collect_invalid_ports,
    collect_invalid_processors,
    count_processor_states,
)
from nifi_automation.flow_builder import deploy_flow_from_file, load_flow_spec, start_processors


pytestmark = pytest.mark.integration


DEFAULT_FLOW_FILES = [Path("automation/flows/NiFi_Flow.yaml")]
_flow_override = os.getenv("NIFI_FLOW_SPECS")
if _flow_override:
    FLOW_FILES: Iterable[Path] = [
        Path(part.strip()) for part in _flow_override.split(",") if part.strip()
    ] or DEFAULT_FLOW_FILES
else:
    FLOW_FILES = DEFAULT_FLOW_FILES


def wait_for_flow_stabilization(client: NiFiClient, pg_id: str, timeout: float = 5.0):
    deadline = time.time() + timeout
    while True:
        flow_entity = client._client.get(f"/flow/process-groups/{pg_id}").json()
        group_flow = flow_entity["processGroupFlow"]["flow"]
        processors = group_flow.get("processors") or []
        invalid = [
            proc["component"]["name"]
            for proc in processors
            if proc["component"].get("validationStatus") not in {"VALID", "DISABLED"}
        ]
        if not invalid or time.time() > deadline:
            return flow_entity, processors, invalid
        time.sleep(0.25)


@pytest.fixture
def nifi_token():
    if not os.getenv("RUN_NIFI_INTEGRATION"):
        pytest.skip("Set RUN_NIFI_INTEGRATION=1 to run live NiFi tests")
    settings = build_settings(None, None, None, False, 10.0)
    token = obtain_access_token(settings)
    assert token, "Expected NiFi access token"
    return settings, token


def test_fetch_token(nifi_token):
    _, token = nifi_token
    assert token, "Access token should not be empty"


@pytest.fixture
def nifi_environment(nifi_token):
    settings, token = nifi_token
    with NiFiClient(settings, token) as client:
        # Environment must be purged before tests run.
        services = client._client.get(
            "/flow/process-groups/root/controller-services",
            params={"includeInherited": "false"},
        ).json().get("controllerServices") or []
        root_flow = client._client.get("/flow/process-groups/root").json()["processGroupFlow"]["flow"]
        if services or (root_flow.get("processGroups") or []):
            pytest.fail(
                "NiFi environment not clean. Run scripts/purge_nifi_root.py before executing tests."
            )
        service_map = ensure_root_controller_services(client)
        yield client, service_map


@pytest.mark.parametrize("spec_path", FLOW_FILES, ids=lambda p: p.stem)
def test_deploy_flow_spec(nifi_environment, spec_path: Path):
    nifi_client, service_map = nifi_environment
    spec = load_flow_spec(spec_path)
    pg_id = deploy_flow_from_file(nifi_client, spec_path, controller_service_map=service_map)

    expected_pg = "root" if pg_id == "root" else pg_id
    flow_entity, processors, invalid_initial = wait_for_flow_stabilization(nifi_client, expected_pg)
    group_flow = flow_entity["processGroupFlow"]["flow"]

    # Verify child process groups exist and contain processors
    child_groups = {
        pg["component"]["name"]: pg["component"]["id"]
        for pg in group_flow.get("processGroups") or []
    }
    for child_spec in spec.root_group.child_groups:
        assert child_spec.name in child_groups, f"{child_spec.name} PG missing"
        fetched = nifi_client._client.get(f"/flow/process-groups/{child_groups[child_spec.name]}").json()
        sub_flow = fetched["processGroupFlow"]["flow"]
        if child_spec.processors:
            assert sub_flow.get("processors"), f"{child_spec.name} has no processors"
        if child_spec.input_ports:
            port_names = {
                port.get("component", {}).get("name")
                for port in sub_flow.get("inputPorts") or []
            }
            expected = {port.name for port in child_spec.input_ports}
            assert expected.issubset(port_names), f"Missing input ports in {child_spec.name}: {expected - port_names}"
        if child_spec.output_ports:
            port_names = {
                port.get("component", {}).get("name")
                for port in sub_flow.get("outputPorts") or []
            }
            expected = {port.name for port in child_spec.output_ports}
            assert expected.issubset(port_names), f"Missing output ports in {child_spec.name}: {expected - port_names}"
        if child_spec.child_groups:
            nested_names = {
                pg["component"]["name"]
                for pg in sub_flow.get("processGroups") or []
            }
            expected_nested = {nested.name for nested in child_spec.child_groups}
            assert expected_nested.issubset(nested_names), f"Missing nested groups in {child_spec.name}: {expected_nested - nested_names}"

    # Validate controller services exist per manifest
    manifested_services = set(service_map.keys())
    for key in manifested_services:
        service_id = service_map[key]
        entity = nifi_client.get_controller_service(service_id)
        assert entity["component"]["state"] in {"ENABLED", "DISABLED"}

    # Ensure no bulletins or validation errors remain (allow lookup placeholder warnings handled elsewhere)
    bulletins = group_flow.get("bulletins") or []
    assert not bulletins, f"Process group emitted bulletins: {bulletins}"

    assert not invalid_initial, f"Processors invalid after deploy: {invalid_initial}"

    disabled = [
        proc["component"]["name"]
        for proc in processors
        if proc["component"].get("state") == "DISABLED"
    ]
    assert not disabled, f"Processors unexpectedly disabled: {disabled}"

    # Detect overlapping component positions to catch layout regressions
    seen_positions = {}
    overlaps = []
    for proc in processors:
        component = proc["component"]
        position = component.get("position") or {}
        key = (round(position.get("x", 0)), round(position.get("y", 0)))
        if key in seen_positions:
            overlaps.append((seen_positions[key], component.get("name")))
        else:
            seen_positions[key] = component.get("name")
    assert not overlaps, f"Overlapping processors detected: {overlaps}"

    # Controller services should remain enabled with canonical properties
    reader = nifi_client.get_controller_service(service_map["json-reader"])
    reader_component = reader["component"]
    assert reader_component["state"] == "ENABLED"
    reader_props = reader_component.get("properties") or {}
    assert reader_props.get("schema-access-strategy") == "infer-schema", reader_props
    assert reader_props.get("Schema Access Strategy") in (None, ""), reader_props
    assert not reader_component.get("validationErrors"), reader_component.get("validationErrors")

    writer = nifi_client.get_controller_service(service_map["json-writer"])
    writer_component = writer["component"]
    assert writer_component["state"] == "ENABLED"
    writer_props = writer_component.get("properties") or {}
    assert writer_props.get("Schema Write Strategy") == "no-schema", writer_props
    assert writer_props.get("schema-write-strategy") in (None, ""), writer_props
    assert not writer_component.get("validationErrors"), writer_component.get("validationErrors")

    with MANIFEST_PATH.open("r", encoding="utf-8") as fp:
        manifest_payload = json.load(fp)

    for entry in manifest_payload.get("controller_services", []):
        assert entry.get("id"), f"Manifest entry missing ID: {entry}"
        props = entry.get("properties") or {}
        assert "Schema Write Strategy" not in props
        assert "Schema Access Strategy" not in props

    invalid_procs = collect_invalid_processors(nifi_client)
    invalid_ports = collect_invalid_ports(nifi_client)
    assert not invalid_procs, f"Invalid processors detected: {invalid_procs}"
    assert not invalid_ports, f"Invalid ports detected: {invalid_ports}"

    start_processors(nifi_client)

    state_counts = count_processor_states(nifi_client)
    stopped = state_counts.get("STOPPED", 0)
    assert stopped == 0, f"Found {stopped} stopped processors: {state_counts}"
