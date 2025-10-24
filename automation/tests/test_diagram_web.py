import json
import threading
import time
from pathlib import Path
from importlib.machinery import SourceFileLoader

import httpx
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]


def _start_server(theme="dark"):
    mod = SourceFileLoader("diagram_web", str(ROOT / "automation/scripts/diagram_web.py")).load_module()
    # Ensure base assets exist
    mod.ensure_icons(theme)
    mod.render_diagrams(ROOT / "automation/flows/groups-md/NiFi_Flow_groups.yaml", theme)

    # Bind to an ephemeral port
    from http.server import ThreadingHTTPServer

    httpd = ThreadingHTTPServer(("127.0.0.1", 0), mod.Handler)
    httpd.theme = theme
    httpd.spec = ROOT / "automation/flows/groups-md/NiFi_Flow_groups.yaml"
    t = threading.Thread(target=httpd.serve_forever, daemon=True)
    t.start()
    port = httpd.server_address[1]

    # Wait for server
    base = f"http://127.0.0.1:{port}"
    deadline = time.time() + 5
    while time.time() < deadline:
        try:
            r = httpx.get(base + "/health", timeout=1)
            if r.status_code == 200:
                break
        except Exception:
            time.sleep(0.05)
    else:
        raise RuntimeError("server failed to start")

    return httpd, t, base


def _stop_server(httpd, t):
    httpd.shutdown()
    t.join(timeout=2)
    httpd.server_close()


def test_server_endpoints_smoke():
    httpd, t, base = _start_server("dark")
    try:
        # UI shell
        r = httpx.get(base + "/", timeout=2)
        assert r.status_code == 200
        assert "Flow Diagrams" in r.text

        # Diagrams index
        r = httpx.get(base + "/diagrams/index.html", timeout=2)
        assert r.status_code == 200
        assert "Flow Diagram Index" in r.text

        # Assets manifest
        r = httpx.get(base + "/assets/svg/dark/manifest.json", timeout=2)
        assert r.status_code == 200
        m = r.json()
        assert "icons" in m

        # Favicon
        r = httpx.get(base + "/favicon.ico", timeout=2)
        assert r.status_code == 200
        assert r.headers.get("content-type", "").startswith("image/png")

        # Preview page
        r = httpx.get(base + "/assets/preview/index.html", timeout=2)
        assert r.status_code == 200
        assert "Processor Icon Preview" in r.text

        # Re-render with light theme and ensure index reflects it
        r = httpx.get(base + "/api/render?theme=light", timeout=5)
        assert r.status_code == 200 and r.json().get("ok")
        r = httpx.get(base + "/diagrams/index.html", timeout=2)
        assert "Flow Diagram Index (light)" in r.text

        # Direct icon fetch (legacy path without theme) should resolve and be valid XML
        r = httpx.get(base + "/assets/svg/RouteOnAttribute.svg", timeout=2)
        assert r.status_code == 200
        ET.fromstring(r.text)

        # Parent page should include clickable link to child process group
        r = httpx.get(base + "/diagrams/NiFi_Flow_BigWorkflow.html", timeout=2)
        assert r.status_code == 200
        assert "NiFi_Flow_BigWorkflow_TransformGroup.html" in r.text
        # Child page has breadcrumb back to parent
        r = httpx.get(base + "/diagrams/NiFi_Flow_BigWorkflow_TransformGroup.html", timeout=2)
        assert r.status_code == 200
        assert "href='NiFi_Flow_BigWorkflow.html'" in r.text
    finally:
        _stop_server(httpd, t)
