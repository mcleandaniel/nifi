#!/usr/bin/env python3
"""Sync process group descriptions from the doc to YAML specs.

Source of truth: automation/flows/test-workflow-suite.md
  - Under each workflow header, include a fenced block:

    ```nifidesc
    name: WorkflowName
    Overview: ...
    Technical: ...
    ```

This tool parses those blocks and writes the description text into the
`description` field for the matching process group names in:
  - All single-flow specs in automation/flows/*.yaml (excluding NiFi_Flow.yaml)
  - The aggregate automation/flows/NiFi_Flow.yaml

Usage:
  python automation/scripts/sync_descriptions.py [--dry-run]
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import Dict

import yaml


FLOWS_DIR = Path(__file__).resolve().parents[1] / "flows"
DOC_PATH = FLOWS_DIR / "test-workflow-suite.md"


def parse_doc() -> Dict[str, str]:
    text = DOC_PATH.read_text(encoding="utf-8")
    # Match ```nifidesc ... ``` blocks
    pattern = re.compile(r"```nifidesc\n(.*?)```", re.DOTALL)
    blocks = pattern.findall(text)
    result: Dict[str, str] = {}
    for block in blocks:
        lines = [ln.rstrip("\n") for ln in block.splitlines()]
        if not lines:
            continue
        first = lines[0].strip()
        if not first.lower().startswith("name:"):
            continue
        name = first.split(":", 1)[1].strip()
        desc = "\n".join(lines[1:]).strip()
        if name and desc:
            result[name] = desc
    return result


def update_yaml_descriptions(name_to_desc: Dict[str, str], *, dry_run: bool) -> int:
    changed = 0

    # Update single-flow specs
    for path in sorted(FLOWS_DIR.glob("*.yaml")):
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            continue
        pg = data.get("process_group")
        if not isinstance(pg, dict):
            continue
        groups = pg.get("process_groups") or []
        if not isinstance(groups, list):
            continue
        updated = False
        for g in groups:
            if not isinstance(g, dict):
                continue
            name = g.get("name")
            if not isinstance(name, str):
                continue
            new_desc = name_to_desc.get(name)
            if new_desc and g.get("description") != new_desc:
                g["description"] = new_desc
                updated = True
        if updated and not dry_run:
            path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
            changed += 1

    # Update aggregate NiFi_Flow.yaml
    agg_path = FLOWS_DIR / "NiFi_Flow.yaml"
    agg = yaml.safe_load(agg_path.read_text(encoding="utf-8"))
    groups = agg.get("process_group", {}).get("process_groups", []) if isinstance(agg, dict) else []
    agg_updated = False
    for g in groups or []:
        if not isinstance(g, dict):
            continue
        name = g.get("name")
        new_desc = name_to_desc.get(name)
        if isinstance(name, str) and new_desc and g.get("description") != new_desc:
            g["description"] = new_desc
            agg_updated = True
    if agg_updated and not dry_run:
        agg_path.write_text(yaml.safe_dump(agg, sort_keys=False), encoding="utf-8")
        changed += 1

    return changed


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="Do not write files; only report diffs")
    args = ap.parse_args()

    mapping = parse_doc()
    if not mapping:
        print("No nifidesc blocks found; nothing to sync.")
        return
    changed = update_yaml_descriptions(mapping, dry_run=args.dry_run)
    print(f"Updated {changed} file(s)." if not args.dry_run else f"Would update {changed} file(s).")


if __name__ == "__main__":
    main()

