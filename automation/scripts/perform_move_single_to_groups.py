#!/usr/bin/env python3
"""Overwrite grouped fragments with single-flow specs (one-off tool).

WARNING: This script overwrites files under automation/flows/groups-md/*/flows.
It assumes a fixed mapping provided below. Use git to review/rollback.

Usage:
  python automation/scripts/perform_move_single_to_groups.py
"""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SINGLES = ROOT / "automation" / "flows"
GROUPS = ROOT / "automation" / "flows" / "groups-md"

# Mapping: source single YAML -> target grouped fragment
MAPPING: dict[str, str] = {
    "big.yaml": "Group_Three/flows/BigWorkflow.yaml",
    "complex.yaml": "Group_One/flows/ComplexWorkflow.yaml",
    "content_jolt_route.yaml": "Group_Three/flows/ContentAttributeRouteWorkflow.yaml",
    "http_server.yaml": "Group_Three/flows/HttpServerWorkflow.yaml",
    "medium.yaml": "Group_One/flows/MediumWorkflow.yaml",
    "nested.yaml": "Group_Two/flows/NestedWorkflow.yaml",
    "nested_ports.yaml": "Group_Two/flows/NestedPortsWorkflow.yaml",
    "path_branch.yaml": "Group_Two/flows/PathBranchWorkflow.yaml",
    "queue_depths_http.yaml": "Monitoring/flows/QueueDepthsHttpWorkflow.yaml",
    "simple.yaml": "Group_One/flows/SimpleWorkflow.yaml",
    "split_merge.yaml": "Group_Two/flows/SplitMergeWorkflow.yaml",
    "trivial.yaml": "Group_One/flows/TrivialFlow.yaml",
    "two_branch.yaml": "Group_Three/flows/TwoBranchWorkflow.yaml",
    # trust_bootstrap.yaml has no mapping (skip)
}


def main() -> int:
    changed = 0
    skipped = []
    for src_name, tgt_rel in MAPPING.items():
        src = SINGLES / src_name
        tgt = GROUPS / tgt_rel
        if not src.exists():
            print(f"[SKIP] source missing: {src}")
            skipped.append(str(src))
            continue
        tgt.parent.mkdir(parents=True, exist_ok=True)
        # Transform single-flow spec into child PG fragment if needed
        text = src.read_text(encoding="utf-8")
        try:
            import yaml  # type: ignore
            obj = yaml.safe_load(text)
            if isinstance(obj, dict) and obj.get("process_group"):
                pg = obj.get("process_group") or {}
                groups = pg.get("process_groups") or []
                if groups and isinstance(groups, list) and isinstance(groups[0], dict):
                    frag = groups[0]
                    text = yaml.safe_dump(frag, sort_keys=False)
        except Exception:
            pass
        tgt.write_text(text, encoding="utf-8")
        changed += 1
        print(f"[WRITE] {src} -> {tgt}")
    print(f"Done. Updated {changed} file(s). Skipped {len(skipped)}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
