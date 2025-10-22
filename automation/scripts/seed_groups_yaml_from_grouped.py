#!/usr/bin/env python3
"""Seed per-group per-flow YAML fragments from NiFi_Flow_groups.yaml into groups-md.

This is a one-time or as-needed migration helper to establish groups-md as the
source of truth for flow specs. After seeding, editors should modify the YAML
fragments under groups-md/<Group>/flows/*.yaml and rebuild the grouped output via
build_groups_yaml_from_md.py.

Usage:
  python automation/scripts/seed_groups_yaml_from_grouped.py \
    --grouped automation/flows/NiFi_Flow_groups.yaml \
    --out-md-dir automation/flows/groups-md
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import Dict, Any

import yaml


def norm(name: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", name.strip()).strip("_") or "flow"


def main() -> int:
    ap = argparse.ArgumentParser(description="Seed per-group YAML fragments from grouped YAML")
    ap.add_argument("--grouped", type=Path, required=True, help="Path to NiFi_Flow_groups.yaml")
    ap.add_argument("--out-md-dir", type=Path, required=True, help="groups-md directory")
    args = ap.parse_args()

    data = yaml.safe_load(args.grouped.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or "process_group" not in data:
        raise SystemExit("Invalid grouped YAML: missing process_group")
    pg = data["process_group"]
    groups = pg.get("groups") or []
    if not isinstance(groups, list):
        raise SystemExit("Invalid grouped YAML: groups not a list")

    args.out_md_dir.mkdir(parents=True, exist_ok=True)
    for g in groups:
        gname = g.get("name") or "Group"
        gdir = args.out_md_dir / norm(gname) / "flows"
        gdir.mkdir(parents=True, exist_ok=True)
        for child in g.get("process_groups") or []:
            if not isinstance(child, dict) or not isinstance(child.get("name"), str):
                continue
            fname = gdir / f"{norm(child['name'])}.yaml"
            # Write child spec as-is
            fname.write_text(yaml.safe_dump(child, sort_keys=False), encoding="utf-8")
            print(f"Wrote {fname}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

