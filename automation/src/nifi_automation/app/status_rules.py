"""Severity ranking and roll-up rules for NiFi component states."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, Tuple

"""
Processor severity policy

Rationale update: We treat STOPPED as a non-acceptable steady state for general
"flow up" checks. Operators expect the platform to end RUNNING after deploy and
after admin flows complete unless a test explicitly leaves it otherwise. To
surface this clearly in roll-ups, STOPPED must rank worse than RUNNING so the
"worst" token reports STOPPED when any processors are not running.

Severity order (high → low): INVALID > STOPPING > STARTING > STOPPED > RUNNING
"""
PROCESSOR_SEVERITY = {
    "INVALID": 4,
    "STOPPING": 3,
    "STARTING": 2,
    "STOPPED": 1,
    "RUNNING": 0,
}

CONTROLLER_SEVERITY = {
    "INVALID": 3,
    "DISABLING": 2,
    "ENABLING": 1,
    "ENABLED": 0,
    "DISABLED": 0,
}

CONNECTION_SEVERITY = {
    "BLOCKED": 2,
    "HEALTHY": 1,
    "EMPTY": 0,
}

# Ports rollup: treat RUNNING and STOPPED (disabled) as acceptable; anything
# else is transitional/invalid. We still compute worst severity for visibility.
PORT_SEVERITY = {
    "INVALID": 3,
    "RUNNING": 0,
    "STOPPED": 0,
    "DISABLED": 0,
}


@dataclass(slots=True)
class ProcessorRollup:
    worst: str
    counts: Dict[str, int]
    total: int
    has_invalid: bool
    has_transitional: bool
    all_running: bool
    all_stopped: bool


@dataclass(slots=True)
class ControllerRollup:
    worst: str
    counts: Dict[str, int]
    total: int
    has_invalid: bool
    has_transitional: bool
    all_enabled: bool
    all_disabled: bool


@dataclass(slots=True)
class ConnectionRollup:
    worst: str
    counts: Dict[str, int]
    total: int


def _worst_state(counts: Dict[str, int], severity_map: Dict[str, int], default: str) -> str:
    worst = default
    worst_score = severity_map.get(default, -1)
    for state, count in counts.items():
        if count <= 0:
            continue
        score = severity_map.get(state, max(severity_map.values()))
        if score > worst_score:
            worst = state
            worst_score = score
    return worst


def rollup_processors(items: Iterable[Dict[str, object]]) -> ProcessorRollup:
    counts: Dict[str, int] = {}
    total = 0
    has_invalid = False
    has_transitional = False
    for item in items:
        state = str(item.get("state", "UNKNOWN")).upper()
        counts[state] = counts.get(state, 0) + 1
        total += 1
        if state == "INVALID":
            has_invalid = True
        elif state in {"STARTING", "STOPPING"}:
            has_transitional = True
        elif state not in {"RUNNING", "STOPPED"}:
            has_transitional = True
    worst = _worst_state(counts, PROCESSOR_SEVERITY, "RUNNING")
    # Consider zero processors as not "all running" to avoid reporting UP
    # when nothing is deployed. This forces callers to consider topology
    # validity separately and prevents false-positives.
    all_running = total > 0 and counts.get("RUNNING", 0) == total
    all_stopped = total > 0 and counts.get("STOPPED", 0) == total
    return ProcessorRollup(
        worst=worst,
        counts=counts,
        total=total,
        has_invalid=has_invalid,
        has_transitional=has_transitional,
        all_running=all_running,
        all_stopped=all_stopped,
    )


def rollup_controllers(items: Iterable[Dict[str, object]]) -> ControllerRollup:
    counts: Dict[str, int] = {}
    total = 0
    has_invalid = False
    has_transitional = False
    for item in items:
        state = str(item.get("state", "UNKNOWN")).upper()
        counts[state] = counts.get(state, 0) + 1
        total += 1
        if state == "INVALID":
            has_invalid = True
        elif state in {"ENABLING", "DISABLING"}:
            has_transitional = True
        elif state not in {"ENABLED", "DISABLED"}:
            has_transitional = True
    worst = _worst_state(counts, CONTROLLER_SEVERITY, "ENABLED")
    all_enabled = total == 0 or counts.get("ENABLED", 0) == total
    all_disabled = total > 0 and counts.get("DISABLED", 0) == total
    return ControllerRollup(
        worst=worst,
        counts=counts,
        total=total,
        has_invalid=has_invalid,
        has_transitional=has_transitional,
        all_enabled=all_enabled,
        all_disabled=all_disabled,
    )


def rollup_connections(items: Iterable[Dict[str, object]]) -> ConnectionRollup:
    counts: Dict[str, int] = {"EMPTY": 0, "HEALTHY": 0, "BLOCKED": 0}
    total = 0
    for item in items:
        total += 1
        queued = int(item.get("queuedCount", 0))
        threshold = int(item.get("backpressureObjectThreshold", 0))
        percent_count = float(item.get("percentUseCount", 0.0))
        percent_bytes = float(item.get("percentUseBytes", 0.0))
        if (threshold and queued >= threshold) or percent_count >= 100.0 or percent_bytes >= 100.0:
            key = "BLOCKED"
        elif queued > 0:
            key = "HEALTHY"
        else:
            key = "EMPTY"
        counts[key] = counts.get(key, 0) + 1
    worst = _worst_state(counts, CONNECTION_SEVERITY, "EMPTY")
    return ConnectionRollup(worst=worst, counts=counts, total=total)


@dataclass(slots=True)
class PortRollup:
    worst: str
    counts: Dict[str, int]
    total: int
    has_invalid: bool


def rollup_ports(items: Iterable[Dict[str, object]]) -> PortRollup:
    counts: Dict[str, int] = {}
    total = 0
    has_invalid = False
    for item in items:
        state = str(item.get("state", "UNKNOWN")).upper()
        counts[state] = counts.get(state, 0) + 1
        total += 1
        if state == "INVALID":
            has_invalid = True
    worst = _worst_state(counts, PORT_SEVERITY, "RUNNING")
    return PortRollup(worst=worst, counts=counts, total=total, has_invalid=has_invalid)


def rollup_flow(processors: ProcessorRollup, controllers: ControllerRollup) -> Tuple[str, Dict[str, object]]:
    if processors.has_invalid or controllers.has_invalid:
        status = "INVALID"
    elif processors.has_transitional or controllers.has_transitional:
        status = "TRANSITION"
    elif processors.all_running and controllers.all_enabled:
        status = "UP"
    elif processors.all_stopped and controllers.all_disabled:
        status = "DOWN"
    else:
        status = "HEALTHY"
    details: Dict[str, object] = {
        "processors": {"counts": processors.counts, "worst": processors.worst},
        "controllers": {"counts": controllers.counts, "worst": controllers.worst},
    }
    return status, details
