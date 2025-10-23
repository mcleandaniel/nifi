#!/usr/bin/env python3
"""Fetch recent NiFi bulletins and print a summary + items as JSON.

Reads defaults from .env (NIFI_BASE_URL, NIFI_USERNAME, NIFI_PASSWORD).

Usage examples:
  python automation/scripts/fetch_bulletins.py --limit 200 --severity ERROR --output json
  python automation/scripts/fetch_bulletins.py --after 12345 --output json
"""

from __future__ import annotations

import argparse
import json
from typing import Dict, List

import httpx

from nifi_automation.config import build_settings
from nifi_automation.auth import obtain_access_token, AuthenticationError


SEVERITY_ORDER = {"ERROR": 3, "WARN": 2, "WARNING": 2, "INFO": 1}


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Fetch recent NiFi bulletins")
    ap.add_argument("--limit", type=int, default=200, help="Max bulletins to fetch (default: 200)")
    ap.add_argument("--after", type=int, default=None, help="Return bulletins with id greater than this value")
    ap.add_argument(
        "--severity",
        default="ERROR",
        choices=["ERROR", "WARN", "INFO"],
        help="Minimum severity to include",
    )
    ap.add_argument("--output", default="json", choices=["json", "text"], help="Output format")
    return ap.parse_args()


def fetch_bulletins(limit: int, after: int | None) -> List[Dict[str, object]]:
    # Use verify_ssl=False by default for dev/self-signed environments
    settings = build_settings(None, None, None, verify_ssl=False, timeout=10.0)
    token = obtain_access_token(settings)
    headers = {"Authorization": f"Bearer {token}"}
    params = {"limit": str(limit)}
    if after is not None:
        params["after"] = str(after)
    with httpx.Client(base_url=str(settings.base_url), verify=settings.verify_ssl, timeout=settings.timeout, headers=headers) as client:
        resp = client.get("/flow/bulletin-board", params=params)
        resp.raise_for_status()
        data = resp.json() or {}
        items = data.get("bulletinBoard", {}).get("bulletins", []) or []
        rows: List[Dict[str, object]] = []
        for it in items:
            b = it.get("bulletin", {})
            rows.append(
                {
                    "id": it.get("id"),
                    "level": b.get("level"),
                    "groupId": b.get("groupId"),
                    "sourceId": b.get("sourceId"),
                    "sourceName": b.get("sourceName"),
                    "message": b.get("message"),
                    "timestamp": b.get("timestamp"),
                }
            )
        return rows


def summarize(items: List[Dict[str, object]], min_sev: str) -> Dict[str, object]:
    min_score = SEVERITY_ORDER.get(min_sev, 1)
    filtered = [it for it in items if SEVERITY_ORDER.get(str(it.get("level", "INFO")), 1) >= min_score]
    counts: Dict[str, int] = {}
    by_component: Dict[str, int] = {}
    last_id = 0
    for it in filtered:
        lvl = str(it.get("level"))
        counts[lvl] = counts.get(lvl, 0) + 1
        name = f"{it.get('sourceName') or ''}".strip()
        by_component[name] = by_component.get(name, 0) + 1
        try:
            last_id = max(last_id, int(it.get("id", 0)))
        except Exception:
            pass
    top_components = sorted(by_component.items(), key=lambda kv: kv[1], reverse=True)[:10]
    return {
        "total": len(filtered),
        "by_level": counts,
        "top_components": top_components,
        "last_id": last_id,
        "items": filtered,
    }


def main() -> int:
    args = parse_args()
    try:
        items = fetch_bulletins(args.limit, args.after)
    except AuthenticationError as exc:
        print(json.dumps({"error": str(exc)}))
        return 3
    except httpx.HTTPError as exc:
        print(json.dumps({"error": str(exc)}))
        return 3
    payload = summarize(items, args.severity)
    if args.output == "json":
        print(json.dumps(payload))
    else:
        by_level = ", ".join(f"{k}:{v}" for k, v in payload["by_level"].items())
        print(f"bulletins total={payload['total']} by_level=({by_level}) last_id={payload['last_id']}")
        for name, cnt in payload["top_components"]:
            print(f"  {cnt} - {name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
