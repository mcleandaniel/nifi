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
        pytest.skip(f"Skipping final-state test: unable to authenticate to NiFi ({exc}).")
    except httpx.TransportError as exc:
        pytest.skip(f"Skipping final-state test: NiFi not reachable ({exc}).")


def _run_cli(args: list[str]) -> dict[str, object]:
    env = _build_cli_env()
    cmd = [sys.executable, "-m", "nifi_automation.cli.main"] + args
    completed = subprocess.run(cmd, capture_output=True, text=True, env=env)
    assert completed.returncode == 0, (
        f"CLI command failed ({completed.returncode}): {cmd}\nSTDOUT: {completed.stdout}\nSTDERR: {completed.stderr}"
    )
    stdout = completed.stdout.strip() or "{}"
    try:
        return json.loads(stdout)
    except json.JSONDecodeError:
        return {"text": stdout}


@pytest.mark.integration
def test_final_processors_running() -> None:
    """Ensure the environment ends with processors RUNNING for operator convenience."""
    _ensure_nifi_available()
    _run_cli(["start", "processors", "--output", "json"])
    out = _run_cli(["status", "processors", "--output", "json"])
    assert out.get("status") == "RUNNING"
