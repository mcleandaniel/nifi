#!/usr/bin/env python3
"""Build a grouped NiFi flow YAML from per-group Markdown files.

Inputs (defaults match repo layout):
  --md-dir      automation/flows/groups-md           (each file: one group)
  --out         automation/flows/NiFi_Flow_groups.yaml
  --root-name   "NiFi Flow"

Behavior:
  - For each Markdown file under --md-dir:
      * Parse group name from first level-1 header (# ...)
      * Parse optional description: first non-empty line after header
      * Parse workflow names from ```nifidesc blocks (line 'name: <PGName>')
      * For each referenced workflow, load its YAML fragment from
        --md-dir/<normalized-group>/flows/<normalized-workflow>.yaml
        (primary). If not found, attempt to extract an inline ```yaml block
        immediately following the corresponding section. As a last resort,
        insert a stub and warn.
  - Assemble a grouped YAML with:
        process_group:
          name: <root-name>
          groups:
            - name: <group-name>
              description: <desc>
              process_groups: [embedded child PG specs by name]

Notes:
  - This does not touch NiFi_Flow.yaml and does not read automation/flows/*.yaml.
  - Source-of-truth is groups-md: per-group MD + per-flow YAML fragments in
    groups-md/<Group>/flows/.
  - If a referenced Process Group name is not found, the tool prints a warning and
    inserts a placeholder stub so the grouping remains intact.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional

import yaml


def load_fragment_from_file(base_dir: Path, group_name: str, flow_name: str) -> Optional[dict]:
    """Load a per-flow YAML fragment from groups-md/<group>/flows/<flow>.yaml if present."""
    def norm(s: str) -> str:
        return re.sub(r"[^A-Za-z0-9_.-]+", "_", s.strip()).strip("_") or "flow"

    group_dir = base_dir / norm(group_name) / "flows"
    cand = [group_dir / f"{norm(flow_name)}.yaml", group_dir / f"{flow_name}.yaml"]
    for p in cand:
        if p.exists():
            try:
                data = yaml.safe_load(p.read_text(encoding="utf-8"))
                if isinstance(data, dict):
                    return data
            except Exception as e:
                print(f"[warn] failed to load {p}: {e}")
    return None


def parse_group_md(md_path: Path) -> Tuple[str, str, List[str], Dict[str, List[str]], Dict[str, Dict[str, Any]]]:
    """Extract (group_name, description, child_names, sections_by_name, flags_by_name)
    from a group markdown file.

    flags_by_name maps workflow name -> flags parsed from the nifidesc block, such as
    { "live": bool, "phase": str }. Missing flags are not enforced and default to
    permissive include behavior.
    """
    text = md_path.read_text(encoding="utf-8")
    lines = text.splitlines()

    # Group name: first H1 header
    group_name = None
    for ln in lines:
        if ln.startswith("# "):
            group_name = ln[2:].strip()
            break
    if not group_name:
        group_name = md_path.stem.replace("_", " ")

    # Description: first non-empty line after the H1 header
    desc = ""
    found_h1 = False
    for ln in lines:
        if not found_h1:
            if ln.startswith("# "):
                found_h1 = True
            continue
        # after header
        if ln.strip():
            desc = ln.strip()
            break

    # Child names from nifidesc blocks
    child_names: List[str] = []
    sections_by_name: Dict[str, List[str]] = {}
    flags_by_name: Dict[str, Dict[str, Any]] = {}
    for m in re.finditer(r"```nifidesc\n(.*?)```", text, re.DOTALL):
        block = m.group(1)
        # Try to parse the whole block as YAML for richer metadata
        meta: Optional[dict] = None
        try:
            parsed = yaml.safe_load(block)
            if isinstance(parsed, dict):
                meta = parsed
        except Exception:
            meta = None

        name: Optional[str] = None
        if meta and isinstance(meta.get("name"), str):
            name = meta.get("name").strip()
        else:
            # Fallback: scan for a name: line
            for line in block.splitlines():
                mm = re.match(r"\s*name:\s*(.+)\s*$", line)
                if mm:
                    name = mm.group(1).strip()
                    break
        if name:
            if name not in child_names:
                child_names.append(name)
            # Capture optional flags if present
            if meta:
                flags: Dict[str, Any] = {}
                if "live" in meta:
                    flags["live"] = bool(meta.get("live"))
                if "phase" in meta and isinstance(meta.get("phase"), str):
                    flags["phase"] = str(meta.get("phase")).strip()
                if flags:
                    flags_by_name[name] = flags

    # Keep raw lines too for optional inline YAML extraction per child
    # Map child name -> entire section text (from its nearest preceding '## ' to next '## ')
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
                sections_by_name[pg_name] = lines[start:end]
            i = j + 1
        else:
            i += 1

    return group_name, desc, child_names, sections_by_name, flags_by_name


def extract_inline_yaml(section_lines: List[str]) -> Optional[dict]:
    """Extract first ```yaml ... ``` block from a section and return parsed YAML dict."""
    text = "\n".join(section_lines)
    m = re.search(r"```yaml\n(.*?)```", text, re.DOTALL)
    if not m:
        return None
    try:
        data = yaml.safe_load(m.group(1))
    except Exception:
        return None
    return data if isinstance(data, dict) else None


def _load_default_children(base_md_dir: Path) -> List[dict]:
    """Load child PG specs from YAML files placed directly under groups-md/.

    Any YAML at groups-md/*.yaml (excluding NiFi_Flow_groups.yaml) is treated as a
    top-level process_group child (the "default" non-grouped set).
    """
    defaults: List[dict] = []
    for p in sorted(base_md_dir.glob("*.yaml")):
        if p.name == "NiFi_Flow_groups.yaml":
            continue
        try:
            data = yaml.safe_load(p.read_text(encoding="utf-8"))
        except Exception:
            continue
        # Accept only child PG fragments (not aggregates). Expect a 'name' key and no top-level 'process_group'.
        if not isinstance(data, dict):
            continue
        if data.get("process_group"):
            # skip aggregates accidentally dropped here
            continue
        if data.get("name"):
            defaults.append(data)
    return defaults


def build_grouped_yaml(root_name: str, groups: List[Tuple[str, str, List[str], Dict[str, List[str]], Dict[str, Dict[str, Any]]]], base_md_dir: Path) -> dict:
    # First, build all group entries
    group_entries: List[Dict[str, Any]] = []
    group_child_names: set[str] = set()

    def has_any_processors(spec: Dict[str, Any]) -> bool:
        try:
            if spec.get("processors"):
                return True
            for child in spec.get("process_groups") or []:
                if isinstance(child, dict) and has_any_processors(child):
                    return True
        except Exception:
            pass
        return False

    for gname, gdesc, child_names, sections, flags_by_name in groups:
        children_specs: List[dict] = []
        for cname in child_names:
            spec = load_fragment_from_file(base_md_dir, gname, cname)
            if not spec and cname in sections:
                spec = extract_inline_yaml(sections[cname])
            if not spec:
                print(f"[info] excluding flow '{cname}' (no fragment found)")
                continue
            # Exclude based on MD/YAML gating flags: phase/live
            md_flags = (flags_by_name or {}).get(cname, {})
            spec_phase = spec.get("phase") if isinstance(spec, dict) else None
            spec_live = spec.get("live") if isinstance(spec, dict) else None
            # Exclusion rules (permissive by default):
            # - If MD sets live: false → exclude
            # - If MD sets phase and phase != ready → exclude
            # - If YAML sets live: false → exclude
            # - If YAML sets phase and phase != ready → exclude
            if isinstance(md_flags.get("live"), bool) and md_flags.get("live") is False:
                print(f"[info] excluding flow '{cname}' (md live=false)")
                continue
            if isinstance(md_flags.get("phase"), str) and md_flags.get("phase").lower() != "ready":
                print(f"[info] excluding flow '{cname}' (md phase={md_flags.get('phase')})")
                continue
            if isinstance(spec_live, bool) and spec_live is False:
                print(f"[info] excluding flow '{cname}' (yaml live=false)")
                continue
            if isinstance(spec_phase, str) and spec_phase.lower() != "ready":
                print(f"[info] excluding flow '{cname}' (yaml phase={spec_phase})")
                continue
            children_specs.append(spec)
        # Filter out any child specs that contain no processors recursively
        children_specs = [s for s in children_specs if has_any_processors(s)]
        if not children_specs:
            print(f"[info] excluding group '{gname}' because all children lack processors")
            continue
        group_entries.append({
            "name": gname,
            "description": gdesc,
            "process_groups": children_specs,
        })
        for s in children_specs:
            n = s.get("name")
            if isinstance(n, str) and n:
                group_child_names.add(n)

    # Load defaults and prefer defaults over duplicates
    default_children = _load_default_children(base_md_dir)
    filtered_defaults: List[dict] = []
    default_names: set[str] = set()
    for c in default_children:
        nm = c.get("name") if isinstance(c, dict) else None
        c_phase = c.get("phase") if isinstance(c, dict) else None
        c_live = c.get("live") if isinstance(c, dict) else None
        if isinstance(c_live, bool) and c_live is False:
            print(f"[info] excluding default child '{nm}' (yaml live=false)")
            continue
        if isinstance(c_phase, str) and c_phase.lower() != "ready":
            print(f"[info] excluding default child '{nm}' (yaml phase={c_phase})")
            continue
        if not has_any_processors(c):
            print(f"[info] excluding default child without processors: {nm}")
            continue
        if isinstance(nm, str) and nm:
            default_names.add(nm)
        filtered_defaults.append(c)

    # Remove from groups any child PG whose name is present in defaults (to allow standalone PGs outside groups)
    final_groups: List[Dict[str, Any]] = []
    for entry in group_entries:
        children = [s for s in entry.get("process_groups", []) if not (isinstance(s.get("name"), str) and s.get("name") in default_names)]
        if not children:
            # If a group becomes empty after filtering, drop it
            print(f"[info] excluding group '{entry.get('name')}' after default dedupe (no remaining children)")
            continue
        final_groups.append({"name": entry["name"], "description": entry["description"], "process_groups": children})

    return {"process_group": {"name": root_name, "process_groups": filtered_defaults, "groups": final_groups}}


def main() -> int:
    ap = argparse.ArgumentParser(description="Build grouped YAML from per-group Markdown files + per-flow fragments")
    ap.add_argument("--md-dir", type=Path, required=True, help="Directory of per-group markdown files")
    ap.add_argument("--out", type=Path, required=True, help="Output NiFi_Flow_groups.yaml path")
    ap.add_argument("--root-name", default="NiFi Flow", help="Root process group name")
    args = ap.parse_args()

    groups: List[Tuple[str, str, List[str], Dict[str, List[str]]]] = []
    for md_path in sorted(args.md_dir.glob("*.md")):
        if md_path.name.lower() == "readme.md":
            continue  # README is documentation; not a group definition
        gname, gdesc, child_names, sections, flags = parse_group_md(md_path)
        groups.append((gname, gdesc, child_names, sections, flags))

    data = build_grouped_yaml(args.root_name, groups, args.md_dir)
    args.out.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
    print(f"Wrote grouped YAML to {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
