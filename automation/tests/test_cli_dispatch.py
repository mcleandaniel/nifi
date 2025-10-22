from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, Tuple

from click.testing import CliRunner

from nifi_automation.app.models import CommandResult
from nifi_automation.cli.main import DISPATCH_TABLE, app

runner = CliRunner()

def _patch_dispatch(key: Tuple[str, str], handler):
    original = DISPATCH_TABLE[key]
    DISPATCH_TABLE[key] = handler
    return original


def test_run_flow_requires_flowfile() -> None:
    result = runner.invoke(app, ["run", "flow"])
    assert result.exit_code != 0
    combined = result.stdout + result.stderr
    assert "FLOWFILE" in combined


def test_run_flow_dispatch(tmp_path: Path) -> None:
    flow_spec = tmp_path / "NiFi_Flow.yaml"
    flow_spec.write_text("name: test")

    captured: Dict[str, Any] = {}

    def handler(*, config, flowfile: Path):
        captured["config"] = config
        captured["flowfile"] = flowfile
        return CommandResult(message="deployed")

    key = ("run", "flow")
    original = _patch_dispatch(key, handler)
    try:
        result = runner.invoke(app, ["run", "flow", str(flow_spec)])
    finally:
        DISPATCH_TABLE[key] = original

    assert result.exit_code == 0
    assert "deployed" in result.stdout
    assert captured["flowfile"] == flow_spec.resolve()
    assert captured["config"].dry_run is False


def test_status_flow_text_outputs_token() -> None:
    key = ("status", "flow")

    def handler(*, config):
        return CommandResult(status_token="UP")

    original = _patch_dispatch(key, handler)
    try:
        result = runner.invoke(app, ["status", "flow"])
    finally:
        DISPATCH_TABLE[key] = original

    assert result.exit_code == 0
    assert result.stdout.strip() == "UP"


def test_dry_run_rejected_for_status() -> None:
    result = runner.invoke(app, ["status", "flow", "--dry-run"])
    assert result.exit_code != 0
    assert "dry-run" in result.stderr.lower()


def test_truncate_connections_supports_flags() -> None:
    captured: Dict[str, Any] = {}

    def handler(*, config, force: bool, max_messages):
        captured["force"] = force
        captured["max_messages"] = max_messages
        return CommandResult(message="truncated")

    key = ("truncate", "connections")
    original = _patch_dispatch(key, handler)
    try:
        result = runner.invoke(
            app,
            [
                "truncate",
                "connections",
                "--force",
                "--max",
                "100",
            ],
        )
    finally:
        DISPATCH_TABLE[key] = original

    assert result.exit_code == 0
    assert "truncated" in result.stdout
    assert captured["force"] is True
    assert captured["max_messages"] == 100


def test_force_flag_rejected_for_other_commands() -> None:
    result = runner.invoke(app, ["status", "processors", "--force"])
    assert result.exit_code != 0
    assert "force" in result.stderr.lower()


def test_module_entrypoint_invocation() -> None:
    env = os.environ.copy()
    project_root = Path(__file__).resolve().parents[2]
    src_path = project_root / "src"
    env["PYTHONPATH"] = f"{src_path}{os.pathsep}{env.get('PYTHONPATH', '')}"
    completed = subprocess.run(
        [sys.executable, "-m", "nifi_automation.cli.main", "--help"],
        capture_output=True,
        text=True,
        env=env,
    )
    assert completed.returncode == 0
    assert "Usage:" in completed.stdout


def test_validate_layout_dispatch(tmp_path: Path) -> None:
    captured = {}

    def handler(*, config):
        captured["called"] = True
        return CommandResult(message="layout ok")

    key = ("validate", "layout")
    original = DISPATCH_TABLE.get(key)
    DISPATCH_TABLE[key] = handler  # type: ignore[assignment]
    try:
        result = runner.invoke(app, ["validate", "layout"])
    finally:
        if original is not None:
            DISPATCH_TABLE[key] = original
    assert result.exit_code == 0
    assert captured.get("called") is True
