from pathlib import Path
import textwrap
import pytest

from nifi_automation.flow_builder import load_flow_spec, FlowDeploymentError


def _write(tmp_path: Path, content: str) -> Path:
    p = tmp_path / "spec.yaml"
    p.write_text(textwrap.dedent(content), encoding="utf-8")
    return p


def test_groups_only_parses_and_orders(tmp_path: Path):
    path = _write(
        tmp_path,
        """
        process_group:
          name: NiFi Flow
          groups:
            - name: Group A
              process_groups:
                - name: A1
                  processors: []
                  connections: []
                - name: A2
                  processors: []
                  connections: []
            - name: Group B
              process_groups:
                - name: B1
                  processors: []
                  connections: []
        """,
    )
    spec = load_flow_spec(path)
    names = [c.name for c in spec.root_group.child_groups]
    assert names == ["A1", "A2", "B1"]


def test_legacy_only_parses(tmp_path: Path):
    path = _write(
        tmp_path,
        """
        process_group:
          name: NiFi Flow
          process_groups:
            - name: X
              processors: []
              connections: []
            - name: Y
              processors: []
              connections: []
        """,
    )
    spec = load_flow_spec(path)
    names = [c.name for c in spec.root_group.child_groups]
    assert names == ["X", "Y"]


def test_mixed_groups_and_legacy_unique_names_enforced(tmp_path: Path):
    path = _write(
        tmp_path,
        """
        process_group:
          name: NiFi Flow
          process_groups:
            - name: Dup
              processors: []
              connections: []
          groups:
            - name: G
              process_groups:
                - name: Dup
                  processors: []
                  connections: []
        """,
    )
    with pytest.raises(FlowDeploymentError):
        load_flow_spec(path)

