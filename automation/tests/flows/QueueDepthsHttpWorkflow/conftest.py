from __future__ import annotations

import os
import socket
import time
from pathlib import Path

import httpx
import pytest

from nifi_automation.auth import AuthenticationError, obtain_access_token
from nifi_automation.config import build_settings
from nifi_automation.infra.nifi_client import NiFiClient
from nifi_automation.infra import purge_adapter
from nifi_automation.controller_registry import ensure_root_controller_services
from nifi_automation.app.trust_service import add as trust_add
from nifi_automation.app.models import AppConfig
from nifi_automation.flow_builder import deploy_flow_from_file, start_processors, FlowDeploymentError


SPEC = Path("automation/flows/queue_depths_http.yaml")


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
        pytest.skip(f"Skipping QueueDepthsHttpWorkflow tests: NiFi not reachable/auth failed ({exc})")
    with NiFiClient.from_settings(settings, token) as client:  # type: ignore[arg-type]
        yield client


@pytest.fixture(scope="session", autouse=True)
def deploy_queue_depths(nifi_session: NiFiClient):
    # Bootstrap trust and a root SSL Context Service ('Workflow SSL') so InvokeHTTP can call https://localhost:8443
    # This runs a minimal tools flow internally and purges as part of the operation.
    cfg = AppConfig(
        base_url=str(nifi_session._client.base_url),
        username=None,
        password=None,
        token=nifi_session._client.headers.get('Authorization', '').replace('Bearer ', ''),
        timeout_seconds=10.0,
        output='json',
        verbose=False,
        dry_run=False,
        ts_name='workflow',
        ts_pass='abcd1234',
        ts_type='PKCS12',
        trust_url='https://SELF:8443',
        ts_alias='nifi-https',
    )
    try:
        trust_add(config=cfg)
    except Exception:
        # If trust tools are unavailable, proceed; the flow may fail at runtime but deploy should still succeed
        pass
    else:
        # Remove the tools PG to avoid port conflicts on 18081
        try:
            resp = nifi_session._client.get("/flow/process-groups/root")
            resp.raise_for_status()
            flow = resp.json().get("processGroupFlow", {}).get("flow", {})
            for pg in flow.get("processGroups") or []:
                comp = pg.get("component", {})
                if comp.get("name") == "Tools_Trust_Add_HTTP":
                    ent = nifi_session._client.get(f"/process-groups/{comp.get('id')}").json()
                    rev = ent.get("revision", {}).get("version", 0)
                    nifi_session._client.delete(
                        f"/process-groups/{comp.get('id')}", params={"version": rev, "clientId": "queue-depths-setup", "recursive": "true"}
                    ).raise_for_status()
                    break
        except Exception:
            pass

    # Ensure manifest services (HTTP Context Map, JSON readers/writers, etc.)
    service_map = ensure_root_controller_services(nifi_session)
    # Opportunistically map 'ssl-context' alias to the 'Workflow SSL' service id if present
    try:
        resp = nifi_session._client.get(
            "/flow/process-groups/root/controller-services",
            params={"includeInherited": "false"},
        )
        resp.raise_for_status()
        for svc in resp.json().get("controllerServices") or []:
            comp = svc.get("component", {})
            if comp.get("type") == "org.apache.nifi.ssl.StandardSSLContextService" and comp.get("name") == "Workflow SSL":
                service_map["ssl-context"] = comp.get("id")
                break
    except Exception:
        pass

    # Deploy the QueueDepths flow and start processors (strict: must reach RUNNING)
    deploy_flow_from_file(nifi_session, SPEC, controller_service_map=service_map)
    start_processors(nifi_session, timeout=60.0)

    # Readiness: wait for HTTP listener
    host = os.getenv("NIFI_HTTP_TEST_HOST", "127.0.0.1")
    port = int(os.getenv("NIFI_HTTP_TEST_PORT", "18081"))
    deadline = time.time() + 10.0
    while time.time() < deadline:
        if _port_open(host, port, timeout=0.5):
            return
        time.sleep(0.2)
    raise AssertionError(f"QueueDepthsHttpWorkflow not listening on {host}:{port} after readiness window")
