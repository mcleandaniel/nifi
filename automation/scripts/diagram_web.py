#!/usr/bin/env python3
"""
A tiny web server to browse flow diagrams and icon assets.

Features
- Serves files under automation/diagrams/out (generated HTML pages).
- Serves icon assets under automation/assets/processor-icons/ (both themes).
- Endpoint /api/render?theme=dark|light&spec=PATH regenerates diagrams on demand.

Usage
  source automation/.venv/bin/activate
  python automation/scripts/diagram_web.py --spec automation/flows/NiFi_Flow.yaml --theme dark --port 8089

Notes
- Requires PyYAML (already in automation/pyproject.toml dependencies).
"""
from __future__ import annotations

import argparse
import io
import json
import mimetypes
import os
import sys
from http import HTTPStatus
import base64
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlparse, parse_qs, unquote
import subprocess

ROOT = Path(__file__).resolve().parents[2]
DIAGRAM_OUT = ROOT / "automation" / "diagrams" / "out"
ASSETS_ROOT = ROOT / "automation" / "assets" / "processor-icons"
SCRIPTS_ROOT = ROOT / "automation" / "scripts"


def ensure_icons(theme: str) -> None:
    manifest = ASSETS_ROOT / "svg" / theme / "manifest.json"
    if not manifest.exists():
        subprocess.check_call([sys.executable, str(SCRIPTS_ROOT / "generate_processor_icons.py"), "--theme", theme])


def render_diagrams(spec: Path, theme: str) -> None:
    DIAGRAM_OUT.mkdir(parents=True, exist_ok=True)
    subprocess.check_call([sys.executable, str(SCRIPTS_ROOT / "render_flow_diagram.py"), "--theme", theme, str(spec)])


class Handler(BaseHTTPRequestHandler):
    server_version = "DiagramServer/0.1"

    def _send_bytes(self, data: bytes, ctype: str = "text/plain; charset=utf-8", code: int = 200) -> None:
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _send_file(self, path: Path) -> None:
        if not path.exists() or not path.is_file():
            self._send_bytes(b"Not Found", "text/plain; charset=utf-8", 404)
            return
        ctype = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
        data = path.read_bytes()
        self._send_bytes(data, ctype)

    def do_GET(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        qp = parse_qs(parsed.query)
        theme = qp.get("theme", [self.server.theme])[0]  # type: ignore[attr-defined]
        # Tiny in-memory favicon to avoid 404s (1x1 transparent PNG)
        if parsed.path == "/favicon.ico":
            png_b64 = (
                "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVQImWNgYGAAAAAEAAGjCh0WAAAAAElFTkSuQmCC"
            )
            data = base64.b64decode(png_b64)
            return self._send_bytes(data, "image/png")
        # Root UI (with theme toggle + regenerate)
        if parsed.path in {"/", "/index.html", "/ui"}:
            index = DIAGRAM_OUT / "index.html"
            if not index.exists():
                try:
                    ensure_icons(theme)
                    render_diagrams(self.server.spec, theme)  # type: ignore[attr-defined]
                except Exception as e:  # pragma: no cover - best effort
                    msg = f"Render failed: {e}".encode()
                    self._send_bytes(msg, "text/plain; charset=utf-8", 500)
                    return
            # Return the UI shell that embeds the generated index in an iframe.
            page = f"""
<!doctype html>
<html lang='en'>
  <meta charset='utf-8'>
  <meta name='viewport' content='width=device-width, initial-scale=1'>
  <title>Flow Diagrams</title>
  <style>
    body {{ background:{'#0b0c10' if theme=='dark' else '#f7fafc'}; color:{'#e6e6e6' if theme=='dark' else '#111827'}; font: 14px system-ui, -apple-system, Segoe UI, Roboto; margin:0; }}
    header {{ display:flex; gap:12px; align-items:center; padding:12px 16px; border-bottom:1px solid {('#1a1b20' if theme=='dark' else '#e5e7eb')}; }}
    select, button {{ font:inherit; padding:4px 8px; }}
    #status {{ margin-left:auto; opacity:0.85; }}
    iframe {{ border:0; width:100vw; height: calc(100vh - 54px); display:block; }}
    a {{ color: inherit; }}
  </style>
  <header>
    <strong>Flow Diagrams</strong>
    <label for="theme">Theme:</label>
    <select id="theme">
      <option value="dark" {('selected' if theme=='dark' else '')}>dark</option>
      <option value="light" {('selected' if theme=='light' else '')}>light</option>
    </select>
    <button id="regen">Regenerate</button>
    <a href="/assets/preview/index.html" target="_blank" rel="noreferrer noopener">Icons Preview</a>
    <span id="status"></span>
  </header>
  <iframe id="frame" src="/diagrams/index.html?ts=0" referrerpolicy="no-referrer"></iframe>
  <script>
    const sel = document.getElementById('theme');
    const btn = document.getElementById('regen');
    const st = document.getElementById('status');
    const frame = document.getElementById('frame');
    function refreshFrame() {{ frame.src = '/diagrams/index.html?ts=' + Date.now(); }}
    btn.onclick = async () => {{
      btn.disabled = true; st.textContent = 'Rendering…';
      const theme = sel.value;
      try {{
        const res = await fetch('/api/render?theme=' + encodeURIComponent(theme));
        const j = await res.json();
        if (!j.ok) throw new Error(j.error || 'render failed');
        st.textContent = 'Done (' + theme + ')';
        refreshFrame();
      }} catch (e) {{
        st.textContent = 'Error: ' + e;
      }} finally {{ btn.disabled = false; }}
    }}
    // Auto-regenerate when theme changes
    sel.onchange = () => btn.click();
    // initial load ensures diagrams reflect current theme
    refreshFrame();
  </script>
  </body>
 </html>
"""
            return self._send_bytes(page.encode("utf-8"), "text/html; charset=utf-8")

        if parsed.path.startswith("/diagrams/"):
            # strip prefix and map under DIAGRAM_OUT
            rel = unquote(parsed.path[len("/diagrams/"):])
            return self._send_file(DIAGRAM_OUT / rel)

        if parsed.path.startswith("/assets/"):
            rel = unquote(parsed.path[len("/assets/"):])
            # Back-compat: allow /assets/processor-icons/* even though ASSETS_ROOT already points to that root
            if rel.startswith("processor-icons/"):
                rel = rel[len("processor-icons/"):]
            # Convenience: if requesting /assets/svg/<name>.svg without theme, serve themed file
            if rel.startswith("svg/"):
                parts = rel.split("/")
                if len(parts) == 2 and parts[1].lower().endswith('.svg'):
                    themed = ASSETS_ROOT / 'svg' / theme / parts[1]
                    if themed.exists():
                        return self._send_file(themed)
            return self._send_file(ASSETS_ROOT / rel)

        if parsed.path == "/api/render":
            spec = qp.get("spec", [str(self.server.spec)])[0]  # type: ignore[attr-defined]
            theme = qp.get("theme", [self.server.theme])[0]  # type: ignore[attr-defined]
            try:
                ensure_icons(theme)
                render_diagrams(Path(spec), theme)
                body = json.dumps({"ok": True, "theme": theme}).encode()
                return self._send_bytes(body, "application/json")
            except subprocess.CalledProcessError as e:  # pragma: no cover
                body = json.dumps({"ok": False, "error": str(e)}).encode()
                return self._send_bytes(body, "application/json", 500)

        if parsed.path == "/health":
            return self._send_bytes(json.dumps({"ok": True}).encode(), "application/json")

        # Fallback 404
        self._send_bytes(b"Not Found", "text/plain; charset=utf-8", 404)


def main() -> None:  # pragma: no cover - server entry point
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=8089)
    ap.add_argument("--spec", default=str(ROOT / "automation" / "flows" / "NiFi_Flow.yaml"))
    ap.add_argument("--theme", choices=["dark", "light"], default="dark")
    args = ap.parse_args()

    # Initial generation (best effort)
    try:
        ensure_icons(args.theme)
        render_diagrams(Path(args.spec), args.theme)
    except Exception:
        pass

    class S(ThreadingHTTPServer):
        # attach config to server instance
        theme = args.theme
        spec = Path(args.spec)

    httpd = S((args.host, args.port), Handler)
    print(f"Serving diagrams on http://{args.host}:{args.port} (theme={args.theme})")
    print("  - /            -> index (diagrams/out/index.html)")
    print("  - /diagrams/*  -> files under automation/diagrams/out/")
    print("  - /assets/*    -> files under automation/assets/processor-icons/")
    print("  - /api/render?theme=dark|light[&spec=...] -> regenerate")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down...")
        httpd.server_close()


if __name__ == "__main__":
    main()
