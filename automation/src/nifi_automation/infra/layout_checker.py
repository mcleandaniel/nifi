"""Layout validation helpers for NiFi flows.

Rules implemented:
- Left-to-right: For connections between processors within the same process group,
  the destination should be to the right of the source by at least ``min_dx``.
- No overlaps: No two components (processors or ports) in the same process group should
  occupy nearly the same position (within ``min_dsep`` in both axes). This prevents ports
  overlaying processors and vice versa.

All thresholds are configurable and meant to be conservative defaults.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Iterable, Iterator, List, Mapping, Tuple

from ..diagnostics import _walk_process_groups
from .nifi_client import NiFiClient


@dataclass(frozen=True)
class LayoutIssue:
    kind: str
    path: str
    details: Mapping[str, Any]


def _extract_component_positions(flow: Mapping[str, Any]) -> Dict[str, Tuple[float, float, str]]:
    """Return map of component id -> (x, y, kind) for processors and ports."""
    positions: Dict[str, Tuple[float, float, str]] = {}
    def _add(items: Iterable[Mapping[str, Any]], kind: str) -> None:
        for ent in items or []:
            comp = ent.get("component", {})
            cid = comp.get("id")
            pos = comp.get("position") or {}
            x = float(pos.get("x", 0.0))
            y = float(pos.get("y", 0.0))
            if cid:
                positions[cid] = (x, y, kind)

    _add(flow.get("processors") or [], "PROCESSOR")
    _add(flow.get("inputPorts") or [], "INPUT_PORT")
    _add(flow.get("outputPorts") or [], "OUTPUT_PORT")
    return positions


def _iter_processor_connections(flow: Mapping[str, Any]) -> Iterator[Tuple[str, str]]:
    for conn in flow.get("connections") or []:
        comp = conn.get("component", {})
        src = (comp.get("source") or {})
        dst = (comp.get("destination") or {})
        if src.get("type") == "PROCESSOR" and dst.get("type") == "PROCESSOR":
            sid = src.get("id")
            did = dst.get("id")
            if sid and did:
                yield sid, did


def check_layout(
    client: NiFiClient,
    *,
    min_dx: float = 50.0,
    vertical_tolerance: float = 15.0,
    min_dsep: float = 40.0,
) -> Dict[str, Any]:
    """Validate layout heuristics and return a structured report.

    Returns a dict with keys:
      - overlaps: list[LayoutIssue]
      - left_to_right_violations: list[LayoutIssue]
    """

    overlaps: List[Mapping[str, Any]] = []
    lr_violations: List[Mapping[str, Any]] = []

    for path, flow in _walk_process_groups(client):
        path_str = "/".join(path)
        positions_all = _extract_component_positions(flow)
        # Filter just processors for directional checks
        positions = {k: (x, y) for k, (x, y, kind) in positions_all.items() if kind == "PROCESSOR"}
        # Left-to-right checks only within this group's processors
        for sid, did in _iter_processor_connections(flow):
            src_pos = positions.get(sid)
            dst_pos = positions.get(did)
            if not src_pos or not dst_pos:
                continue
            dx = dst_pos[0] - src_pos[0]
            # Allow near-vertical connections (|dx| <= vertical_tolerance),
            # otherwise require destination to be at least min_dx to the right.
            if not (-vertical_tolerance <= dx <= vertical_tolerance or dx >= min_dx):
                lr_violations.append(
                    {
                        "path": path_str,
                        "source": sid,
                        "destination": did,
                        "source_pos": src_pos,
                        "destination_pos": dst_pos,
                        "dx": dx,
                        "min_dx": min_dx,
                        "vertical_tolerance": vertical_tolerance,
                    }
                )

        # Overlap checks within group (processors and ports)
        items = list(positions_all.items())
        n = len(items)
        for i in range(n):
            for j in range(i + 1, n):
                (aid, (ax, ay, akind)) = items[i]
                (bid, (bx, by, bkind)) = items[j]
                if abs(ax - bx) < min_dsep and abs(ay - by) < min_dsep:
                    overlaps.append(
                        {
                            "path": path_str,
                            "a": aid,
                            "a_kind": akind,
                            "b": bid,
                            "b_kind": bkind,
                            "a_pos": (ax, ay),
                            "b_pos": (bx, by),
                            "min_dsep": min_dsep,
                        }
                    )

    return {
        "overlaps": overlaps,
        "left_to_right_violations": lr_violations,
    }
