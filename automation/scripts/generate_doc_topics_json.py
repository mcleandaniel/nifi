#!/usr/bin/env python3
"""Convert the documentation topics table into a structured JSON manifest."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_INPUT = PROJECT_ROOT / "kb" / "documentation-topics-text.md"
DEFAULT_OUTPUT = PROJECT_ROOT / "kb" / "documentation-topics.json"


GROUP_PATTERN = re.compile(r"\d+\.\s+\*\*(.+?):\*\*\s*(.+)")


def _slugify(value: str) -> str:
    normalized = value.lower()
    normalized = re.sub(r"[^\w\s-]+", "", normalized)
    normalized = re.sub(r"[\s]+", "-", normalized)
    return normalized.strip("-")


def parse_group_tags(markdown: str) -> dict[str, list[str]]:
    """Extract group assignments from the numbered list at the end of the file."""
    mapping: dict[str, list[str]] = {}
    for match in GROUP_PATTERN.finditer(markdown):
        group_label = match.group(1).strip().rstrip(":")
        tag = _slugify(group_label)
        candidates = match.group(2)
        for raw_id in candidates.split(","):
            topic_id = raw_id.strip().strip(".")
            if not topic_id:
                continue
            mapping.setdefault(topic_id, []).append(tag)
    return mapping


def parse_table(markdown: str) -> list[dict[str, Any]]:
    """Parse the Markdown table into topic dictionaries without enrichment."""
    lines = [
        line
        for line in markdown.splitlines()
        if line.strip().startswith("|") and not line.strip().startswith("|----")
    ]
    if not lines:
        return []

    header_cells = [
        cell.strip()
        for cell in lines[0].strip("|").split("|")
    ]
    columns = [col.lower() for col in header_cells]
    topics: list[dict[str, Any]] = []
    for line in lines[1:]:
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) != len(columns):
            continue
        record = dict(zip(columns, cells))
        topic_id = record.get("id")
        if not topic_id or topic_id == "id":
            continue
        sources = [
            src.strip()
            for src in re.split(r"<br>|\\n", record.get("recommended sources", ""))
            if src.strip()
        ]
        dependencies = [
            dep.strip()
            for dep in record.get("dependencies", "")
            .replace("—", "")
            .replace("–", "")
            .split(",")
            if dep.strip()
        ]
        topics.append(
            {
                "id": topic_id,
                "title": record.get("title", ""),
                "summary": record.get("summary", ""),
                "recommended_sources": sources,
                "dependencies": dependencies,
            }
        )
    return topics


def build_topics(
    parsed_topics: list[dict[str, Any]],
    existing: dict[str, dict[str, Any]],
    group_tags: dict[str, list[str]],
) -> list[dict[str, Any]]:
    """Merge parsed topics with any existing metadata."""
    results: list[dict[str, Any]] = []
    for topic in parsed_topics:
        original = existing.get(topic["id"], {})
        tags = original.get("tags") or group_tags.get(topic["id"], [])
        priority = original.get("priority", "medium")
        research_request = original.get("research_request")
        if not research_request:
            research_request = (
                f"Develop a comprehensive document on {topic['title']} that expands on the focus: "
                f"{topic['summary']}"
            )
        results.append(
            {
                **topic,
                "priority": priority,
                "tags": tags,
                "research_request": research_request,
            }
        )
    return results


def load_existing(path: Path) -> dict[str, dict[str, Any]]:
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return {topic["id"]: topic for topic in data.get("topics", []) if "id" in topic}


def generate_manifest(
    input_path: Path,
    output_path: Path,
    version: str,
    repo_root: str,
) -> None:
    markdown = input_path.read_text(encoding="utf-8")
    parsed_topics = parse_table(markdown)
    group_tags = parse_group_tags(markdown)
    existing = load_existing(output_path)
    topics = build_topics(parsed_topics, existing, group_tags)
    manifest = {
        "version": version,
        "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "repo_root": repo_root,
        "topics": topics,
    }
    output_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate documentation topics JSON manifest.")
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT, help="Path to Markdown source.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="Destination JSON path.")
    parser.add_argument("--version", default="1", help="Manifest version marker.")
    parser.add_argument("--repo-root", default=".", help="Repository root recorded in the manifest.")
    args = parser.parse_args()
    generate_manifest(args.input, args.output, args.version, args.repo_root)


if __name__ == "__main__":
    main()
