"""CLI handlers for ephemeral trust-store operations (create/add/remove/inspect)."""

from __future__ import annotations

import re
import time
from pathlib import Path
import secrets
from typing import Dict, Optional, Tuple

from .client import open_client
from .errors import BadInputError, TimeoutError
from .models import AppConfig, CommandResult, ExitCode
from ..infra import purge_adapter, deploy_adapter
import httpx


TOOLS_DIR = Path("automation/tools/flows/ops")
DEFAULT_TIMEOUT = 20.0
TOOLS_PORT = 18081


def _split_url(url: str) -> Tuple[str, int]:
    m = re.match(r"^https?://([^/:]+)(?::(\d+))?", url)
    if not m:
        raise BadInputError(f"Invalid URL: {url}")
    host = m.group(1)
    port = int(m.group(2) or 443)
    return host, port


def _find_pg_by_name(client, name: str) -> Optional[str]:
    resp = client._client.get("/flow/process-groups/root")
    resp.raise_for_status()
    for pg in resp.json().get("processGroupFlow", {}).get("flow", {}).get("processGroups", []) or []:
        comp = pg.get("component", {})
        if comp.get("name") == name:
            return comp.get("id")
    return None


def _find_processor_by_name(client, pg_id: str, name: str) -> Optional[str]:
    resp = client._client.get(f"/flow/process-groups/{pg_id}")
    resp.raise_for_status()
    flow = resp.json().get("processGroupFlow", {}).get("flow", {})
    for proc in flow.get("processors", []) or []:
        if proc.get("component", {}).get("name") == name:
            return proc.get("component", {}).get("id")
    return None


def _update_processor_properties(client, processor_id: str, props: Dict[str, str]) -> None:
    entity = client._client.get(f"/processors/{processor_id}").json()
    rev = entity.get("revision", {})
    comp = entity.get("component", {})
    cfg = comp.get("config", {})
    cfg_props = cfg.get("properties", {}) or {}
    cfg_props.update(props)
    cfg["properties"] = cfg_props
    body = {"revision": rev, "component": {"id": processor_id, "config": cfg}}
    client._client.put(f"/processors/{processor_id}", json=body).raise_for_status()


def _assert_pg_valid(client, pg_name: str) -> None:
    """Fail fast if any processor in the given PG is INVALID to avoid 404/empty responses."""
    pg_id = _find_pg_by_name(client, pg_name)
    if not pg_id:
        raise BadInputError(f"Process group '{pg_name}' not found after deploy")
    flow = client._client.get(f"/flow/process-groups/{pg_id}").json()["processGroupFlow"]["flow"]
    invalid = []
    for proc in flow.get("processors") or []:
        comp = proc.get("component", {})
        status = comp.get("validationStatus")
        if status not in {"VALID", "DISABLED"}:
            invalid.append({
                "name": comp.get("name"),
                "type": comp.get("type"),
                "errors": comp.get("validationErrors") or [],
            })
    if invalid:
        raise BadInputError(f"Invalid processors in tools PG '{pg_name}'", details=invalid)


def _wait_pg_ready(client, pg_name: str, *, timeout: float = 30.0, poll: float = 1.0) -> None:
    """Wait until all processors in the given PG are VALID (or DISABLED) and scheduled (RUNNING/STOPPED/DISABLED)."""
    pg_id = _find_pg_by_name(client, pg_name)
    if not pg_id:
        raise BadInputError(f"Process group '{pg_name}' not found after deploy")
    deadline = time.time() + timeout
    while True:
        flow = client._client.get(f"/flow/process-groups/{pg_id}").json()["processGroupFlow"]["flow"]
        procs = flow.get("processors") or []
        invalid = []
        not_ready = []
        for proc in procs:
            comp = proc.get("component", {})
            name = comp.get("name")
            vstat = comp.get("validationStatus")
            if vstat not in {"VALID", "DISABLED"}:
                invalid.append({"name": name, "errors": comp.get("validationErrors") or []})
            s = comp.get("state") or "STOPPED"
            if s not in {"RUNNING", "STOPPED", "DISABLED"}:
                not_ready.append({"name": name, "state": s})
        if not invalid and not not_ready:
            return
        if time.time() > deadline:
            raise TimeoutError(f"Tools PG '{pg_name}' did not become ready", details={"invalid": invalid, "not_ready": not_ready})
        time.sleep(poll)


def _run_once(client, processor_id: str, *, timeout: float = DEFAULT_TIMEOUT) -> None:
    # PUT run-status RUN_ONCE
    entity = client._client.get(f"/processors/{processor_id}").json()
    rev = entity.get("revision", {})
    body = {"revision": rev, "state": "RUN_ONCE"}
    client._client.put(f"/processors/{processor_id}/run-status", json=body).raise_for_status()
    # Wait briefly for completion
    deadline = time.time() + timeout
    while time.time() < deadline:
        ent = client._client.get(f"/processors/{processor_id}").json()
        st = ent.get("component", {}).get("state")
        if st in {"RUNNING", "STOPPED", "DISABLED"}:
            return
        time.sleep(0.2)


def _deploy_and_trigger(config: AppConfig, spec_path: Path, params: Dict[str, str], *, pg_name: str) -> CommandResult:
    with open_client(config) as client:
        purge_adapter.graceful_purge(client)
        deploy_adapter.deploy_flow(client, spec_path, dry_run=False)
        pg_id = _find_pg_by_name(client, pg_name)
        if not pg_id:
            raise BadInputError(f"Process group '{pg_name}' not found after deploy")
        op = pg_name.replace("Tools_Trust_", "").lower()
        ua_name = f"Params ({op})"
        gen_name = f"Trigger ({op})"
        ua = _find_processor_by_name(client, pg_id, ua_name)
        gen = _find_processor_by_name(client, pg_id, gen_name)
        if not ua or not gen:
            raise BadInputError(f"Unable to locate processors '{ua_name}'/'{gen_name}' in tools PG '{pg_name}'")
        _update_processor_properties(client, ua, params)
        _run_once(client, gen)
        # Minimal success response; deeper introspection comes in Phase C
        return CommandResult(message=f"trust op '{pg_name}' triggered", data={"pg": pg_name}, exit_code=ExitCode.SUCCESS)


def _start_root(client) -> None:
    try:
        client.schedule_process_group("root", "RUNNING")
        time.sleep(1.0)
    except Exception:
        pass


def create(*, config: AppConfig) -> CommandResult:
    if not config.ts_name or not config.ts_pass:
        raise BadInputError("--name and --password are required")
    spec = TOOLS_DIR / "trust_create_http.yaml"
    shared_key = secrets.token_urlsafe(24)
    with open_client(config) as client:
        deploy_adapter.deploy_flow(client, spec, dry_run=False)
        # inject shared key
        pg_id = _find_pg_by_name(client, "Tools_Trust_Create_HTTP")
        if pg_id:
            inj = _find_processor_by_name(client, pg_id, "Inject Key")
            if inj:
                _update_processor_properties(client, inj, {"tools.expected.key": shared_key})
        _start_root(client)
        _assert_pg_valid(client, "Tools_Trust_Create_HTTP")
        _wait_pg_ready(client, "Tools_Trust_Create_HTTP")
    params = {"name": config.ts_name, "type": (config.ts_type or "JKS"), "pass": config.ts_pass}
    r = _tools_get("/tools/trust/create", params=params, timeout=10.0, key=shared_key)
    r.raise_for_status()
    # Cleanup ephemeral tools PG
    _delete_tools_pg(config, pg_name="Tools_Trust_Create_HTTP")
    return CommandResult(message=r.text.strip() or "trust create ok", data={"pg": "Tools_Trust_Create_HTTP"})


def add(*, config: AppConfig) -> CommandResult:
    if not config.ts_name or not config.ts_pass or not config.trust_url or not config.ts_alias:
        raise BadInputError("--name, --password, --url and --alias are required")
    spec = TOOLS_DIR / "trust_add_http.yaml"
    shared_key = secrets.token_urlsafe(24)
    with open_client(config) as client:
        deploy_adapter.deploy_flow(client, spec, dry_run=False)
        pg_id = _find_pg_by_name(client, "Tools_Trust_Add_HTTP")
        if pg_id:
            inj = _find_processor_by_name(client, pg_id, "Inject Key")
            if inj:
                _update_processor_properties(client, inj, {"tools.expected.key": shared_key})
        _start_root(client)
        _assert_pg_valid(client, "Tools_Trust_Add_HTTP")
        _wait_pg_ready(client, "Tools_Trust_Add_HTTP")
    params = {
        "name": config.ts_name,
        "type": (config.ts_type or "JKS"),
        "pass": config.ts_pass,
        "url": config.trust_url,
        "alias": config.ts_alias,
    }
    r = _tools_get("/tools/trust/add", params=params, timeout=30.0, key=shared_key)
    status = r.status_code
    details = {"status": status, "body": r.text}
    if status >= 400:
        try:
            _delete_tools_pg(config, pg_name="Tools_Trust_Add_HTTP")
        except Exception:
            pass
        return CommandResult(exit_code=ExitCode.HTTP_ERROR, message="trust add failed", details=details)

    # After importing, ensure a root-level StandardSSLContextService named 'Workflow SSL'
    # points at the created truststore so flows can reference alias 'ssl-context'.
    ts_name = config.ts_name
    ts_type = (config.ts_type or "JKS").upper()
    ts_pass = config.ts_pass
    ext = "jks" if ts_type == "JKS" else ("p12" if ts_type in {"PKCS12", "P12"} else ("bcfks" if ts_type == "BCFKS" else "jks"))
    ts_file = f"/opt/nifi/nifi-current/conf/truststores/{ts_name}.{ext}"
    _ensure_workflow_ssl_context(config, truststore_file=ts_file, truststore_type=ts_type, truststore_pass=ts_pass)
    _delete_tools_pg(config, pg_name="Tools_Trust_Add_HTTP")
    return CommandResult(message="trust add ok", data={}, details=details)


def remove(*, config: AppConfig) -> CommandResult:
    if not config.ts_name or not config.ts_pass or not config.ts_alias:
        raise BadInputError("--name, --password and --alias are required")
    spec = TOOLS_DIR / "trust_remove_http.yaml"
    shared_key = secrets.token_urlsafe(24)
    with open_client(config) as client:
        deploy_adapter.deploy_flow(client, spec, dry_run=False)
        pg_id = _find_pg_by_name(client, "Tools_Trust_Remove_HTTP")
        if pg_id:
            inj = _find_processor_by_name(client, pg_id, "Inject Key")
            if inj:
                _update_processor_properties(client, inj, {"tools.expected.key": shared_key})
        _start_root(client)
        _assert_pg_valid(client, "Tools_Trust_Remove_HTTP")
        _wait_pg_ready(client, "Tools_Trust_Remove_HTTP")
    params = {"name": config.ts_name, "type": (config.ts_type or "JKS"), "pass": config.ts_pass, "alias": config.ts_alias}
    r = _tools_get("/tools/trust/remove", params=params, timeout=10.0, key=shared_key)
    status = r.status_code
    details = {"status": status, "body": r.text}
    if status >= 400:
        try:
            _delete_tools_pg(config, pg_name="Tools_Trust_Remove_HTTP")
        except Exception:
            pass
        return CommandResult(exit_code=ExitCode.HTTP_ERROR, message="trust remove failed", details=details)
    _delete_tools_pg(config, pg_name="Tools_Trust_Remove_HTTP")
    return CommandResult(message="trust remove ok", data={}, details=details)


def inspect(*, config: AppConfig) -> CommandResult:
    if not config.ts_name or not config.ts_pass:
        raise BadInputError("--name and --password are required")
    # Deploy HTTP-triggered inspect flow, then call it and return body
    spec = TOOLS_DIR / "trust_inspect_http.yaml"
    shared_key = secrets.token_urlsafe(24)
    with open_client(config) as client:
        deploy_adapter.deploy_flow(client, spec, dry_run=False)
        pg_id = _find_pg_by_name(client, "Tools_Trust_Inspect_HTTP")
        if pg_id:
            inj = _find_processor_by_name(client, pg_id, "Inject Key")
            if inj:
                _update_processor_properties(client, inj, {"tools.expected.key": shared_key})
        _start_root(client)
        _assert_pg_valid(client, "Tools_Trust_Inspect_HTTP")
        _wait_pg_ready(client, "Tools_Trust_Inspect_HTTP")
    # For now, assume localhost:18081 is reachable from the CLI host
    params = {
        "name": config.ts_name,
        "type": (config.ts_type or "JKS"),
        "pass": config.ts_pass,
    }
    r = _tools_get("/tools/trust/inspect", params=params, timeout=15.0, key=shared_key)
    # Do not raise; return body on error to aid debugging
    # Parse: expect plain text with a listing block followed by '---' then keytool output
    text = r.text or ""
    stores: list[str] = []
    keytool = ""
    if text:
        parts = text.split("---\n", 1)
        head = parts[0]
        keytool = parts[1] if len(parts) > 1 else ""
        lines = [ln.strip() for ln in head.splitlines()]
        # drop header 'TRUSTSTORES:'
        for ln in lines[1:]:
            if ln:
                stores.append(ln)
    try:
        _delete_tools_pg(config, pg_name="Tools_Trust_Inspect_HTTP")
    except Exception:
        pass
    return CommandResult(
        message="trust inspect ok" if r.status_code < 400 else "trust inspect error",
        data={"stores": stores, "keytool": keytool},
        details={"status": r.status_code, "body": text},
        exit_code=ExitCode.SUCCESS if r.status_code < 400 else ExitCode.HTTP_ERROR,
    )


def _delete_tools_pg(config: AppConfig, *, pg_name: str) -> None:
    with open_client(config) as client:
        resp = client._client.get("/flow/process-groups/root")
        resp.raise_for_status()
        flow = resp.json().get("processGroupFlow", {}).get("flow", {})
        for pg in flow.get("processGroups") or []:
            comp = pg.get("component", {})
            if comp.get("name") == pg_name:
                gid = comp.get("id")
                try:
                    client._client.put(f"/flow/process-groups/{gid}", json={"id": gid, "state": "STOPPED"}).raise_for_status()
                except Exception:
                    pass
                ent = client._client.get(f"/process-groups/{gid}").json()
                rev = ent.get("revision", {}).get("version", 0)
                client._client.delete(f"/process-groups/{gid}", params={"version": rev, "clientId": "tools-clean", "recursive": "true"}).raise_for_status()
                break


def _tools_get(path: str, *, params: dict, timeout: float, key: str) -> httpx.Response:
    """Call the ephemeral tools HTTP endpoint trying the preferred tools port, then 18081 as a fallback."""
    ports = [TOOLS_PORT, 18081]
    last_exc: Optional[Exception] = None
    for p in ports:
        url = f"http://127.0.0.1:{p}{path}"
        try:
            return httpx.get(url, params=params, timeout=timeout, headers={"X-Tools-Key": key})
        except Exception as exc:  # pragma: no cover - network
            last_exc = exc
            continue
    if last_exc:
        raise last_exc
    raise RuntimeError("tools_get fell through without response")


def _ensure_workflow_ssl_context(
    config: AppConfig,
    *,
    truststore_file: str,
    truststore_type: str,
    truststore_pass: str,
) -> None:
    """Create or update a root StandardSSLContextService named 'Workflow SSL'."""
    with open_client(config) as client:
        # Find existing service by name
        resp = client._client.get(
            "/flow/process-groups/root/controller-services",
            params={"includeInherited": "false"},
        )
        resp.raise_for_status()
        svc_id: Optional[str] = None
        for svc in resp.json().get("controllerServices") or []:
            comp = svc.get("component", {})
            if comp.get("name") == "Workflow SSL" and comp.get("type") == "org.apache.nifi.ssl.StandardSSLContextService":
                svc_id = comp.get("id")
                break

        props = {
            "Truststore Filename": truststore_file,
            "Truststore Type": truststore_type,
            "Truststore Password": truststore_pass,
        }

        if svc_id:
            # Update properties and enable
            ent = client.get_controller_service(svc_id)
            rev = ent.get("revision", {})
            comp = ent.get("component", {})
            cfg = comp.get("properties", {}) or {}
            cfg.update(props)
            body = {"revision": rev, "component": {"id": svc_id, "name": "Workflow SSL", "properties": cfg}}
            client._client.put(f"/controller-services/{svc_id}", json=body).raise_for_status()
            client.enable_controller_service(svc_id)
        else:
            # Create new service
            created = client.create_controller_service(
                parent_id="root",
                name="Workflow SSL",
                type_name="org.apache.nifi.ssl.StandardSSLContextService",
                properties=props,
            )
            new_id = created.get("id")
            if new_id:
                client.enable_controller_service(new_id)


def create_ssl_context(*, config: AppConfig) -> CommandResult:
    """Create/enable an SSL Context Service named 'SSL TS:<name>' for the given truststore.

    Uses --ts-name (service suffix), --ts-type, --ts-password, and optional --ts-file.
    Default truststore path: /opt/nifi/nifi-current/conf/truststores/<name>.<ext>
    """
    if not config.ts_name or not config.ts_pass:
        raise BadInputError("--ts-name and --ts-password are required")
    ts_type = (config.ts_type or "PKCS12").upper()
    ext = "jks" if ts_type == "JKS" else ("p12" if ts_type in {"PKCS12", "P12"} else ("bcfks" if ts_type == "BCFKS" else "p12"))
    ts_file = config.ts_file or f"/opt/nifi/nifi-current/conf/truststores/{config.ts_name}.{ext}"
    svc_name = f"SSL TS:{config.ts_name}"
    props = {
        "Truststore Filename": ts_file,
        "Truststore Type": ts_type,
        "Truststore Password": config.ts_pass,
    }
    with open_client(config) as client:
        # Find by name
        resp = client._client.get("/flow/process-groups/root/controller-services", params={"includeInherited": "false"})
        resp.raise_for_status()
        svc_id = None
        for svc in resp.json().get("controllerServices") or []:
            comp = svc.get("component", {})
            if comp.get("name") == svc_name and comp.get("type") == "org.apache.nifi.ssl.StandardSSLContextService":
                svc_id = comp.get("id"); break
        if svc_id:
            ent = client.get_controller_service(svc_id)
            rev = ent.get("revision", {})
            cfg = ent.get("component", {}).get("properties", {}) or {}
            cfg.update(props)
            client._client.put(f"/controller-services/{svc_id}", json={"revision": rev, "component": {"id": svc_id, "name": svc_name, "properties": cfg}}).raise_for_status()
            client.enable_controller_service(svc_id)
            return CommandResult(message=f"Updated and enabled {svc_name}")
        created = client.create_controller_service(parent_id="root", name=svc_name, type_name="org.apache.nifi.ssl.StandardSSLContextService", properties=props)
        new_id = created.get("id")
        if new_id:
            client.enable_controller_service(new_id)
        return CommandResult(message=f"Created and enabled {svc_name}")
