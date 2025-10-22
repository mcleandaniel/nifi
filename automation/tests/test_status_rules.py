from __future__ import annotations

from nifi_automation.app.status_rules import (
    rollup_connections,
    rollup_controllers,
    rollup_flow,
    rollup_processors,
    rollup_ports,
)


def test_rollup_processors_identifies_transitional() -> None:
    items = [{"state": "RUNNING"}, {"state": "STOPPING"}]
    rollup = rollup_processors(items)
    assert rollup.worst == "STOPPING"
    assert rollup.has_transitional is True
    assert rollup.has_invalid is False


def test_rollup_controllers_invalid() -> None:
    items = [{"state": "ENABLED"}, {"state": "INVALID", "validationErrors": ["bad"]}]
    rollup = rollup_controllers(items)
    assert rollup.worst == "INVALID"
    assert rollup.has_invalid is True


def test_rollup_connections_blocked_and_empty() -> None:
    items = [
        {"queuedCount": 0, "backpressureObjectThreshold": 10, "percentUseCount": 0},
        {"queuedCount": 12, "backpressureObjectThreshold": 10, "percentUseCount": 100},
    ]
    rollup = rollup_connections(items)
    assert rollup.worst == "BLOCKED"
    assert rollup.counts["BLOCKED"] == 1
    assert rollup.counts["EMPTY"] == 1


def test_rollup_flow_rules() -> None:
    proc = rollup_processors([{"state": "RUNNING"}])
    ctrl = rollup_controllers([{"state": "ENABLED"}])
    status, _ = rollup_flow(proc, ctrl)
    assert status == "UP"

    proc_invalid = rollup_processors([{ "state": "INVALID" }])
    status_invalid, _ = rollup_flow(proc_invalid, ctrl)
    assert status_invalid == "INVALID"

    proc_transition = rollup_processors([{"state": "STARTING"}])
    status_transition, _ = rollup_flow(proc_transition, ctrl)
    assert status_transition == "TRANSITION"


def test_zero_processors_not_up() -> None:
    # When there are zero processors, do not claim everything is RUNNING
    proc = rollup_processors([])
    ctrl = rollup_controllers([{"state": "ENABLED"}])
    assert proc.total == 0
    assert proc.all_running is False
    status, _ = rollup_flow(proc, ctrl)
    assert status != "UP"


def test_rollup_ports_states() -> None:
    items = [
        {"state": "RUNNING"},
        {"state": "STOPPED"},
        {"state": "DISABLED"},
    ]
    roll = rollup_ports(items)
    assert roll.counts["RUNNING"] == 1
    assert roll.counts["STOPPED"] == 1
    assert roll.counts["DISABLED"] == 1
    assert roll.worst in {"RUNNING", "STOPPED", "DISABLED"}
