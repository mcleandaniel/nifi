from __future__ import annotations

import socket
import subprocess
import time
import os
import pytest


def _port_open(host: str, port: int, timeout: float = 1.0) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(timeout)
        try:
            s.connect((host, port))
            return True
        except OSError:
            return False


@pytest.fixture(scope="session", autouse=True)
def ensure_http_pg_running() -> None:
    # Start processors (idempotent); rely on integration runner having deployed the flow
    subprocess.call([
        "python", "-m", "nifi_automation.cli.main", "up", "flow", "--output", "json"
    ])
    host = os.getenv("NIFI_HTTP_TEST_HOST", "127.0.0.1")
    port = int(os.getenv("NIFI_HTTP_TEST_PORT", "18081"))
    # Readiness probe up to ~10s
    deadline = time.time() + 10.0
    while time.time() < deadline:
        if _port_open(host, port, timeout=0.5):
            return
        time.sleep(0.2)
    # Hard fail: external trigger must be reachable
    raise AssertionError(f"HttpServerWorkflow not listening on {host}:{port} after readiness window")

