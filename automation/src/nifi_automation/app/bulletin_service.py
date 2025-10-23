"""Bulletin inspection service for CLI.

Provides a simple one-shot summary of recent NiFi bulletins so operators can
triage runtime errors without blocking deploys.
"""

from __future__ import annotations

from typing import Dict, List

from .client import open_client
from .models import AppConfig, CommandResult


SEVERITY_ORDER = {"ERROR": 3, "WARN": 2, "WARNING": 2, "INFO": 1}


def _summarize(items: List[Dict[str, object]], min_sev: str) -> Dict[str, object]:
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


def inspect(*, config: AppConfig) -> CommandResult:
    # Defaults: last 200 bulletins, min severity ERROR
    limit = 200
    min_severity = "ERROR"
    with open_client(config) as client:
        payload = client.get_bulletins(limit=limit, after=None)
    summary = _summarize(payload, min_severity)
    return CommandResult(message="Recent bulletins", data=summary)

