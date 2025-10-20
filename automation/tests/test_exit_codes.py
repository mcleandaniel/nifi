from __future__ import annotations

import json

from nifi_automation.app.models import CommandResult, ExitCode
from nifi_automation.cli.io import emit_error, emit_result


def test_emit_result_text_status(capsys):
    result = CommandResult(status_token="UP")
    exit_code = emit_result(result, output="text")
    captured = capsys.readouterr()
    assert exit_code == 0
    assert captured.out.strip() == "UP"
    assert captured.err == ""


def test_emit_result_json(capsys):
    result = CommandResult(
        message="details",
        data={"counts": {"running": 5}},
        exit_code=ExitCode.TIMEOUT,
    )
    exit_code = emit_result(result, output="json")
    captured = capsys.readouterr()
    assert exit_code == ExitCode.TIMEOUT
    payload = json.loads(captured.out)
    assert payload["message"] == "details"
    assert payload["data"]["counts"]["running"] == 5
    assert payload["exit_code"] == ExitCode.TIMEOUT
    assert captured.err == ""


def test_emit_error(capsys):
    exit_code = emit_error("boom", exit_code=ExitCode.HTTP_ERROR)
    captured = capsys.readouterr()
    assert exit_code == ExitCode.HTTP_ERROR
    assert captured.err.strip().endswith("boom")
