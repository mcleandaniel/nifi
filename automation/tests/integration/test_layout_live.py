from __future__ import annotations

import httpx
import pytest

from nifi_automation.auth import AuthenticationError, obtain_access_token
from nifi_automation.config import build_settings
from nifi_automation.infra.layout_checker import check_layout
from nifi_automation.infra.nifi_client import NiFiClient


def _ensure_reachable() -> tuple[NiFiClient, str]:
    settings = build_settings(None, None, None, False, 10.0)
    try:
        token = obtain_access_token(settings)
    except AuthenticationError as exc:
        pytest.skip(f"Skipping layout test: authentication failed ({exc})")
    except httpx.TransportError as exc:
        pytest.skip(f"Skipping layout test: NiFi not reachable ({exc})")
    client = NiFiClient.from_settings(settings, token)
    return client, token


def test_no_overlaps_after_deploy():
    client, _ = _ensure_reachable()
    with client:
        report = check_layout(client)
        assert report["overlaps"] == [], f"Overlapping processors: {report['overlaps']}"
        # Left-to-right violations are informative for now; do not fail the test
        # but include them in the test output if present for visibility.
        if report["left_to_right_violations"]:
            pytest.skip(f"Left-to-right issues observed: {len(report['left_to_right_violations'])}")

