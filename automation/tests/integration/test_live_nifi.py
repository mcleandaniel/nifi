import os
from pathlib import Path
from uuid import uuid4

import pytest

from nifi_automation.config import build_settings
from nifi_automation.auth import obtain_access_token
from nifi_automation.client import NiFiClient
from nifi_automation.flow_builder import deploy_flow_from_file


pytestmark = pytest.mark.integration


@pytest.mark.skipif(
    not os.getenv("RUN_NIFI_INTEGRATION"),
    reason="Set RUN_NIFI_INTEGRATION=1 to run NiFi integration tests against https://localhost:8443/nifi-api.",
)
def test_deploy_flow_and_resolve_metadata(tmp_path: Path):
    """Deploy a sample flow, confirm controller-service stubs exist, and auto-termination is inferred."""

    spec_path = tmp_path / "integration-flow.yaml"
    process_group_name = f"Integration-{uuid4()}"
    spec_path.write_text(
        "\n".join(
            [
                "process_group:",
                f"  name: {process_group_name}",
                "  position: [0, 0]",
                "",
                "processors:",
                "  - id: generate",
                "    name: Generate FlowFile",
                "    type: org.apache.nifi.processors.standard.GenerateFlowFile",
                "    position: [0, 0]",
                "    properties:",
                '      Batch Size: "1"',
                "  - id: lookup",
                "    name: Lookup Attribute",
                "    type: org.apache.nifi.processors.standard.LookupAttribute",
                "    position: [400, 0]",
                "    properties:",
                "      include-empty-values: \"false\"",
                "  - id: log",
                "    name: Log Attribute",
                "    type: org.apache.nifi.processors.standard.LogAttribute",
                "    position: [800, 0]",
                "",
                "connections:",
                "  - name: generate-to-lookup",
                "    source: generate",
                "    destination: lookup",
                "    relationships: [success]",
                "  - name: lookup-to-log",
                "    source: lookup",
                "    destination: log",
                "    relationships: [matched]",
                "",
                "auto_terminate: {}",
                "",
            ]
        ),
        encoding="utf-8",
    )

    settings = build_settings(None, None, None, False, 10.0)
    token = obtain_access_token(settings)
    with NiFiClient(settings, token) as client:
        pg_id = deploy_flow_from_file(client, spec_path)

        flow_entity = client._client.get(f"/flow/process-groups/{pg_id}").json()
        processors = flow_entity["processGroupFlow"]["flow"]["processors"]
        lookup_proc = next(proc for proc in processors if proc["component"]["name"] == "Lookup Attribute")
        lookup_config = lookup_proc["component"]["config"]

        service_id = lookup_config["properties"]["lookup-service"]
        assert service_id, "Lookup Attribute should reference an auto-created controller service"
        assert set(lookup_config["autoTerminatedRelationships"]) == {"failure", "unmatched"}

        controller_service = client._client.get(f"/controller-services/{service_id}").json()
        assert controller_service["component"]["state"] == "DISABLED"
        assert controller_service["component"]["name"].endswith("-Stub")

        # Ensure no bulletins (warnings/errors) were raised on this flow
        group_flow = flow_entity["processGroupFlow"]["flow"]
        bulletins = group_flow.get("bulletins") or []
        assert not bulletins, f"Process group emitted bulletins: {bulletins}"

        # Confirm all processors are valid and not disabled
        invalid_details = []
        for proc in processors:
            status = proc["component"].get("validationStatus")
            if status == "VALID":
                continue
            errors = proc["component"].get("validationErrors") or []
            # Allow the Lookup Attribute processor to remain invalid because the stub controller service stays disabled
            if (
                proc["component"].get("name") == "Lookup Attribute"
                and errors
                and all("controller service" in err.lower() for err in errors)
            ):
                continue
            invalid_details.append((proc["component"].get("name"), status, errors))
        assert not invalid_details, f"Unexpected processor validation issues: {invalid_details}"

        disabled = [
            proc["component"]["name"]
            for proc in processors
            if proc["component"].get("state") == "DISABLED"
        ]
        assert not disabled, f"Processors unexpectedly disabled: {disabled}"

        # Detect overlapping processors or process groups (exact same rounded position)
        def ensure_no_overlaps(items, label):
            seen: dict[tuple[int, int], str] = {}
            overlaps: list[tuple[str, str]] = []
            for item in items:
                component = item["component"]
                position = component.get("position") or {}
                key = (round(position.get("x", 0)), round(position.get("y", 0)))
                if key in seen:
                    overlaps.append((seen[key], component.get("name")))
                else:
                    seen[key] = component.get("name")
            assert not overlaps, f"Overlapping {label}: {overlaps}"

        ensure_no_overlaps(processors, "processors")
        ensure_no_overlaps(group_flow.get("processGroups", []), "process groups")

        pg_entity = client.get_process_group(pg_id)
        client.delete_process_group(pg_id, pg_entity["revision"]["version"])
