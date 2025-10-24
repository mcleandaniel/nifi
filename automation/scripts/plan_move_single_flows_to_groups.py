#!/usr/bin/env python3
"""Plan mapping of single-flow specs to grouped fragments (no file writes).

Scans `automation/flows/*.yaml` (excluding grouped/aggregate files), reads the
first process group name from each spec, and attempts to find the corresponding
fragment under `automation/flows/groups-md/*/flows/{Name}.yaml`.

Outputs a plan of proposed moves in text (default) or JSON.

Usage:
  python automation/scripts/plan_move_single_flows_to_groups.py [--output json|text]
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Dict, List

import yaml

ROOT = Path(__file__).resolve().parents[2]
# Use automation/flows (not repo-root/flows)
FLOWS_DIR = ROOT / "automation" / "flows"
GROUPS_MD = FLOWS_DIR / "groups-md"


def find_flow_name(spec_path: Path) -> str | None:
    try:
        data = yaml.safe_load(spec_path.read_text(encoding="utf-8"))
    except Exception:
        return None
    if not isinstance(data, dict):
        return None
    pg = data.get("process_group")
    if not isinstance(pg, dict):
        return None
    groups = pg.get("process_groups") or []
    if not isinstance(groups, list) or not groups:
        return None
    first = groups[0]
    if not isinstance(first, dict):
        return None
    name = first.get("name")
    return name if isinstance(name, str) and name.strip() else None


def plan_moves(output: str = "text") -> int:
    singles: List[Path] = []
    for p in sorted(FLOWS_DIR.glob("*.yaml")):
        # Skip aggregate or non-single files if present
        if p.name in {"NiFi_Flow.yaml", "NiFi_Flow_groups.yaml"}:
            continue
        singles.append(p)

    proposed: List[Dict[str, object]] = []
    unmatched: List[Dict[str, object]] = []
    ambiguous: List[Dict[str, object]] = []

    verbose_rows: List[Dict[str, object]] = []
    for src in singles:
        name = find_flow_name(src)
        if not name:
            unmatched.append({"source": str(src), "reason": "missing or invalid top-level process group name"})
            verbose_rows.append({"source": str(src), "status": "INVALID_SPEC", "detail": "missing or invalid PG name"})
            continue
        # Look for groups-md/*/flows/{name}.yaml
        matches = sorted(GROUPS_MD.glob(f"**/flows/{name}.yaml"))
        if not matches:
            unmatched.append({"source": str(src), "flow_name": name, "reason": "no matching fragment"})
            verbose_rows.append({"source": str(src), "flow_name": name, "status": "MISSING", "detail": "no fragment found"})
            continue
        if len(matches) > 1:
            ambiguous.append({"source": str(src), "flow_name": name, "candidates": [str(m) for m in matches]})
            verbose_rows.append({"source": str(src), "flow_name": name, "status": "AMBIGUOUS", "candidates": [str(m) for m in matches]})
            continue
        tgt = str(matches[0])
        proposed.append({"source": str(src), "flow_name": name, "target": tgt})
        verbose_rows.append({"source": str(src), "flow_name": name, "status": "MATCH", "target": tgt})

    plan = {
        "proposed": proposed,
        "ambiguous": ambiguous,
        "unmatched": unmatched,
        "counts": {
            "singles": len(singles),
            "proposed": len(proposed),
            "ambiguous": len(ambiguous),
            "unmatched": len(unmatched),
        },
    }

    if output == "json":
        plan["verbose"] = verbose_rows
        print(json.dumps(plan, indent=2))
    else:
        print("Scanning directory:")
        print(f"  singles_dir = {FLOWS_DIR}")
        print(f"  groups_dir  = {GROUPS_MD}")
        print("\nResults per single-flow spec:")
        for row in verbose_rows:
            status = row.get("status")
            src = row.get("source")
            name = row.get("flow_name", "?")
            if status == "MATCH":
                print(f"  [OK]    {src}  -> {row.get('target')}  (name={name})")
            elif status == "MISSING":
                print(f"  [MISS]  {src}  (name={name})  no fragment found")
            elif status == "AMBIGUOUS":
                print(f"  [AMB]   {src}  (name={name})  candidates:")
                for cand in row.get("candidates", []):
                    print(f"           - {cand}")
            elif status == "INVALID_SPEC":
                print(f"  [BAD]   {src}  missing/invalid process_group name")
        print("\nProposed moves (replace placeholders with single-flow specs):")
        for item in proposed:
            print(f"  {item['source']} -> {item['target']}  # name={item['flow_name']}")
        print("\nSummary:")
        counts = plan["counts"]
        print(
            f"  singles={counts['singles']} proposed={counts['proposed']} "
            f"ambiguous={counts['ambiguous']} unmatched={counts['unmatched']}"
        )
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Plan mapping of single-flow YAMLs into grouped fragments")
    ap.add_argument("--output", default="text", choices=["text", "json"], help="Output format")
    args = ap.parse_args()
    return plan_moves(output=args.output)


if __name__ == "__main__":
    raise SystemExit(main())
