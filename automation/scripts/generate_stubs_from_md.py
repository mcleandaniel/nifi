#!/usr/bin/env python3
"""Generate YAML stub fragments from per-group Markdown files.

Purpose: Create initial per-workflow YAML fragments from the group docs to
establish the MD → stub → YAML authoring flow. The fragments include a
`phase` marker (e.g., 'draft') so authors and tooling can track readiness.

Inputs:
  --md-dir       automation/flows/groups-md        (Group_*.md files)
  --out-md-dir   automation/flows/groups-md        (where to write fragments)
  --phase        draft|ready|wip (default: draft)
  --overwrite-stub  overwrite if existing fragment has phase in {draft, stub}

Behavior:
  - For each group MD file (ignores README.md):
      * Parse group name (H1), optional description (first paragraph)
      * Parse nifidesc blocks to get workflow names in order
      * Ensure groups-md/<Group>/flows/<Workflow>.yaml exists:
          - If absent, write a stub:
              name: <Workflow>
              phase: <phase>
              description: <derived from Overview/Technical if present>
              processors: []
              connections: []
          - If present and --overwrite-stub is set, overwrite only when
            existing phase is 'draft' or 'stub'

Notes:
  - This tool does not modify NiFi_Flow.yaml or NiFi_Flow_groups.yaml.
  - The build step (build_groups_yaml_from_md.py) assembles the grouped file
    from these fragments without reading automation/flows/*.yaml.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import Dict, List, Tuple, Optional

import yaml


def norm(name: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", name.strip()).strip("_") or "flow"


def parse_group_md(md_path: Path) -> Tuple[str, str, List[str], Dict[str, List[str]]]:
    text = md_path.read_text(encoding="utf-8")
    lines = text.splitlines()

    # Group name
    group_name = None
    for ln in lines:
        if ln.startswith("# "):
            group_name = ln[2:].strip()
            break
    if not group_name:
        group_name = md_path.stem.replace("_", " ")

    # First non-empty line after H1 as description
    desc = ""
    after_h1 = False
    for ln in lines:
        if not after_h1:
            if ln.startswith("# "):
                after_h1 = True
            continue
        if ln.strip():
            desc = ln.strip()
            break

    # Workflow names and section ranges
    child_names: List[str] = []
    sections_by_name: Dict[str, List[str]] = {}

    i = 0
    n = len(lines)
    while i < n:
        if lines[i].strip().startswith("```nifidesc"):
            j = i + 1
            pg_name = None
            while j < n and not lines[j].strip().startswith("```"):
                m = re.match(r"\s*name:\s*(.+)\s*$", lines[j])
                if m:
                    pg_name = m.group(1).strip()
                j += 1
            # locate enclosing section
            start = i
            k = i - 1
            while k >= 0:
                if lines[k].startswith("## "):
                    start = k
                    break
                k -= 1
            end = n
            k = j + 1
            while k < n:
                if lines[k].startswith("## "):
                    end = k
                    break
                k += 1
            if pg_name:
                if pg_name not in child_names:
                    child_names.append(pg_name)
                sections_by_name[pg_name] = lines[start:end]
            i = j + 1
        else:
            i += 1

    return group_name, desc, child_names, sections_by_name


def derive_description(section_lines: List[str]) -> str:
    """Try to extract Overview and Technical lines into a description body."""
    overview = None
    technical = None
    for ln in section_lines:
        m = re.match(r"\s*Overview:\s*(.*)$", ln)
        if m:
            overview = m.group(1).strip()
        m = re.match(r"\s*Technical:\s*(.*)$", ln)
        if m:
            technical = m.group(1).strip()
    parts = []
    if overview:
        parts.append(f"Overview: {overview}")
    if technical:
        parts.append(f"Technical: {technical}")
    return "\n".join(parts)


def main() -> int:
    ap = argparse.ArgumentParser(description="Generate YAML stubs from groups-md")
    ap.add_argument("--md-dir", type=Path, required=True, help="Directory containing Group_*.md files")
    ap.add_argument("--out-md-dir", type=Path, required=True, help="Root directory to write fragments (groups-md)")
    ap.add_argument("--phase", default="draft", help="Phase marker to include in new stubs (default: draft)")
    ap.add_argument("--overwrite-stub", action="store_true", help="Overwrite existing fragments when phase is draft/stub")
    args = ap.parse_args()

    args.out_md_dir.mkdir(parents=True, exist_ok=True)
    for md_path in sorted(args.md_dir.glob("*.md")):
        if md_path.name.lower() == "readme.md":
            continue
        gname, gdesc, child_names, sections = parse_group_md(md_path)
        gdir = args.out_md_dir / norm(gname) / "flows"
        gdir.mkdir(parents=True, exist_ok=True)
        for flow in child_names:
            outp = gdir / f"{norm(flow)}.yaml"
            if outp.exists() and not args.overwrite_stub:
                # Inspect existing phase; overwrite only if requested and draft/stub
                try:
                    data = yaml.safe_load(outp.read_text(encoding="utf-8")) or {}
                except Exception:
                    data = {}
                phase = str(data.get("phase", "")).lower()
                if phase not in {"draft", "stub"}:
                    continue
                if not args.overwrite_stub:
                    continue

            desc = derive_description(sections.get(flow, []))
            stub = {
                "name": flow,
                "phase": args.phase,
                "description": desc or "",
                "processors": [],
                "connections": [],
            }
            outp.write_text(yaml.safe_dump(stub, sort_keys=False), encoding="utf-8")
            print(f"Wrote stub {outp}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

