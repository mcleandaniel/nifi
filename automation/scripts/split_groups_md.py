#!/usr/bin/env python3
"""Split the LLM workflow Markdown into one file per root-level group.

Inputs:
  --yaml  automation/flows/NiFi_Flow_groups.yaml   (grouped spec)
  --md    automation/flows/test-workflow-suite.md  (LLM notes with `nifidesc` blocks)
  --out   automation/flows/groups-md               (output directory)

Behavior:
  - Reads groups[*].name/description and groups[*].process_groups[*].name from the YAML.
  - Parses the Markdown into sections keyed by ProcessGroup name using the `nifidesc` name field.
  - Writes one Markdown file per group with a header and the selected workflow sections (in YAML order).

This is a best-effort splitter; it expects each workflow section to have a heading (## ...) and a `nifidesc`
block that includes a `name: <ProcessGroupName>` line.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import Dict, List, Tuple

import yaml


def load_groups(yaml_path: Path) -> List[Tuple[str, str, List[str]]]:
    data = yaml.safe_load(yaml_path.read_text())
    if not isinstance(data, dict) or "process_group" not in data:
        raise ValueError("Invalid grouped YAML: missing process_group")
    pg = data["process_group"]
    groups = pg.get("groups") or []
    result: List[Tuple[str, str, List[str]]] = []
    for g in groups:
        name = g.get("name") or "Unnamed Group"
        desc = g.get("description") or ""
        children = [c.get("name") for c in (g.get("process_groups") or []) if c.get("name")]
        result.append((name, desc, children))
    return result


def normalize_filename(name: str) -> str:
    safe = re.sub(r"[^A-Za-z0-9_.-]+", "_", name.strip())
    return safe.strip("_") or "group"


def parse_md_sections(md_path: Path) -> Dict[str, List[str]]:
    lines = md_path.read_text().splitlines()
    sections_by_name: Dict[str, List[str]] = {}

    # Find all `nifidesc` blocks and map them to their enclosing section range
    i = 0
    n = len(lines)
    while i < n:
        if lines[i].strip().startswith("```nifidesc"):
            # parse within the block to find 'name: <PG>'
            j = i + 1
            pg_name = None
            while j < n and not lines[j].strip().startswith("```"):
                m = re.match(r"\s*name:\s*(.+)\s*$", lines[j])
                if m:
                    pg_name = m.group(1).strip()
                j += 1
            # j now at closing ``` or end
            # find section start: the nearest preceding '## '
            start = i
            k = i - 1
            while k >= 0:
                if lines[k].startswith("## "):
                    start = k
                    break
                k -= 1
            # find section end: next '## ' after j
            end = n
            k = j + 1
            while k < n:
                if lines[k].startswith("## "):
                    end = k
                    break
                k += 1

            if pg_name:
                sections_by_name[pg_name] = lines[start:end]
            i = j + 1
        else:
            i += 1

    return sections_by_name


def write_group_files(outdir: Path, groups: List[Tuple[str, str, List[str]]], sections: Dict[str, List[str]]) -> None:
    outdir.mkdir(parents=True, exist_ok=True)
    for gname, gdesc, children in groups:
        fname = normalize_filename(gname) + ".md"
        out_path = outdir / fname
        body: List[str] = []
        # Header
        body.append(f"# {gname}")
        if gdesc:
            body.append("")
            body.append(gdesc)
        # Add sections for children in order
        for child in children:
            sec = sections.get(child)
            if not sec:
                # Fallback: write a placeholder
                body.extend(["", f"## {child}", "_No section found in source markdown._"])
            else:
                body.append("")
                body.extend(sec)
        out_path.write_text("\n".join(body) + "\n")
        print(f"Wrote {out_path}")


def main() -> int:
    ap = argparse.ArgumentParser(description="Split workflow suite markdown into per-group files")
    ap.add_argument("--yaml", required=True, type=Path, help="Grouped YAML (NiFi_Flow_groups.yaml)")
    ap.add_argument("--md", required=True, type=Path, help="Source workflow suite markdown")
    ap.add_argument("--out", required=True, type=Path, help="Output directory for group markdown files")
    args = ap.parse_args()

    groups = load_groups(args.yaml)
    sections = parse_md_sections(args.md)
    write_group_files(args.out, groups, sections)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

