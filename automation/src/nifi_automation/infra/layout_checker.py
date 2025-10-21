"""Layout validation helpers for NiFi flows.

Rules implemented:
- Left-to-right: For connections between processors within the same process group,
  the destination should be to the right of the source by at least ``min_dx``.
- No overlaps: No two processors in the same process group should occupy nearly
  the same position (within ``min_dsep`` in both axes).

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


def _extract_processor_positions(flow: Mapping[str, Any]) -> Dict[str, Tuple[float, float]]:
    positions: Dict[str, Tuple[float, float]] = {}
    for proc in flow.get("processors") or []:
        comp = proc.get("component", {})
        pid = comp.get("id")
        pos = (comp.get("position") or {})
        x = float(pos.get("x", 0.0))
        y = float(pos.get("y", 0.0))
        if pid:
            positions[pid] = (x, y)
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
        positions = _extract_processor_positions(flow)
        # Left-to-right checks only within this group's processors
        for sid, did in _iter_processor_connections(flow):
            src_pos = positions.get(sid)
            dst_pos = positions.get(did)
            if not src_pos or not dst_pos:
                continue
            if dst_pos[0] < src_pos[0] + min_dx:
                lr_violations.append(
                    {
                        "path": path_str,
                        "source": sid,
                        "destination": did,
                        "source_pos": src_pos,
                        "destination_pos": dst_pos,
                        "min_dx": min_dx,
                    }
                )

        # Overlap checks within group
        items = list(positions.items())
        n = len(items)
        for i in range(n):
            for j in range(i + 1, n):
                (aid, (ax, ay)) = items[i]
                (bid, (bx, by)) = items[j]
                if abs(ax - bx) < min_dsep and abs(ay - by) < min_dsep:
                    overlaps.append(
                        {
                            "path": path_str,
                            "a": aid,
                            "b": bid,
                            "a_pos": (ax, ay),
                            "b_pos": (bx, by),
                            "min_dsep": min_dsep,
                        }
                    )

    return {
        "overlaps": overlaps,
        "left_to_right_violations": lr_violations,
    }

