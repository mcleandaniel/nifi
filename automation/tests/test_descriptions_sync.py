from __future__ import annotations

from pathlib import Path
import re
from typing import Dict

import pytest

try:
    import yaml  # type: ignore
except Exception:  # pragma: no cover - environment guard
    yaml = None


FLOWS_DIR = Path(__file__).resolve().parents[1] / "flows"
DOC_PATH = Path(__file__).resolve().parents[1] / "flows" / "test-workflow-suite.md"


@pytest.mark.skipif(yaml is None, reason="PyYAML required for description sync test")
def test_yaml_descriptions_present_in_docs_and_aggregate():
    md_text = DOC_PATH.read_text(encoding="utf-8")
    # Parse nifidesc blocks from MD
    blocks = re.findall(r"```nifidesc\n(.*?)```", md_text, flags=re.DOTALL)
    md_desc: Dict[str, str] = {}
    for block in blocks:
        lines = [ln.rstrip("\n") for ln in block.splitlines()]
        if not lines:
            continue
        if not lines[0].lower().startswith("name:"):
            continue
        name = lines[0].split(":", 1)[1].strip()
        desc = "\n".join(lines[1:]).strip()
        if name:
            md_desc[name] = desc

    # Load aggregate NiFi_Flow descriptions for cross-check
    agg = yaml.safe_load((FLOWS_DIR / "NiFi_Flow.yaml").read_text(encoding="utf-8"))
    agg_groups = agg.get("process_group", {}).get("process_groups", []) if isinstance(agg, dict) else []
    agg_desc_by_name: Dict[str, str] = {}
    for g in agg_groups:
        if not isinstance(g, dict):
            continue
        name = g.get("name")
        desc = g.get("description")
        if name and isinstance(desc, str):
            agg_desc_by_name[name] = desc.strip()

    # For each single-flow spec, require:
    #  1) description exists
    #  2) description is present verbatim in the MD file
    #  3) description matches the one in the aggregate NiFi_Flow.yaml for the same PG
    for path in sorted(FLOWS_DIR.glob("*.yaml")):
        if path.name == "NiFi_Flow.yaml":
            continue
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        assert isinstance(data, dict)
        pg = data.get("process_group") or {}
        groups = pg.get("process_groups") or []
        assert groups, f"No process_groups defined in {path.name}"
        # Assume a single top-level child group per file
        g = groups[0]
        name = g.get("name")
        desc = g.get("description")
        assert isinstance(name, str)
        assert isinstance(desc, str) and desc.strip(), f"Missing description in {path.name}"
        desc_norm = desc.strip()
        # Compare exactly to MD block for this flow
        md_block = md_desc.get(name)
        assert md_block is not None, f"Doc missing nifidesc block for {name}"
        # Allow YAML indentation; remove leading whitespace per line for comparison
        desc_norm_md = "\n".join(ln.lstrip() for ln in desc_norm.splitlines())
        assert md_block == desc_norm_md, f"Doc block mismatch for {name}"

        # Match aggregate description when the flow is present in NiFi_Flow.yaml
        agg_desc = agg_desc_by_name.get(name)
        if agg_desc is not None:
            assert agg_desc == desc_norm, f"Description mismatch for {name} between single YAML and aggregate"
