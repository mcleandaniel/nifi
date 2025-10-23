from __future__ import annotations

import os
import httpx
import pytest


@pytest.mark.integration
def test_library_harness_http_returns_204(compose_and_deploy_harness):  # noqa: F401 (fixture use)
    host = os.getenv("NIFI_HTTP_TEST_HOST", "127.0.0.1")
    port = int(os.getenv("NIFI_HTTP_TEST_PORT", "18081"))
    path = os.getenv("NIFI_HTTP_TEST_PATH", "/libtest")
    url = f"http://{host}:{port}{path}"
    resp = httpx.get(url, timeout=5.0)
    assert resp.status_code == 204

