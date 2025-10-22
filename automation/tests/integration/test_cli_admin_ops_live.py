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
        pytest.skip(f"Skipping admin ops test: unable to authenticate to NiFi ({exc}).")
    except httpx.TransportError as exc:
        pytest.skip(f"Skipping admin ops test: NiFi not reachable ({exc}).")


def _run_cli(args: list[str]) -> dict[str, object]:
    env = _build_cli_env()
    cmd = [sys.executable, "-m", "nifi_automation.cli.main"] + args
    completed = subprocess.run(cmd, capture_output=True, text=True, env=env)
    assert (
        completed.returncode == 0
    ), f"CLI command failed ({completed.returncode}): {cmd}\nSTDOUT: {completed.stdout}\nSTDERR: {completed.stderr}"
    stdout = completed.stdout.strip() or "{}"
    try:
        return json.loads(stdout)
    except json.JSONDecodeError:
        return {"text": stdout}


@pytest.mark.integration
def test_cli_start_stop_enable_disable() -> None:
    _ensure_nifi_available()

    # Ensure something is deployed; reuse aggregate spec
    flow_spec = Path("automation/flows/NiFi_Flow.yaml").resolve()
    _run_cli(["deploy", "flow", str(flow_spec), "--output", "json"])

    # Processors: stop then start
    out = _run_cli(["stop", "processors", "--output", "json"])
    assert out["data"]["worst"] in {"STOPPED", "RUNNING"}
    out = _run_cli(["status", "processors", "--output", "json"])
    assert out["data"]["worst"] in {"STOPPED", "RUNNING"}
    out = _run_cli(["start", "processors", "--output", "json"])
    assert out["data"]["worst"] == "RUNNING"

    # Ports: stop then start
    out = _run_cli(["stop", "ports", "--output", "json"])
    assert out["data"]["worst"] in {"STOPPED", "RUNNING"}
    out = _run_cli(["status", "ports", "--output", "json"])
    assert out["data"]["worst"] in {"STOPPED", "RUNNING", "DISABLED"}
    out = _run_cli(["start", "ports", "--output", "json"])
    assert out["data"]["worst"] == "RUNNING"

    # Controllers: stop processors/ports first, then disable, then enable
    _run_cli(["stop", "processors", "--output", "json"])
    _run_cli(["stop", "ports", "--output", "json"])
    out = _run_cli(["disable", "controllers", "--output", "json"])
    assert out["data"]["worst"] in {"DISABLED", "ENABLED"}
    out = _run_cli(["status", "controllers", "--output", "json"])
    assert out["data"]["worst"] in {"DISABLED", "ENABLED"}
    out = _run_cli(["enable", "controllers", "--output", "json"])
    assert out["data"]["worst"] == "ENABLED"

    # Leave the environment in a running state for subsequent workflows
    _run_cli(["start", "ports", "--output", "json"])
    out = _run_cli(["start", "processors", "--output", "json"])
    assert out["data"]["worst"] == "RUNNING"
