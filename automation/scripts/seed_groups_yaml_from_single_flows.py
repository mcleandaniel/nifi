#!/usr/bin/env python3
"""Seed per-group per-flow YAML fragments from existing single-flow YAML files.

This migration helper uses the per-group Markdown files to determine group membership
and workflow names, then finds each workflow's YAML spec in automation/flows/*.yaml
and writes a copy under groups-md/<Group>/flows/<Workflow>.yaml.

After seeding, build_groups_yaml_from_md.py can assemble NiFi_Flow_groups.yaml without
referencing automation/flows/*.yaml going forward.

Usage:
  python automation/scripts/seed_groups_yaml_from_single_flows.py \
    --md-dir automation/flows/groups-md \
    --flows-dir automation/flows \
    --out-md-dir automation/flows/groups-md
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import Dict, List, Tuple, Optional

import yaml


def norm(name: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", name.strip()).strip("_") or "flow"


def parse_group_md(md_path: Path) -> Tuple[str, List[str]]:
    text = md_path.read_text(encoding="utf-8")
    # Group name from first H1
    gname = None
    for ln in text.splitlines():
        if ln.startswith("# "):
            gname = ln[2:].strip()
            break
    if not gname:
        gname = md_path.stem.replace("_", " ")
    # Flow names from nifidesc blocks
    child_names: List[str] = []
    for m in re.finditer(r"```nifidesc\n(.*?)```", text, re.DOTALL):
        block = m.group(1)
        for line in block.splitlines():
            mm = re.match(r"\s*name:\s*(.+)\s*$", line)
            if mm:
                n = mm.group(1).strip()
                if n not in child_names:
                    child_names.append(n)
                break
    return gname, child_names


def find_child_spec(flows_dir: Path, flow_name: str) -> Optional[dict]:
    for path in sorted(flows_dir.glob("*.yaml")):
        if path.name in {"NiFi_Flow.yaml", "NiFi_Flow_groups.yaml"}:
            continue
        try:
            data = yaml.safe_load(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        if not isinstance(data, dict):
            continue
        pg = data.get("process_group")
        if not isinstance(pg, dict):
            continue
        children = pg.get("process_groups") or []
        for child in children or []:
            if isinstance(child, dict) and child.get("name") == flow_name:
                return child
    return None


def main() -> int:
    ap = argparse.ArgumentParser(description="Seed per-group YAML fragments from single-flow specs")
    ap.add_argument("--md-dir", type=Path, required=True, help="groups-md directory containing Group_*.md files")
    ap.add_argument("--flows-dir", type=Path, required=True, help="Directory of single-flow YAML files")
    ap.add_argument("--out-md-dir", type=Path, required=True, help="groups-md output directory (same as --md-dir)")
    args = ap.parse_args()

    args.out_md_dir.mkdir(parents=True, exist_ok=True)
    for md_path in sorted(args.md_dir.glob("*.md")):
        if md_path.name.lower() == "readme.md":
            continue  # ignore folder readme
        gname, child_names = parse_group_md(md_path)
        gdir = args.out_md_dir / norm(gname) / "flows"
        gdir.mkdir(parents=True, exist_ok=True)
        for flow in child_names:
            spec = find_child_spec(args.flows_dir, flow)
            if not spec:
                print(f"[warn] no spec found for '{flow}' in {args.flows_dir}")
                continue
            outp = gdir / f"{norm(flow)}.yaml"
            outp.write_text(yaml.safe_dump(spec, sort_keys=False), encoding="utf-8")
            print(f"Wrote {outp}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
