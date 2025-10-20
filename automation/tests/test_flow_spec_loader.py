from __future__ import annotations

from pathlib import Path

import pytest

from nifi_automation.flow_builder import FlowDeploymentError, load_flow_spec


def test_load_sample_flow_spec() -> None:
    sample_path = Path(__file__).parent / "data" / "NiFi_Flow_sample.yaml"
    try:
        spec = load_flow_spec(sample_path)
    except FlowDeploymentError as exc:
        if "PyYAML is required" in str(exc):
            pytest.fail("PyYAML must be installed for flow specification loading tests.")
        raise

    assert spec.root_group.name == "NiFi Flow"
    child_names = [child.name for child in spec.root_group.child_groups]
    assert "TrivialFlow" in child_names
    first_child = spec.root_group.child_groups[0]
    assert first_child.position == (0.0, 0.0)
    assert first_child.processors[0].name == "GenerateFlowFile"
