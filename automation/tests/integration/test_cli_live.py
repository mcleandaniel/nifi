from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import httpx
import pytest

from nifi_automation.auth import AuthenticationError, obtain_access_token
from nifi_automation.config import build_settings


def _build_cli_env() -> dict[str, str]:
    env = os.environ.copy()
    project_root = Path(__file__).resolve().parents[3]
    src_path = project_root / "automation" / "src"
    existing = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = f"{src_path}{os.pathsep}{existing}" if existing else str(src_path)
    return env


def _ensure_nifi_available() -> None:
    settings = build_settings(None, None, None, verify_ssl=None, timeout=10.0)
    try:
        obtain_access_token(settings)
    except AuthenticationError as exc:
        pytest.skip(f"Skipping CLI live test: unable to authenticate to NiFi ({exc}).")
    except httpx.TransportError as exc:
        pytest.skip(f"Skipping CLI live test: NiFi not reachable ({exc}).")


def _run_cli(args: list[str]) -> dict[str, object]:
    env = _build_cli_env()
    cmd = [sys.executable, "-m", "nifi_automation.cli.main"] + args
    completed = subprocess.run(cmd, capture_output=True, text=True, env=env)
    assert (
        completed.returncode == 0
    ), f"CLI command failed ({completed.returncode}): {cmd}\nSTDOUT: {completed.stdout}\nSTDERR: {completed.stderr}"
    stdout = completed.stdout.strip()
    assert stdout, f"CLI command produced no JSON output: {cmd}\nSTDERR: {completed.stderr}"
    try:
        payload = json.loads(stdout)
    except json.JSONDecodeError as exc:  # pragma: no cover - defensive
        raise AssertionError(f"Invalid JSON output: {stdout}") from exc
    return payload


def test_cli_end_to_end():
    _ensure_nifi_available()

    # Always start from a clean environment.
    purge_payload = _run_cli(["purge", "flow", "--output", "json"])
    assert purge_payload["message"] == "Purged NiFi root"

    flow_spec = Path("automation/flows/groups-md/NiFi_Flow_groups.yaml").resolve()
    run_payload = _run_cli(["run", "flow", str(flow_spec), "--output", "json"])
    assert run_payload.get("status") == "UP"

    status_payload = _run_cli(["status", "flow", "--output", "json"])
    assert status_payload.get("status") in {"UP", "HEALTHY"}

    inspect_payload = _run_cli(["inspect", "flow", "--output", "json"])
    data = inspect_payload.get("data", {})
    assert data.get("invalid_processors") == []
    assert data.get("invalid_ports") == []

    controllers_payload = _run_cli(["status", "controllers", "--output", "json"])
    assert controllers_payload.get("status") in {"ENABLED", "DISABLED"}

    processors_payload = _run_cli(["status", "processors", "--output", "json"])
    assert processors_payload.get("status") in {"RUNNING", "STOPPED"}

    truncate_payload = _run_cli(["truncate", "connections", "--output", "json"])
    assert "connections" in truncate_payload.get("data", {})
