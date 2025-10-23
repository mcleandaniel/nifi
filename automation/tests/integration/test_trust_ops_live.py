import os
import pytest
import subprocess


pytestmark = [pytest.mark.integration, pytest.mark.tools]


def _cli(*args: str) -> int:
    cmd = ["python", "-m", "nifi_automation.cli.main", *args]
    return subprocess.call(cmd)


def test_trust_ops_cycle_live():
    # Requires a running NiFi per project .env
    ts_name = "it-local-nifi"
    ts_pass = "changeMe123!"
    ts_alias = "it-nifi-https"
    # Purge
    assert _cli("purge", "flow", "--output", "json") == 0
    # Add localhost:8443 (default JKS)
    assert _cli(
        "add", "trust",
        "--ts-name", ts_name,
        "--ts-password", ts_pass,
        "--trust-url", "https://localhost:8443",
        "--ts-alias", ts_alias,
        "--output", "json",
    ) == 0
    # Inspect (default JKS)
    assert _cli("inspect", "trust", "--ts-name", ts_name, "--ts-password", ts_pass, "--output", "json") == 0
    # Remove alias
    assert _cli("remove", "trust", "--ts-name", ts_name, "--ts-password", ts_pass, "--ts-alias", ts_alias, "--output", "json") == 0
