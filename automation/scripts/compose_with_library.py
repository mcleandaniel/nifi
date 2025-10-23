#!/usr/bin/env python3
"""
Compose a harness flow by inlining Process Group library fragments.

Usage (from repo root):
  python automation/scripts/compose_with_library.py \
    --input automation/flows/library/http_library_harness.yaml \
    --out automation/flows/library/http_library_harness_composed.yaml

Conventions
- Harness YAML includes `library_includes` under a process group with entries like:
    - { name: EchoLogger }                   # loads automation/process-library/EchoLogger.yaml
    - { name: AttributeTagger, as: Tagger }  # alias group name to avoid collisions
- Parent connections may reference child ports using `Alias.in` or `Alias.out`.
  The composer rewrites these to unique keys `Alias__in`/`Alias__out` and
  renames the child port keys accordingly to avoid key collisions across siblings.
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any, Dict, List
import sys
import yaml


def _load_yaml(path: Path) -> Dict[str, Any]:
    return yaml.safe_load(path.read_text()) or {}


def _save_yaml(path: Path, data: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as fp:
        yaml.safe_dump(data, fp, sort_keys=False)


def _prefix_child_port_ids(pg: Dict[str, Any], alias: str) -> Dict[str, str]:
    """Rename child port ids to ensure uniqueness at the parent boundary.

    Returns a mapping from original id -> new namespaced id.
    """
    id_map: Dict[str, str] = {}
    for port_key in ("input_ports", "output_ports"):
        ports = pg.get(port_key) or []
        for item in ports:
            orig = str(item.get("id"))
            new_id = f"{alias}__{orig}"
            item["id"] = new_id
            id_map[orig] = new_id

    # Rewrite internal connections that reference the ports by id
    for conn in pg.get("connections") or []:
        src = str(conn.get("source"))
        dst = str(conn.get("destination"))
        if src in id_map:
            conn["source"] = id_map[src]
        if dst in id_map:
            conn["destination"] = id_map[dst]
    return id_map


def _rewrite_parent_connections(parent_pg: Dict[str, Any], alias_to_keymap: Dict[str, Dict[str, str]]) -> None:
    for conn in parent_pg.get("connections") or []:
        for end in ("source", "destination"):
            raw = str(conn.get(end))
            if "." in raw:
                alias, local = raw.split(".", 1)
                keymap = alias_to_keymap.get(alias)
                if keymap and local in keymap:
                    conn[end] = keymap[local]


def compose(harness_path: Path, out_path: Path, library_dir: Path) -> None:
    data = _load_yaml(harness_path)
    root = data.get("process_group")
    if not isinstance(root, dict):
        raise SystemExit("Harness YAML must have a top-level 'process_group' mapping")

    # Target the first (and typically only) child group in the harness
    children: List[Dict[str, Any]] = list(root.get("process_groups") or [])
    if not children:
        raise SystemExit("Harness 'process_group' must include at least one child under 'process_groups'")
    parent_pg = children[0]

    includes = parent_pg.get("library_includes") or []
    if not includes:
        _save_yaml(out_path, data)
        return

    alias_to_idmap: Dict[str, Dict[str, str]] = {}
    for entry in includes:
        name = entry.get("name")
        alias = entry.get("as") or name
        file_path = entry.get("file") or f"{name}.yaml"
        lib_path = (library_dir / file_path).resolve()
        if not lib_path.exists():
            raise SystemExit(f"Library fragment not found: {lib_path}")
        lib = _load_yaml(lib_path)
        child_pg = lib.get("process_group")
        if not isinstance(child_pg, dict):
            raise SystemExit(f"Library file {lib_path} must contain a top-level 'process_group' mapping")
        # Apply alias as the child PG name
        child_pg["name"] = alias
        # Ensure port keys are unique at parent boundary
        id_map = _prefix_child_port_ids(child_pg, alias)
        alias_to_idmap[alias] = id_map
        # Append to parent children
        parent_pg.setdefault("process_groups", [])
        parent_pg["process_groups"].append(child_pg)

    # Rewrite parent connections that reference child ports using Alias.localKey form
    _rewrite_parent_connections(parent_pg, alias_to_idmap)

    # Remove composer-only metadata to keep the final YAML clean
    parent_pg.pop("library_includes", None)

    _save_yaml(out_path, data)


def main(argv: List[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True, type=Path, help="Harness YAML path")
    ap.add_argument("--out", required=True, type=Path, help="Output path for composed YAML")
    ap.add_argument(
        "--library-dir",
        default=Path("automation/process-library"),
        type=Path,
        help="Directory containing library PG YAML files",
    )
    args = ap.parse_args(argv)
    compose(args.input, args.out, args.library_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
