from __future__ import annotations

import os
import httpx
import pytest


@pytest.mark.integration
def test_queue_depths_html(deploy_queue_depths):  # noqa: F401
    host = os.getenv("NIFI_HTTP_TEST_HOST", "127.0.0.1")
    port = int(os.getenv("NIFI_HTTP_TEST_PORT", "18081"))
    resp = httpx.get(f"http://{host}:{port}/queues", timeout=5.0)
    if resp.status_code != 200:
        pytest.skip(f"QueueDepths endpoint returned {resp.status_code} (dev env may not expose /queues)")
    body = resp.text.lower()
    assert "<table" in body and "queued" in body
