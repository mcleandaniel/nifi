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
from nifi_automation.flow_builder import deploy_flow_from_file, load_flow_spec


pytestmark = pytest.mark.integration


FLOW_FILES: Iterable[Path] = [
    Path("flows/trivial.yaml"),
    Path("flows/simple.yaml"),
]


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


def purge_process_group(client: NiFiClient, pg_id: str, delete_group: bool = False) -> None:
    flow = client._client.get(f"/flow/process-groups/{pg_id}").json()["processGroupFlow"]["flow"]
    response = client._client.get(
        f"/flow/process-groups/{pg_id}/controller-services",
        params={"includeInherited": "false"},
    )
    service_listing: list[dict] = []
    if response.status_code == 200:
        service_listing = response.json().get("controllerServices", [])

    # Recurse into child process groups first
    for child in flow.get("processGroups", []) or []:
        child_id = child["component"]["id"]
        purge_process_group(client, child_id, delete_group=True)

    # Stop all processors to avoid conflicts during deletion
    for processor in flow.get("processors", []) or []:
        proc_id = processor["component"]["id"]
        revision = processor.get("revision") or {}
        body = {"revision": revision, "component": {"id": proc_id, "state": "STOPPED"}}
        client._client.put(f"/processors/{proc_id}", json=body).raise_for_status()

    # Disable & delete controller services defined at this level (after processors stop)
    for service in service_listing or []:
        component = service.get("component", {})
        if component.get("parentGroupId") != pg_id:
            continue
        service_id = component.get("id")
        client.disable_controller_service(service_id)
        # wait for disable to propagate
        for _ in range(20):
            entity = client.get_controller_service(service_id)
            state = entity["component"].get("state")
            if state == "DISABLED":
                break
            time.sleep(0.2)
        client.delete_controller_service(service_id)

    if delete_group:
        client.delete_process_group_recursive(pg_id)


def purge_root(client: NiFiClient) -> None:
    purge_process_group(client, "root", delete_group=False)


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


def test_clear_nifi_instance(nifi_token):
    settings, token = nifi_token
    with NiFiClient(settings, token) as client:
        purge_root(client)


@pytest.fixture
def nifi_environment(nifi_token):
    settings, token = nifi_token
    with NiFiClient(settings, token) as client:
        purge_root(client)
        service_map = ensure_root_controller_services(client)
        yield client, service_map


@pytest.mark.parametrize("spec_path", FLOW_FILES, ids=lambda p: p.stem)
def test_deploy_flow_spec(nifi_environment, spec_path: Path):
    nifi_client, service_map = nifi_environment
    spec = load_flow_spec(spec_path)
    pg_id = deploy_flow_from_file(nifi_client, spec_path, controller_service_map=service_map)

    flow_entity, processors, invalid_initial = wait_for_flow_stabilization(nifi_client, pg_id)
    group_flow = flow_entity["processGroupFlow"]["flow"]

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

def test_create_json_record_services(nifi_token):
    """Provision JsonTreeReader/JsonRecordSetWriter and verify canonical properties only remain."""

    settings, token = nifi_token
    with NiFiClient(settings, token) as client:
        purge_root(client)
        clear_manifest_service_ids()
        service_map = ensure_root_controller_services(client)

        reader_id = service_map["json-reader"]
        writer_id = service_map["json-writer"]

        reader = client.get_controller_service(reader_id)
        reader_component = reader["component"]
        assert reader_component["state"] == "ENABLED"
        reader_props = reader_component.get("properties") or {}
        assert "schema-access-strategy" in reader_props
        assert reader_props.get("Schema Access Strategy") in (None, ""), reader_props
        assert not reader_component.get("validationErrors"), reader_component.get("validationErrors")

        writer = client.get_controller_service(writer_id)
        writer_component = writer["component"]
        assert writer_component["state"] == "ENABLED"
        writer_props = writer_component.get("properties") or {}
        assert "schema-write-strategy" in writer_props, writer_props
        assert writer_props.get("Schema Write Strategy") in (None, ""), writer_props
        assert not writer_component.get("validationErrors"), writer_component.get("validationErrors")

        with MANIFEST_PATH.open("r", encoding="utf-8") as fp:
            manifest_payload = json.load(fp)

        for entry in manifest_payload.get("controller_services", []):
            assert entry.get("id"), f"Manifest entry missing ID: {entry}"
            props = entry.get("properties") or {}
            assert "Schema Write Strategy" not in props
            assert "Schema Access Strategy" not in props
