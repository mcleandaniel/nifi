from __future__ import annotations

import httpx
import pytest


@pytest.mark.integration
def test_http_server_returns_204() -> None:
    url = "http://localhost:18081/test"
    resp = httpx.get(url, timeout=5.0)
    assert resp.status_code == 204
