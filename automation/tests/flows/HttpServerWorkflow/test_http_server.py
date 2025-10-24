from __future__ import annotations

import socket
import time

import httpx
import pytest


def _port_open(host: str, port: int, timeout: float = 1.0) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(timeout)
        try:
            s.connect((host, port))
            return True
        except OSError:
            return False


@pytest.mark.integration
def test_http_server_returns_204() -> None:
    host = "localhost"
    port = 18081
    deadline = time.time() + 10.0
    while time.time() < deadline:
        if _port_open(host, port, timeout=0.5):
            break
        time.sleep(0.2)
    url = f"http://{host}:{port}/test"
    resp = httpx.get(url, timeout=5.0)
    assert resp.status_code == 204
