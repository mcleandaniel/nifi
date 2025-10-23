from __future__ import annotations

import os
import socket
import subprocess
import time
from pathlib import Path

import httpx
import pytest

from nifi_automation.auth import AuthenticationError, obtain_access_token
from nifi_automation.config import build_settings
from nifi_automation.infra.nifi_client import NiFiClient
from nifi_automation.infra import purge_adapter
from nifi_automation.controller_registry import ensure_root_controller_services
from nifi_automation.flow_builder import deploy_flow_from_file, start_processors


HARNESS_SRC = Path("automation/flows/library/http_library_harness.yaml")
HARNESS_OUT = Path("automation/flows/library/http_library_harness_composed.yaml")


def _port_open(host: str, port: int, timeout: float = 1.0) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(timeout)
        try:
            s.connect((host, port))
            return True
        except OSError:
            return False


@pytest.fixture(scope="session")
def nifi_session():
    settings = build_settings(None, None, None, False, 10.0)
    try:
        token = obtain_access_token(settings)
    except (AuthenticationError, httpx.TransportError) as exc:
        pytest.skip(f"Skipping LibraryHarnessHTTP tests: NiFi not reachable/auth failed ({exc})")
    with NiFiClient.from_settings(settings, token) as client:  # type: ignore[arg-type]
        yield client


@pytest.fixture(scope="session", autouse=True)
def compose_and_deploy_harness(nifi_session: NiFiClient):
    # Compose the harness with library PGs inlined
    subprocess.check_call([
        "python",
        "automation/scripts/compose_with_library.py",
        "--input",
        str(HARNESS_SRC),
        "--out",
        str(HARNESS_OUT),
    ])

    # Clean slate to avoid controller service conflicts, then ensure manifest services
    purge_adapter.graceful_purge(nifi_session)
    service_map = ensure_root_controller_services(nifi_session)

    # Deploy the composed harness and start processors
    deploy_flow_from_file(nifi_session, HARNESS_OUT, controller_service_map=service_map)
    start_processors(nifi_session)

    # Readiness: wait for HTTP listener
    host = os.getenv("NIFI_HTTP_TEST_HOST", "127.0.0.1")
    port = int(os.getenv("NIFI_HTTP_TEST_PORT", "18081"))
    deadline = time.time() + 10.0
    while time.time() < deadline:
        if _port_open(host, port, timeout=0.5):
            return
        time.sleep(0.2)
    raise AssertionError(f"LibraryHarnessHTTP not listening on {host}:{port} after readiness window")

