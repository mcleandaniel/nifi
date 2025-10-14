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

        pg_entity = client.get_process_group(pg_id)
        client.delete_process_group(pg_id, pg_entity["revision"]["version"])
