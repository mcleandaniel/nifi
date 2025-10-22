import os
import sys
import json
import shutil
import subprocess
from pathlib import Path

import yaml


def _scripts_dir() -> Path:
    # automation/ is test root; scripts live at automation/scripts
    return Path(__file__).resolve().parents[1] / "scripts"


def test_build_ignores_readme_md(tmp_path: Path):
    md_dir = tmp_path / "groups-md"
    md_dir.mkdir(parents=True)

    # README.md should be ignored
    (md_dir / "README.md").write_text("# Documentation only\n", encoding="utf-8")

    # Group MD with two flows
    group_md = md_dir / "Group_One.md"
    group_md.write_text(
        """
        # Group One

        My group description.

        ## 1. Foo
        ```nifidesc
        name: FooFlow
        ```

        ## 2. Bar
        ```nifidesc
        name: BarFlow
        ```
        """.strip()
        + "\n",
        encoding="utf-8",
    )

    # Per-workflow fragments under groups-md/<Group>/flows
    flows_dir = md_dir / "Group_One" / "flows"
    flows_dir.mkdir(parents=True)
    (flows_dir / "FooFlow.yaml").write_text(
        yaml.safe_dump({
            "name": "FooFlow",
            "processors": [],
            "connections": [],
        }, sort_keys=False),
        encoding="utf-8",
    )
    (flows_dir / "BarFlow.yaml").write_text(
        yaml.safe_dump({
            "name": "BarFlow",
            "processors": [],
            "connections": [],
        }, sort_keys=False),
        encoding="utf-8",
    )

    out_yaml = tmp_path / "NiFi_Flow_groups.yaml"
    script = _scripts_dir() / "build_groups_yaml_from_md.py"

    res = subprocess.run(
        [sys.executable, str(script), "--md-dir", str(md_dir), "--out", str(out_yaml), "--root-name", "NiFi Flow"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert res.returncode == 0, res.stderr or res.stdout
    data = yaml.safe_load(out_yaml.read_text(encoding="utf-8"))
    assert data["process_group"]["name"] == "NiFi Flow"
    groups = data["process_group"].get("groups") or []
    assert len(groups) == 1  # README.md ignored, only Group One present
    g = groups[0]
    assert g["name"] == "Group One"
    names = [c.get("name") for c in g.get("process_groups", [])]
    assert names == ["FooFlow", "BarFlow"]


def test_seed_ignores_readme_md(tmp_path: Path):
    # Prepare md-dir with README and a group referencing one flow
    md_dir = tmp_path / "groups-md"
    md_dir.mkdir(parents=True)
    (md_dir / "README.md").write_text("# Doc only\n", encoding="utf-8")
    (md_dir / "Group_A.md").write_text(
        """
        # Group A

        ## 1. A
        ```nifidesc
        name: AlphaFlow
        ```
        """.strip()
        + "\n",
        encoding="utf-8",
    )

    # Prepare flows-dir with single-flow YAMLs (seed source)
    flows_dir = tmp_path / "flows"
    flows_dir.mkdir(parents=True)
    # A file containing AlphaFlow under process_group.process_groups
    single = {
        "process_group": {
            "name": "NiFi Flow",
            "process_groups": [
                {"name": "AlphaFlow", "processors": [], "connections": []}
            ],
        }
    }
    (flows_dir / "alpha.yaml").write_text(yaml.safe_dump(single, sort_keys=False), encoding="utf-8")

    # Seed fragments into groups-md/<Group>/flows
    out_md_dir = md_dir
    script = _scripts_dir() / "seed_groups_yaml_from_single_flows.py"
    res = subprocess.run(
        [
            sys.executable,
            str(script),
            "--md-dir",
            str(md_dir),
            "--flows-dir",
            str(flows_dir),
            "--out-md-dir",
            str(out_md_dir),
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    assert res.returncode == 0, res.stderr or res.stdout

    # README.md is ignored; fragment should exist only for Group A / AlphaFlow
    frag = out_md_dir / "Group_A" / "flows" / "AlphaFlow.yaml"
    assert frag.exists(), f"missing fragment at {frag}"
    spec = yaml.safe_load(frag.read_text(encoding="utf-8"))
    assert spec.get("name") == "AlphaFlow"


def test_generate_stubs_from_md(tmp_path: Path):
    md_dir = tmp_path / "groups-md"
    md_dir.mkdir(parents=True)
    (md_dir / "README.md").write_text("# Doc only\n", encoding="utf-8")
    (md_dir / "Group_B.md").write_text(
        """
        # Group B

        First paragraph is the group description.

        ## 1. Beta
        ```nifidesc
        name: BetaFlow
        ```

        Some narrative here.
        Overview: A simple generator.
        Technical: GenerateFlowFile to LogAttribute.
        """.strip()
        + "\n",
        encoding="utf-8",
    )

    out_md_dir = md_dir
    script = _scripts_dir() / "generate_stubs_from_md.py"
    res = subprocess.run(
        [
            sys.executable,
            str(script),
            "--md-dir",
            str(md_dir),
            "--out-md-dir",
            str(out_md_dir),
            "--phase",
            "draft",
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    assert res.returncode == 0, res.stderr or res.stdout

    frag = out_md_dir / "Group_B" / "flows" / "BetaFlow.yaml"
    assert frag.exists(), "stub was not generated"
    spec = yaml.safe_load(frag.read_text(encoding="utf-8"))
    assert spec.get("name") == "BetaFlow"
    assert spec.get("phase") == "draft"
    # Description should incorporate extracted Overview/Technical when present
    desc = spec.get("description", "")
    assert "Overview:" in desc and "Technical:" in desc

    # Builder should consume the stub and produce grouped YAML
    out_yaml = tmp_path / "NiFi_Flow_groups.yaml"
    builder = _scripts_dir() / "build_groups_yaml_from_md.py"
    res2 = subprocess.run(
        [sys.executable, str(builder), "--md-dir", str(md_dir), "--out", str(out_yaml), "--root-name", "NiFi Flow"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert res2.returncode == 0, res2.stderr or res2.stdout
    data = yaml.safe_load(out_yaml.read_text(encoding="utf-8"))
    groups = data["process_group"].get("groups") or []
    assert any(
        g.get("name") == "Group B" and any(c.get("name") == "BetaFlow" for c in g.get("process_groups", []))
        for g in groups
    )
