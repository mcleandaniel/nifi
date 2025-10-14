"""Generate candidate processor and controller service lists from the NiFi source tree."""

from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import Iterable

PROJECT_ROOT = Path(__file__).resolve().parents[2]
PROCESSOR_PATTERN = [
    re.compile(r"class\s+(\w+)\s+extends\s+Abstract\w*Processor"),
    re.compile(r"class\s+(\w+)\s+implements\s+Processor"),
]
CONTROLLER_PATTERN = [
    re.compile(r"class\s+(\w+)\s+extends\s+Abstract\w*ControllerService"),
    re.compile(r"class\s+(\w+)\s+implements\s+ControllerService"),
]
SKIP_TOKENS = ("Test", "Mock", "Fake", "Stub")
CAPABILITY_RE = re.compile(r"@CapabilityDescription\(\"([^\"]+)\"\)")
TAGS_RE = re.compile(r"@Tags\(\s*\{([^}]*)\}", re.DOTALL)


def collect_types(patterns: Iterable[re.Pattern[str]], include_keyword: str) -> list[tuple[str, Path]]:
    candidates: dict[str, Path] = {}
    for java_file in PROJECT_ROOT.rglob("src/main/java/**/*.java"):
        parts = {part.lower() for part in java_file.parts}
        if "target" in parts or "test" in parts:
            continue
        if any(token in java_file.name for token in SKIP_TOKENS):
            continue
        try:
            text = java_file.read_text(encoding="utf-8")
        except Exception:
            continue
        if not any(p.search(text) for p in patterns):
            continue
        pkg = None
        for line in text.splitlines():
            if line.startswith("package "):
                pkg = line[len("package ") :].rstrip(";")
                break
        if not pkg or include_keyword not in pkg:
            continue
        class_match = re.search(r"class\s+(\w+)", text)
        if not class_match:
            continue
        name = class_match.group(1)
        fqcn = f"{pkg}.{name}"
        candidates[fqcn] = java_file
    return [(fqcn, candidates[fqcn]) for fqcn in sorted(candidates)]


def extract_metadata(java_path: Path) -> dict[str, str]:
    data = {
        "properties": "",
        "relationships": "",
        "annotations": "",
        "source": str(java_path.relative_to(PROJECT_ROOT)),
        "description": "",
    }
    try:
        text = java_path.read_text(encoding="utf-8")
    except Exception:
        return data

    normalized = re.sub(r'"\s*\+\s*"', '', text)
    desc_match = CAPABILITY_RE.search(normalized)
    if desc_match:
        data["description"] = desc_match.group(1)

    prop_total = normalized.count("PropertyDescriptor.Builder")
    required_count = len(re.findall(r"\.required\(\s*true\s*\)", normalized))
    if prop_total:
        data["properties"] = f"{prop_total} (required {required_count})"

    rel_names = re.findall(r"\.name\(\s*\"([^\"]+)\"\s*\)", normalized)
    if rel_names:
        data["relationships"] = ", ".join(sorted(set(rel_names)))

    annotations = []
    tags_match = TAGS_RE.search(normalized)
    if tags_match:
        tags = [t.strip().strip('"') for t in tags_match.group(1).split(',') if t.strip()]
        if tags:
            annotations.append(f"Tags: {', '.join(tags)}")
    for marker, label in [
        ("@Restricted", "Restricted"),
        ("@Stateful", "Stateful"),
        ("@WritesAttributes", "WritesAttributes"),
        ("@ReadsAttributes", "ReadsAttributes"),
    ]:
        if marker in normalized:
            annotations.append(label)
    if annotations:
        data["annotations"] = "; ".join(annotations)

    return data


def write_table(path: Path, header: str, items: list[tuple[str, Path]]) -> None:
    path.write_text(header, encoding="utf-8")
    with path.open("a", encoding="utf-8") as f:
        for fqcn, java_path in items:
            meta = extract_metadata(java_path)
            f.write(
                "| `{}` | {} | {} | {} | {} | {} |\n".format(
                    fqcn,
                    meta.get("properties", ""),
                    meta.get("relationships", ""),
                    meta.get("annotations", ""),
                    meta.get("source", ""),
                    meta.get("description", ""),
                )
            )
        f.write("\n> Auto-generated from NiFi source; update scripts as needed.\n")


def main(args: argparse.Namespace) -> None:
    processors = collect_types(PROCESSOR_PATTERN, "processor")
    controllers = collect_types(CONTROLLER_PATTERN, "controller")

    docs_dir = PROJECT_ROOT / "docs" / "components"
    write_table(
        docs_dir / "processors-candidate.md",
        "# Candidate Processors (from NiFi source)\n\n| Type | Properties | Relationships | Annotations | Source | Description |\n|------|-----------|---------------|------------|--------|-------------|\n",
        processors,
    )
    write_table(
        docs_dir / "controller-services-candidate.md",
        "# Candidate Controller Services\n\n| Type | Properties | Relationships | Annotations | Source | Description |\n|------|-----------|---------------|------------|--------|-------------|\n",
        controllers,
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate candidate component lists")
    main(parser.parse_args())
