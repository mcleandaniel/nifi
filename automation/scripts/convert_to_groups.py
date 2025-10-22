#!/usr/bin/env python3
"""Convert a root-level process_groups flow into grouped form.

Usage:
  python automation/scripts/convert_to_groups.py \
    --in automation/flows/NiFi_Flow.yaml \
    --out automation/flows/NiFi_Flow_groups.yaml \
    --groups "Group One:Core and simple flows" \
            "Group Two:Branching and batching" \
            "Group Three:HTTP and composites"

The script reads the root-level `process_group.process_groups` list and
evenly distributes entries across the provided group names (in order).
It nests the full child specs under `process_group.groups[*].process_groups`.

Notes:
  - Only root-level grouping is handled; nested child groups remain as-is.
  - If no --groups provided, defaults to 3 groups with generic descriptions.
"""

from __future__ import annotations

import argparse
import math
from pathlib import Path
from typing import List, Tuple

import yaml


def parse_group_args(values: List[str]) -> List[Tuple[str, str]]:
    if not values:
        return [
            ("Group One", "Core and simple flows"),
            ("Group Two", "Branching and batching"),
            ("Group Three", "HTTP and composite flows"),
        ]
    result: List[Tuple[str, str]] = []
    for item in values:
        if ":" in item:
            name, desc = item.split(":", 1)
        else:
            name, desc = item, ""
        result.append((name.strip(), desc.strip()))
    return result


def main() -> int:
    ap = argparse.ArgumentParser(description="Convert root process_groups to grouped form")
    ap.add_argument("--in", dest="src", required=True, type=Path, help="Source YAML file")
    ap.add_argument("--out", dest="dst", required=True, type=Path, help="Destination YAML file")
    ap.add_argument(
        "--groups",
        nargs="*",
        default=[],
        help="GroupName[:Description] entries; order determines left-to-right placement",
    )
    args = ap.parse_args()

    data = yaml.safe_load(args.src.read_text())
    if not isinstance(data, dict) or "process_group" not in data:
        raise SystemExit("Invalid spec: missing top-level process_group")

    pg = data["process_group"]
    children = list(pg.get("process_groups") or [])

    groups = parse_group_args(args.groups)
    n = len(children)
    k = len(groups)
    if n == 0:
        # Still produce groups but with empty lists
        pg["groups"] = [
            {"name": gname, "description": gdesc, "process_groups": []} for gname, gdesc in groups
        ]
        pg.pop("process_groups", None)
        args.dst.write_text(yaml.safe_dump({"process_group": pg}, sort_keys=False))
        return 0

    # Even distribution preserving original order
    per = math.ceil(n / k)
    grouped: List[dict] = []
    idx = 0
    for gname, gdesc in groups:
        chunk = children[idx : idx + per]
        idx += per
        grouped.append(
            {
                "name": gname,
                "description": gdesc,
                "process_groups": chunk,
            }
        )
    # If any remainder (when n < k*per), they will be empty chunks; it's fine

    pg["groups"] = grouped
    # Remove ungrouped list in the grouped output
    pg.pop("process_groups", None)

    args.dst.write_text(yaml.safe_dump({"process_group": pg}, sort_keys=False))
    print(f"Wrote grouped flow to {args.dst}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

