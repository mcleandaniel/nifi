#!/usr/bin/env python3
"""
Generate SVG icons for NiFi processors using a small glyph library and a color‑coded
category system. Outputs to automation/assets/processor-icons/svg/.

No external deps; reads YAML via PyYAML if available, else simple hand parser fallback.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import argparse
from typing import Dict, Any

try:
    import yaml  # type: ignore
except Exception:
    yaml = None

ROOT = Path(__file__).resolve().parents[2]
ICON_DIR = ROOT / "automation" / "assets" / "processor-icons"
SVG_BASE = ICON_DIR / "svg"
CONFIG = ICON_DIR / "icons.yml"

COLORS: Dict[str, str] = {
    "source": "#2ecc71",
    "sink": "#9b59b6",
    "transform": "#3498db",
    "route": "#e67e22",
    "utility": "#95a5a6",
    "network": "#1abc9c",
    "messaging": "#e91e63",
    "storage": "#8e6b3a",
    "compute": "#f1c40f",
}

def load_config(path: Path) -> Dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    if yaml is not None:
        return yaml.safe_load(text)
    # Tiny fallback parser for our simple structure
    data: Dict[str, Any] = {"processors": []}
    cur: Dict[str, str] | None = None
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("- name:"):
            if cur:
                data["processors"].append(cur)
            cur = {"name": line.split(":", 1)[1].strip()}
        elif cur and ":" in line:
            k, v = [p.strip() for p in line.split(":", 1)]
            cur[k] = v
    if cur:
        data["processors"].append(cur)
    return data


def svg_header(fg: str) -> str:
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" width="96" height="96" viewBox="0 0 96 96"'
        ' shape-rendering="geometricPrecision" text-rendering="optimizeLegibility"'
        ' stroke-linecap="round" stroke-linejoin="round">\n'
        '<defs>\n'
        '  <marker id="arrow" markerWidth="8" markerHeight="8" refX="4" refY="4" orient="auto-start-reverse">\n'
        f'    <path d="M0,0 L8,4 L0,8 z" fill="{fg}"/>\n'
        '  </marker>\n'
        '</defs>\n'
    )


def svg_base(color: str, card: str, border: str) -> str:
    return (
        # card
        f'<rect x=\"6\" y=\"6\" width=\"84\" height=\"84\" rx=\"12\" fill=\"{card}\" stroke=\"{border}\" stroke-width=\"1\"/>\n'
        f'<rect x=\"6\" y=\"6\" width=\"84\" height=\"16\" rx=\"12\" fill=\"{color}\"/>\n'
    )


def stroke(fg: str, style: str = "") -> str:
    # Normalize any extra attributes (e.g., marker-end=url(#arrow)) to include quoted values.
    extra = ""
    if style:
        parts = []
        for tok in style.strip().split():
            if "=" in tok:
                k, v = tok.split("=", 1)
                if not (v.startswith('"') or v.startswith("'")):
                    v = f'"{v}"'
                parts.append(f"{k}={v}")
            else:
                parts.append(tok)
        extra = " " + " ".join(parts)
    return f'stroke=\"{fg}\" stroke-width=\"2.5\" fill=\"none\"{extra}'


# --- Glyphs ---
def g_bolt(fg: str) -> str:
    return (
        f'<polygon points=\"46,26 36,52 48,52 42,70 60,44 48,44\" fill=\"{fg}\" stroke=\"{fg}\"/>\n'
    )


def g_gear(fg: str) -> str:
    parts = [
        f'<circle cx=\"48\" cy=\"52\" r=\"12\" {stroke(fg)} />',
        # six teeth
        *[
            f'<rect x=\"46\" y=\"30\" width=\"4\" height=\"8\" rx=\"1\" fill=\"{fg}\" transform=\"rotate({deg},48,52) translate(0,-22)\"/>'
            for deg in (0, 60, 120, 180, 240, 300)
        ],
        f'<circle cx=\"48\" cy=\"52\" r=\"3\" fill=\"{fg}\" />',
    ]
    return "\n".join(parts) + "\n"


def g_split_route(fg: str) -> str:
    return (
        f'<path d=\"M30,64 C48,64 56,48 66,36\" {stroke(fg)} />\n'
        f'<path d=\"M30,40 C44,40 50,46 56,52\" {stroke(fg)} />\n'
        f'<path d=\"M66,36 L70,32\" {stroke(fg, "marker-end=url(#arrow)")} />\n'
        f'<path d=\"M56,52 L60,48\" {stroke(fg, "marker-end=url(#arrow)")} />\n'
    )


def g_log(fg: str) -> str:
    return (
        f'<rect x=\"28\" y=\"34\" width=\"40\" height=\"36\" rx=\"4\" {stroke(fg)} />\n'
        f'<path d=\"M32,42 H64\" {stroke(fg)} />\n'
        f'<path d=\"M32,50 H60\" {stroke(fg)} />\n'
        f'<path d=\"M32,58 H52\" {stroke(fg)} />\n'
    )


def g_replace(fg: str) -> str:
    return (
        f'<path d=\"M28,48 H56\" {stroke(fg, "marker-end=url(#arrow)")} />\n'
        f'<path d=\"M68,58 H40\" {stroke(fg, "marker-end=url(#arrow)")} />\n'
        f'<rect x=\"24\" y=\"40\" width=\"12\" height=\"16\" rx=\"2\" {stroke(fg)} />\n'
        f'<rect x=\"60\" y=\"52\" width=\"12\" height=\"16\" rx=\"2\" {stroke(fg)} />\n'
    )


def g_search(fg: str) -> str:
    return (
        f'<circle cx=\"44\" cy=\"50\" r=\"10\" {stroke(fg)} />\n'
        f'<line x1=\"50\" y1=\"56\" x2=\"62\" y2=\"66\" {stroke(fg)} />\n'
    )


def g_merge(fg: str) -> str:
    return (
        f'<path d=\"M30,40 C42,48 42,56 42,64\" {stroke(fg)} />\n'
        f'<path d=\"M60,40 C48,48 48,56 48,64\" {stroke(fg)} />\n'
        f'<path d=\"M45,64 H66\" {stroke(fg, "marker-end=url(#arrow)")} />\n'
    )


def g_split(fg: str) -> str:
    return (
        f'<path d=\"M48,36 V56\" {stroke(fg)} />\n'
        f'<path d=\"M48,56 C60,58 64,60 66,66\" {stroke(fg, "marker-end=url(#arrow)")} />\n'
        f'<path d=\"M48,56 C36,58 32,60 30,66\" {stroke(fg, "marker-end=url(#arrow)")} />\n'
    )


def g_jsonpath(fg: str) -> str:
    return (
        f'<path d=\"M30,44 C26,44 26,36 30,36 H34 C30,36 30,44 34,44 30,44 30,52 34,52 H30 C26,52 26,44 30,44\" {stroke(fg)} />\n'
        f'<circle cx=\"58\" cy=\"44\" r=\"6\" {stroke(fg)} />\n'
        f'<path d=\"M64,50 L72,58\" {stroke(fg)} />\n'
        f'<circle cx=\"72\" cy=\"58\" r=\"2.5\" fill=\"{fg}\" />\n'
    )


def g_json(fg: str) -> str:
    return (
        f'<path d=\"M32,44 C28,44 28,36 32,36 H36 C32,36 32,44 36,44 32,44 32,52 36,52 H32 C28,52 28,44 32,44\" {stroke(fg)} />\n'
        f'<path d=\"M60,44 C64,44 64,36 60,36 H56 C60,36 60,44 56,44 60,44 60,52 56,52 H60 C64,52 64,44 60,44\" {stroke(fg)} />\n'
    )


def g_convert(fg: str) -> str:
    return (
        f'<rect x=\"22\" y=\"36\" width=\"20\" height=\"26\" rx=\"3\" {stroke(fg)} />\n'
        f'<rect x=\"54\" y=\"42\" width=\"20\" height=\"26\" rx=\"3\" {stroke(fg)} />\n'
        f'<path d=\"M44,44 H54\" {stroke(fg, "marker-end=url(#arrow)")} />\n'
    )


def g_query(fg: str) -> str:
    return (
        f'<ellipse cx=\"44\" cy=\"48\" rx=\"14\" ry=\"6\" {stroke(fg)} />\n'
        f'<path d=\"M30,48 V58 C30,62 58,62 58,58 V48\" {stroke(fg)} />\n'
        f'<circle cx=\"60\" cy=\"60\" r=\"6\" {stroke(fg)} />\n'
        f'<line x1=\"64\" y1=\"64\" x2=\"72\" y2=\"72\" {stroke(fg)} />\n'
    )


def g_merge_record(fg: str) -> str:
    return (
        f'<rect x=\"24\" y=\"36\" width=\"16\" height=\"12\" rx=\"2\" {stroke(fg)} />\n'
        f'<rect x=\"56\" y=\"36\" width=\"16\" height=\"12\" rx=\"2\" {stroke(fg)} />\n'
        f'<path d=\"M32,48 C40,54 44,58 44,64\" {stroke(fg)} />\n'
        f'<path d=\"M64,48 C56,54 52,58 52,64\" {stroke(fg)} />\n'
        f'<path d=\"M46,64 H58\" {stroke(fg, "marker-end=url(#arrow)")} />\n'
    )


def g_http(fg: str) -> str:
    return (
        f'<circle cx=\"48\" cy=\"52\" r=\"12\" {stroke(fg)} />\n'
        f'<path d=\"M36,52 H60\" {stroke(fg)} />\n'
        f'<path d=\"M48,40 V64\" {stroke(fg)} />\n'
        f'<path d=\"M40,46 C44,48 52,48 56,46\" {stroke(fg)} />\n'
    )


def g_http_in(fg: str) -> str:
    return g_http(fg) + f"<path d=\"M24,52 H40\" {stroke(fg, 'marker-end=url(#arrow)')} />\n"


def g_http_out(fg: str) -> str:
    return g_http(fg) + f"<path d=\"M56,52 H72\" {stroke(fg, 'marker-end=url(#arrow)')} />\n"


def g_queue_out(fg: str) -> str:
    return (
        f'<circle cx=\"36\" cy=\"48\" r=\"3\" fill=\"{fg}\" />\n'
        f'<circle cx=\"44\" cy=\"52\" r=\"3\" fill=\"{fg}\" />\n'
        f'<circle cx=\"52\" cy=\"56\" r=\"3\" fill=\"{fg}\" />\n'
        f'<path d=\"M56,56 H70\" {stroke(fg, "marker-end=url(#arrow)")} />\n'
    )


def g_queue_in(fg: str) -> str:
    return (
        f'<path d=\"M26,56 H40\" {stroke(fg, "marker-end=url(#arrow)")} />\n'
        f'<circle cx=\"44\" cy=\"56\" r=\"3\" fill=\"{fg}\" />\n'
        f'<circle cx=\"52\" cy=\"52\" r=\"3\" fill=\"{fg}\" />\n'
        f'<circle cx=\"60\" cy=\"48\" r=\"3\" fill=\"{fg}\" />\n'
    )


def g_file_out(fg: str) -> str:
    return (
        f'<path d=\"M28,40 H48 L52,44 V68 H28 Z\" {stroke(fg)} />\n'
        f'<path d=\"M52,58 H72\" {stroke(fg, "marker-end=url(#arrow)")} />\n'
    )


def g_file_in(fg: str) -> str:
    return (
        f'<path d=\"M44,40 H64 L68,44 V68 H44 Z\" {stroke(fg)} />\n'
        f'<path d=\"M24,58 H44\" {stroke(fg, "marker-end=url(#arrow)")} />\n'
    )


def g_record_edit(fg: str) -> str:
    # document with small gear
    return (
        f'<rect x=\"26\" y=\"34\" width=\"40\" height=\"36\" rx=\"4\" {stroke(fg)} />\n'
        f'<line x1=\"30\" y1=\"42\" x2=\"62\" y2=\"42\" {stroke(fg)} />\n'
        f'<line x1=\"30\" y1=\"50\" x2=\"54\" y2=\"50\" {stroke(fg)} />\n'
        f'<circle cx=\"60\" cy=\"60\" r=\"6\" {stroke(fg)} />\n'
        f'<path d=\"M60,54 v-3 m0,18 v-3 m6,-6 h3 m-18,0 h3 m9,-4 l2,-2 m-2,10 l2,2 m-10,-2 l-2,2 m2,-10 l-2,-2\" {stroke(fg)} />\n'
    )


def g_table_plus(fg: str) -> str:
    # table with plus symbol
    return (
        f'<rect x=\"24\" y=\"36\" width=\"40\" height=\"28\" rx=\"4\" {stroke(fg)} />\n'
        f'<line x1=\"24\" y1=\"46\" x2=\"64\" y2=\"46\" {stroke(fg)} />\n'
        f'<line x1=\"34\" y1=\"36\" x2=\"34\" y2=\"64\" {stroke(fg)} />\n'
        f'<circle cx=\"66\" cy=\"62\" r=\"8\" {stroke(fg)} />\n'
        f'<path d=\"M66,58 v8 M62,62 h8\" {stroke(fg)} />\n'
    )


def g_compress(fg: str) -> str:
    # clamp/zip metaphor
    return (
        f'<path d=\"M34,36 h28 v12 h-8 v-4 h-12 v4 h-8 z\" {stroke(fg)} />\n'
        f'<rect x=\"42\" y=\"52\" width=\"12\" height=\"16\" rx=\"2\" {stroke(fg)} />\n'
        f'<path d=\"M48,44 v8 m0,16 v8\" {stroke(fg)} />\n'
    )


def g_content_route(fg: str) -> str:
    # document + split arrows
    return (
        f'<rect x=\"26\" y=\"34\" width=\"36\" height=\"28\" rx=\"4\" {stroke(fg)} />\n'
        f'<path d=\"M62,48 C70,48 72,46 76,44\" {stroke(fg, "marker-end=url(#arrow)")} />\n'
        f'<path d=\"M62,48 C70,52 72,54 76,56\" {stroke(fg, "marker-end=url(#arrow)")} />\n'
    )


GLYPHS = {
    "bolt": g_bolt,
    "gear": g_gear,
    "split-route": g_split_route,
    "log": g_log,
    "replace": g_replace,
    "search": g_search,
    "merge": g_merge,
    "split": g_split,
    "jsonpath": g_jsonpath,
    "json": g_json,
    "convert": g_convert,
    "query": g_query,
    "merge-record": g_merge_record,
    "http": g_http,
    "http-in": g_http_in,
    "http-out": g_http_out,
    "queue-out": g_queue_out,
    "queue-in": g_queue_in,
    "file-out": g_file_out,
    "file-in": g_file_in,
    "record-edit": g_record_edit,
    "table-plus": g_table_plus,
    "compress": g_compress,
    "content-route": g_content_route,
}


def render_svg(name: str, category: str, glyph: str, theme: str) -> str:
    color = COLORS.get(category, "#666")
    if theme == "light":
        fg = "#2d3640"; card = "#ffffff"; border = "#e6e9ee"
    else:
        fg = "#ffffff"; card = "#0c0d12"; border = "#1a1b20"
    body = GLYPHS[glyph](fg)
    return svg_header(fg) + svg_base(color, card, border) + body + "</svg>\n"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--theme", choices=["dark", "light"], default="dark")
    args = ap.parse_args()

    cfg = load_config(CONFIG)
    SVG_OUT = SVG_BASE / args.theme
    SVG_OUT.mkdir(parents=True, exist_ok=True)
    written = []
    for proc in cfg.get("processors", []):
        name = proc["name"]
        category = proc.get("category", "transform")
        glyph = proc.get("glyph", "convert")
        if glyph not in GLYPHS:
            raise SystemExit(f"Unknown glyph '{glyph}' for {name}")
        svg = render_svg(name, category, glyph, args.theme)
        out = SVG_OUT / f"{name}.svg"
        out.write_text(svg, encoding="utf-8")
        written.append(out.name)
    # Write a tiny manifest to help previews
    (SVG_OUT / "manifest.json").write_text(json.dumps({"icons": written}, indent=2), encoding="utf-8")
    print(f"Wrote {len(written)} icons to {SVG_OUT}")


if __name__ == "__main__":
    main()
