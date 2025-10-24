"""Application-layer orchestrations for NiFi flow operations."""

from __future__ import annotations

import time
from pathlib import Path
import sys

from ..infra import ctrl_adapter, deploy_adapter, diag_adapter, purge_adapter, status_adapter
from .client import open_client
from .errors import TimeoutError, ValidationError
from .models import AppConfig, CommandResult, ExitCode
from .status_rules import rollup_controllers, rollup_flow, rollup_processors, rollup_connections

POLL_INTERVAL = 0.5


def _log(config: AppConfig, message: str) -> None:
    if config.verbose:
        print(message, file=sys.stderr)


def _await_stable_states(config: AppConfig, client) -> None:
    deadline = time.time() + config.timeout_seconds
    while True:
        processors = status_adapter.fetch_processors(client)["items"]
        controllers = status_adapter.fetch_controllers(client)["items"]
        proc_roll = rollup_processors(processors)
        ctrl_roll = rollup_controllers(controllers)
        if proc_roll.has_invalid or ctrl_roll.has_invalid:
            details = diag_adapter.gather_validation_details(client)
            raise ValidationError("Invalid components detected", details=details)
        if not proc_roll.has_transitional and not ctrl_roll.has_transitional:
            return
        if time.time() > deadline:
            raise TimeoutError("Components did not settle into a stable state before timeout")
        time.sleep(POLL_INTERVAL)


def _collect_flow_status(client):
    processors = status_adapter.fetch_processors(client)["items"]
    controllers = status_adapter.fetch_controllers(client)["items"]
    ports = status_adapter.fetch_ports(client)["items"]
    proc_roll = rollup_processors(processors)
    ctrl_roll = rollup_controllers(controllers)
    # Ports are reported separately; for now do not gate flow status on them.
    from .status_rules import rollup_ports  # local import to avoid cycle

    port_roll = rollup_ports(ports)
    status, details = rollup_flow(proc_roll, ctrl_roll)
    details["ports"] = {"counts": port_roll.counts, "worst": port_roll.worst}
    return status, proc_roll, ctrl_roll, details


def run_flow(*, config: AppConfig, flowfile: Path) -> CommandResult:
    if config.dry_run:
        with open_client(config) as client:
            _log(config, "[flow] generating dry-run deployment plan")
            result = deploy_adapter.deploy_flow(client, flowfile, dry_run=True)
        return CommandResult(message="Dry-run deployment plan", data=result["summary"])

    with open_client(config) as client:
        try:
            # Baseline last bulletin id to filter runtime errors for this session
            baseline_last_id = 0
            try:
                payload = client.get_bulletins(limit=100, after=None)
                if payload:
                    baseline_last_id = max(int(it.get("id", 0)) for it in payload if isinstance(it.get("id"), int) or str(it.get("id")).isdigit())
            except Exception:
                baseline_last_id = 0
            _log(config, "[flow] purging NiFi root before deployment")
            purge_adapter.graceful_purge(client)
            _log(config, "[flow] deploying flow specification")
            deploy_result = deploy_adapter.deploy_flow(client, flowfile, dry_run=False)
            _log(config, "[flow] validating deployed topology against spec")
            topo = diag_adapter.validate_deployed_topology(client, flowfile)
            if not topo.get("ok", False):
                raise ValidationError("Topology validation failed (missing processors or count mismatch)", details={"topology": topo})
            # Layout validation: attach report and fail when overlaps exist
            from ..infra.layout_checker import check_layout as _check_layout

            layout = _check_layout(client)
            if layout.get("overlaps"):
                return CommandResult(
                    exit_code=ExitCode.VALIDATION,
                    message=f"Layout overlaps detected: {len(layout['overlaps'])}",
                    data={"process_group_id": deploy_result.get("process_group_id")},
                    details={"layout": layout},
                )

            _log(config, "[flow] waiting for deployed components to stabilize")
            _await_stable_states(config, client)
            # Pre-emptively stop Tools_* HTTP listeners to free ports used by workflows
            ctrl_adapter.stop_tools_http_listeners(client)
            _log(config, "[flow] enabling controller services")
            ctrl_adapter.enable_all_controllers(client, timeout=config.timeout_seconds)
            _log(config, "[flow] starting processors")
            ctrl_adapter.start_all_processors(client, timeout=config.timeout_seconds)
            # Immediately stop Tools_* HTTP listeners to avoid port conflicts with workflow listeners
            ctrl_adapter.stop_tools_http_listeners(client)
            _await_stable_states(config, client)
            status_token, proc_roll, ctrl_roll, details = _collect_flow_status(client)
            # Include connections rollup and elevate status if backpressure is hit
            connections = status_adapter.fetch_connections(client)["items"]
            conn_roll = rollup_connections(connections)
            details["connections"] = {"counts": conn_roll.counts, "worst": conn_roll.worst}
            if conn_roll.worst == "BLOCKED":
                status_token = "INVALID"
            # Require all processors RUNNING after start
            if status_token not in {"INVALID", "TRANSITION"} and not proc_roll.all_running:
                status_token = "INVALID"
            # Check for runtime ERROR bulletins emitted after baseline and flag as invalid
            try:
                bulletins = client.get_bulletins(limit=200, after=None)
                new_errors = [b for b in bulletins if (b.get("level") == "ERROR" and int(b.get("id", 0)) > baseline_last_id)]
                if new_errors:
                    details = details or {}
                    details["bulletins"] = {"errors": new_errors}
                    status_token = "INVALID"
            except Exception:
                pass
        except ValidationError as exc:
            details = exc.details or diag_adapter.gather_validation_details(client)
            return CommandResult(
                exit_code=ExitCode.VALIDATION,
                message=str(exc),
                data={"process_group_id": deploy_result.get("process_group_id")},
                details=details,
            )

    if status_token in {"INVALID", "TRANSITION"}:
        return CommandResult(
            exit_code=ExitCode.VALIDATION,
            status_token=status_token,
            data={
                "processors": proc_roll.counts,
                "controllers": ctrl_roll.counts,
                "process_group_id": deploy_result.get("process_group_id"),
            },
            details=details,
        )
    return CommandResult(
        status_token=status_token,
        data={
            "processors": proc_roll.counts,
            "controllers": ctrl_roll.counts,
            "process_group_id": deploy_result.get("process_group_id"),
        },
        details=details,
    )


def deploy_flow(*, config: AppConfig, flowfile: Path) -> CommandResult:
    with open_client(config) as client:
        if config.dry_run:
            _log(config, "[flow] generating dry-run deployment plan")
            result = deploy_adapter.deploy_flow(client, flowfile, dry_run=True)
            return CommandResult(message="Dry-run deployment plan", data=result["summary"])
        _log(config, "[flow] purging NiFi root before deployment")
        purge_adapter.graceful_purge(client)
        _log(config, "[flow] deploying flow specification")
        result = deploy_adapter.deploy_flow(client, flowfile, dry_run=False)
        from ..infra.layout_checker import check_layout as _check_layout
        layout = _check_layout(client)
        if layout.get("overlaps"):
            return CommandResult(
                exit_code=ExitCode.VALIDATION,
                message=f"Layout overlaps detected: {len(layout['overlaps'])}",
                data={
                    "process_group_id": result.get("process_group_id"),
                    "controller_services": result.get("controller_services"),
                },
                details={"layout": layout},
            )
        _log(config, "[flow] validating deployed topology against spec")
        topo = diag_adapter.validate_deployed_topology(client, flowfile)
        if not topo.get("ok", False):
            raise ValidationError("Topology validation failed (missing processors or count mismatch)", details={"topology": topo})
        status_token, proc_roll, ctrl_roll, details = _collect_flow_status(client)
        connections = status_adapter.fetch_connections(client)["items"]
        conn_roll = rollup_connections(connections)
        details["connections"] = {"counts": conn_roll.counts, "worst": conn_roll.worst}
        if conn_roll.worst == "BLOCKED":
            status_token = "INVALID"
    exit_code = ExitCode.VALIDATION if status_token == "INVALID" else ExitCode.SUCCESS
    return CommandResult(
        exit_code=exit_code,
        message="Flow deployed" if exit_code == ExitCode.SUCCESS else "Flow deployment has invalid components",
        data={
            "process_group_id": result.get("process_group_id"),
            "controller_services": result.get("controller_services"),
            "status": status_token,
            "processors": proc_roll.counts,
            "controllers": ctrl_roll.counts,
        },
        details=details if exit_code != ExitCode.SUCCESS else {},
    )


def up_flow(*, config: AppConfig) -> CommandResult:
    with open_client(config) as client:
        try:
            baseline_last_id = 0
            try:
                payload = client.get_bulletins(limit=100, after=None)
                if payload:
                    baseline_last_id = max(int(it.get("id", 0)) for it in payload if isinstance(it.get("id"), int) or str(it.get("id")).isdigit())
            except Exception:
                baseline_last_id = 0
            # Pre-emptively stop Tools_* HTTP listeners
            ctrl_adapter.stop_tools_http_listeners(client)
            _log(config, "[flow] enabling controller services")
            ctrl_adapter.enable_all_controllers(client, timeout=config.timeout_seconds)
            _log(config, "[flow] starting processors")
            ctrl_adapter.start_all_processors(client, timeout=config.timeout_seconds)
            # Stop Tools_* HTTP listeners to avoid port conflicts
            ctrl_adapter.stop_tools_http_listeners(client)
            _await_stable_states(config, client)
            status_token, proc_roll, ctrl_roll, details = _collect_flow_status(client)
            connections = status_adapter.fetch_connections(client)["items"]
            conn_roll = rollup_connections(connections)
            details["connections"] = {"counts": conn_roll.counts, "worst": conn_roll.worst}
            if conn_roll.worst == "BLOCKED":
                status_token = "INVALID"
            # Bulletin check after start
            try:
                bulletins = client.get_bulletins(limit=200, after=None)
                new_errors = [b for b in bulletins if (b.get("level") == "ERROR" and int(b.get("id", 0)) > baseline_last_id)]
                if new_errors:
                    details = details or {}
                    details["bulletins"] = {"errors": new_errors}
                    status_token = "INVALID"
            except Exception:
                pass
        except ValidationError as exc:
            details = exc.details or diag_adapter.gather_validation_details(client)
            return CommandResult(
                exit_code=ExitCode.VALIDATION,
                message=str(exc),
                details=details,
            )
    exit_code = ExitCode.VALIDATION if status_token in {"INVALID", "TRANSITION"} else ExitCode.SUCCESS
    return CommandResult(
        exit_code=exit_code,
        status_token=status_token,
        data={"processors": proc_roll.counts, "controllers": ctrl_roll.counts},
        details=details,
    )


def down_flow(*, config: AppConfig) -> CommandResult:
    with open_client(config) as client:
        _log(config, "[flow] stopping processors")
        ctrl_adapter.stop_all_processors(client, timeout=config.timeout_seconds)
        _log(config, "[flow] disabling controller services")
        ctrl_adapter.disable_all_controllers(client, timeout=config.timeout_seconds)
        status_token, proc_roll, ctrl_roll, details = _collect_flow_status(client)
        connections = status_adapter.fetch_connections(client)["items"]
        conn_roll = rollup_connections(connections)
        details["connections"] = {"counts": conn_roll.counts, "worst": conn_roll.worst}
        if conn_roll.worst == "BLOCKED":
            status_token = "INVALID"
    exit_code = ExitCode.VALIDATION if status_token == "INVALID" else ExitCode.SUCCESS
    return CommandResult(
        exit_code=exit_code,
        status_token=status_token,
        data={"processors": proc_roll.counts, "controllers": ctrl_roll.counts},
        details=details if exit_code != ExitCode.SUCCESS else {},
    )


def purge_flow(*, config: AppConfig) -> CommandResult:
    with open_client(config) as client:
        _log(config, "[flow] purging NiFi root")
        summary = purge_adapter.graceful_purge(client)
    return CommandResult(message="Purged NiFi root", data=summary)


def status_flow(*, config: AppConfig) -> CommandResult:
    with open_client(config) as client:
        status_token, proc_roll, ctrl_roll, details = _collect_flow_status(client)
        # Always compute ports and include in data for visibility
        from .status_rules import rollup_ports  # local import to avoid cycle

        ports = status_adapter.fetch_ports(client)["items"]
        port_roll = rollup_ports(ports)
        # Attach connection rollup in details for richer status payload
        connections = status_adapter.fetch_connections(client)["items"]
        conn_roll = rollup_connections(connections)
        details["connections"] = {"counts": conn_roll.counts, "worst": conn_roll.worst}
    exit_code = ExitCode.VALIDATION if status_token == "INVALID" else ExitCode.SUCCESS
    return CommandResult(
        exit_code=exit_code,
        status_token=status_token,
        data={
            "processors": proc_roll.counts,
            "controllers": ctrl_roll.counts,
            "connections": details.get("connections", {}),
            "ports": {"counts": port_roll.counts, "worst": port_roll.worst},
        },
        details=details if exit_code != ExitCode.SUCCESS else {},
    )


def inspect_flow(*, config: AppConfig) -> CommandResult:
    with open_client(config) as client:
        diagnostics = diag_adapter.gather_validation_details(client)

    total_issues = len(diagnostics.get("invalid_processors", [])) + len(diagnostics.get("invalid_ports", []))
    message = "No invalid components" if total_issues == 0 else f"Found {total_issues} invalid components"
    return CommandResult(message=message, data=diagnostics)
