"""Parameter Context planning and (future) application services.

Phase 1: implement a plan/inspect that parses a flow spec, extracts parameter
references (#{name}) per top-level process group, and produces a default
"single context" plan with assignments.

Future phases: apply/rotate that mutate NiFi via REST.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

from ..flow_builder import FlowSpec, load_flow_spec, ProcessGroupSpec, ProcessorSpec
from .models import AppConfig, CommandResult, ExitCode


PARAM_REF_RE = re.compile(r"#\{\s*([A-Za-z0-9_.:-]+)\s*\}")


def _extract_param_refs_from_properties(props: Dict[str, str]) -> Iterable[str]:
    for value in (props or {}).values():
        if not isinstance(value, str):
            continue
        for m in PARAM_REF_RE.finditer(value):
            yield m.group(1)


def _collect_pg_params(pg: ProcessGroupSpec) -> Dict[str, Dict[str, object]]:
    """Return a mapping param_name -> metadata for a top-level PG.

    Currently only detects presence and simple sensitivity heuristics. Future work
    may leverage NiFi descriptors to mark sensitive accurately.
    """

    names: Dict[str, Dict[str, object]] = {}

    def mark(name: str) -> None:
        key = name.strip()
        if not key:
            return
        entry = names.setdefault(key, {})
        # Heuristic sensitivity
        lower = key.lower()
        if any(tok in lower for tok in ("password", "secret", "token", "apikey", "api_key", "key")):
            entry["sensitive"] = True

    def walk(group: ProcessGroupSpec) -> None:
        for proc in group.processors:
            for param in _extract_param_refs_from_properties(proc.properties or {}):
                mark(param)
        for child in group.child_groups:
            walk(child)

    walk(pg)
    # Default sensitive False if not marked
    for meta in names.values():
        meta.setdefault("sensitive", False)
    return names


def _plan_single_context(spec: FlowSpec) -> Dict[str, object]:
    # Gather per-PG sets and global union
    pg_params: List[Tuple[str, Dict[str, Dict[str, object]]]] = []
    union: Dict[str, Dict[str, object]] = {}
    for child in spec.root_group.child_groups:
        params = _collect_pg_params(child)
        pg_params.append((child.name, params))
        for name, meta in params.items():
            # Merge sensitivity (once sensitive always sensitive)
            u = union.setdefault(name, {"sensitive": False})
            u["sensitive"] = bool(u.get("sensitive") or meta.get("sensitive"))

    context_name = "ctx-all"
    contexts = [
        {
            "name": context_name,
            "parameters": [
                {"name": name, "sensitive": bool(meta.get("sensitive", False))}
                for name, meta in sorted(union.items())
            ],
        }
    ]
    assignments = [
        {"process_group": pg_name, "context": context_name} for pg_name, _ in pg_params
    ]
    return {
        "strategy": "single",
        "contexts": contexts,
        "assignments": assignments,
        "counts": {
            "process_groups": len(pg_params),
            "contexts": len(contexts),
            "parameters": len(union),
        },
    }


def plan(*, config: AppConfig, flowfile: Path) -> CommandResult:
    spec = load_flow_spec(flowfile)
    plan = _plan_single_context(spec)
    return CommandResult(message="Parameter plan", data=plan)


def inspect(*, config: AppConfig, flowfile: Path) -> CommandResult:
    # For now, reuse planning output as inspection view.
    spec = load_flow_spec(flowfile)
    plan = _plan_single_context(spec)
    return CommandResult(message="Parameter inspection", data=plan)


def apply(*, config: AppConfig, flowfile: Path) -> CommandResult:
    # Phase 1: not implemented. Future will call NiFi REST to create/update contexts and assign to PGs.
    spec = load_flow_spec(flowfile)
    plan = _plan_single_context(spec)
    return CommandResult(
        message="Params apply not implemented (dry-run only)",
        data=plan,
    )


def rotate(*, config: AppConfig, flowfile: Path) -> CommandResult:
    # Placeholder stub; future will accept selectors and new values/refs.
    return CommandResult(
        exit_code=ExitCode.BAD_INPUT,
        message="Rotate not implemented; use your provider (Vault/DB) or update source manifests",
    )

