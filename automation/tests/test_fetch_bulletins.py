from __future__ import annotations

import importlib.util
import types
from pathlib import Path


def _load_script_module() -> types.ModuleType:
    script_path = Path(__file__).resolve().parents[1] / "scripts" / "fetch_bulletins.py"
    spec = importlib.util.spec_from_file_location("fetch_bulletins", str(script_path))
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # type: ignore[arg-type]
    return mod


def test_fetch_bulletins_and_summarize(monkeypatch):
    fb = _load_script_module()

    # Stub settings and token
    class _S:
        base_url = "https://example.test/nifi-api"
        verify_ssl = False
        timeout = 5.0

    monkeypatch.setattr(fb, "build_settings", lambda *a, **k: _S)
    monkeypatch.setattr(fb, "obtain_access_token", lambda s: "tok")

    # Fake httpx client
    class FakeResp:
        def raise_for_status(self):
            return None

        def json(self):
            return {
                "bulletinBoard": {
                    "bulletins": [
                        {
                            "id": 100,
                            "bulletin": {
                                "level": "ERROR",
                                "groupId": "g1",
                                "sourceId": "p1",
                                "sourceName": "InvokeHTTP (demo)",
                                "message": "Connection refused",
                                "timestamp": "now",
                            },
                        },
                        {
                            "id": 90,
                            "bulletin": {
                                "level": "INFO",
                                "groupId": "g2",
                                "sourceId": "p2",
                                "sourceName": "Other",
                                "message": "ok",
                                "timestamp": "now",
                            },
                        },
                    ]
                }
            }

    class FakeClient:
        def __init__(self, *a, **k):
            pass

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def get(self, path, params=None):
            assert path == "/flow/bulletin-board"
            return FakeResp()

    fake_httpx = types.SimpleNamespace(Client=FakeClient, HTTPError=Exception)
    monkeypatch.setattr(fb, "httpx", fake_httpx)

    items = fb.fetch_bulletins(limit=50, after=None)
    assert isinstance(items, list) and len(items) == 2

    summary = fb.summarize(items, min_sev="ERROR")
    assert summary["total"] == 1  # only ERROR retained
    assert summary["by_level"].get("ERROR") == 1
    assert summary["last_id"] == 100
    assert summary["top_components"][0][0] == "InvokeHTTP (demo)"
