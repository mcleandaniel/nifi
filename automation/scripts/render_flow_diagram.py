#!/usr/bin/env python3
"""
Render simple HTML/SVG diagrams from a NiFi flow YAML using our icon set.

Outputs per‑group HTML files under automation/diagrams/out/ and an index.html.

Dependencies: PyYAML (preferred). If missing, the script exits with an
actionable message, since full parsing is non‑trivial for this spec.

Usage:
  python automation/scripts/render_flow_diagram.py [PATH_TO_YAML]
"""
from __future__ import annotations

import argparse
import html
import os
from dataclasses import dataclass
import re
from pathlib import Path
from typing import Dict, List, Tuple, Optional

try:
    import yaml  # type: ignore
except Exception as e:  # pragma: no cover - thin CLI helper
    print("ERROR: PyYAML is required for render_flow_diagram.py.\n"
          "Install into your venv: pip install pyyaml\n"
          "(venv) $ source automation/.venv/bin/activate && pip install pyyaml")
    raise

ROOT = Path(__file__).resolve().parents[2]
ASSETS_DIR = ROOT / "automation" / "assets" / "processor-icons" / "svg"
OUT_DIR = ROOT / "automation" / "diagrams" / "out"


@dataclass
class Node:
    id: str
    kind: str  # processor|input_port|output_port|process_group
    name: str
    type_short: Optional[str] = None  # for processors
    layer: int = 0
    order: int = 0
    x: int = 0
    y: int = 0
    href: Optional[str] = None  # for process_group navigation


@dataclass
class Edge:
    src: str
    dst: str
    name: str = ""


# Map NiFi type short names to our icon filenames (without .svg)
TYPE_TO_ICON_NAME: Dict[str, str] = {
    "GenerateFlowFile": "GenerateFlowFile",
    "LogAttribute": "LogAttribute",
    "RouteOnAttribute": "RouteOnAttribute",
    "SplitText": "SplitText",
    "MergeRecord": "MergeRecord",
    "MergeContent": "MergeContent",
    "ConvertRecord": "ConvertRecord",
    "QueryRecord": "QueryRecord",
    "AttributesToJSON": "AttributesToJSON",
    "HandleHttpRequest": "HandleHttpRequest",
    "HandleHttpResponse": "HandleHttpResponse",
    "PutFile": "PutFile",
    "GetFile": "GetFile",
    # Explicit icons for newly added processors
    "UpdateRecord": "UpdateRecord",
    "GenerateRecord": "GenerateRecord",
    "CompressContent": "CompressContent",
    "RouteOnContent": "RouteOnContent",
}


def short_type(fqcn: str) -> str:
    return fqcn.split(".")[-1]


def safe_name(title: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", title)


def build_group_graph(pg: dict, title_prefix: str) -> Tuple[Dict[str, Node], List[Edge]]:
    nodes: Dict[str, Node] = {}
    edges: List[Edge] = []

    for p in pg.get("processors", []) or []:
        sid = p["id"]
        nm = p.get("name", sid)
        tshort = short_type(p.get("type", "Processor"))
        nodes[sid] = Node(id=sid, kind="processor", name=nm, type_short=tshort)

    for port in pg.get("input_ports", []) or []:
        sid = port["id"]
        nm = port.get("name", sid)
        nodes[sid] = Node(id=sid, kind="input_port", name=nm)

    for port in pg.get("output_ports", []) or []:
        sid = port["id"]
        nm = port.get("name", sid)
        nodes[sid] = Node(id=sid, kind="output_port", name=nm)

    for c in pg.get("connections", []) or []:
        src = c["source"]
        dst = c["destination"]
        nm = c.get("name", f"{src}->{dst}")
        edges.append(Edge(src=src, dst=dst, name=nm))

    # Represent child process groups as clickable nodes linking to their pages
    for idx, child in enumerate(pg.get("process_groups", []) or []):
        nm = child.get("name", f"Group{idx}")
        child_title = f"{title_prefix}/{nm}" if title_prefix else nm
        href = f"{safe_name(child_title)}.html"
        nid = f"pg::{safe_name(nm)}::{idx}"
        nodes[nid] = Node(id=nid, kind="process_group", name=nm, href=href)

    return nodes, edges


def topological_layers(nodes: Dict[str, Node], edges: List[Edge]) -> None:
    indeg: Dict[str, int] = {nid: 0 for nid in nodes}
    succ: Dict[str, List[str]] = {nid: [] for nid in nodes}
    for e in edges:
        if e.src in nodes and e.dst in nodes:
            indeg[e.dst] += 1
            succ[e.src].append(e.dst)

    layer = 0
    assigned = set()
    while len(assigned) < len(nodes):
        frontier = [nid for nid, d in indeg.items() if d == 0 and nid not in assigned]
        if not frontier:
            # cycle or cross-boundary; assign the remaining arbitrarily
            frontier = [nid for nid in nodes.keys() if nid not in assigned]
        for i, nid in enumerate(frontier):
            n = nodes[nid]
            n.layer = layer
            n.order = i
            assigned.add(nid)
            for s in succ.get(nid, []):
                indeg[s] = max(0, indeg[s] - 1)
        layer += 1
    # Push process_group nodes to the rightmost layer for navigation
    if nodes:
        max_layer = max((n.layer for n in nodes.values() if n.kind != "process_group"), default=0)
        pg_nodes = [n for n in nodes.values() if n.kind == "process_group"]
        for i, n in enumerate(pg_nodes):
            n.layer = max_layer + 1
            n.order = i


def place(nodes: Dict[str, Node]) -> None:
    # Simple grid placement per layer
    dx, dy = 220, 140
    margin_x, margin_y = 40, 60
    by_layer: Dict[int, List[Node]] = {}
    for n in nodes.values():
        by_layer.setdefault(n.layer, []).append(n)
    for L, arr in by_layer.items():
        arr.sort(key=lambda n: (n.kind != "input_port", n.order, n.name))
        for idx, n in enumerate(arr):
            n.x = margin_x + L * dx
            n.y = margin_y + idx * dy


def icon_href(n: Node, theme: str) -> Optional[str]:
    if n.kind != "processor":
        return None
    base = TYPE_TO_ICON_NAME.get(n.type_short or "", "ConvertRecord")
    filename = f"{base}.svg"
    themed = ASSETS_DIR / theme / filename
    if themed.exists():
        return f"../assets/processor-icons/svg/{theme}/" + filename
    p = ASSETS_DIR / filename
    if p.exists():
        return "../assets/processor-icons/svg/" + filename
    return None


def render_svg(pg_name: str, nodes: Dict[str, Node], edges: List[Edge], theme: str) -> str:
    width = max((n.x for n in nodes.values()), default=0) + 300
    height = max((n.y for n in nodes.values()), default=0) + 220
    parts: List[str] = []
    parts.append(f"<svg xmlns='http://www.w3.org/2000/svg' width='{width}' height='{height}' viewBox='0 0 {width} {height}'>")
    if theme == "light":
        edge = "#6b7280"; label = "#374151"; title = "#111827"; port = "#2563eb"; box = "#ffffff"; border = "#e5e7eb"; arrow = edge
    else:
        edge = "#9da3b0"; label = "#cfd3da"; title = "#e6e6e6"; port = "#1f6feb"; box = "#12131a"; border = "#1a1b20"; arrow = edge
    parts.append("<defs>" \
                 f"<marker id='arrow' markerWidth='8' markerHeight='8' refX='4' refY='4' orient='auto-start-reverse'><path d='M0,0 L8,4 L0,8 z' fill='{arrow}'/></marker>" \
                 f"<style><![CDATA[ .edge{{stroke:{edge};stroke-width:1.8;fill:none}} .label{{font:12px system-ui;fill:{label}}} .title{{font:16px system-ui;fill:{title}}} .port{{fill:{port}}} .box{{fill:{box}; stroke:{border}; stroke-width:1}} ]]></style>" \
                 "</defs>")

    # Title
    parts.append(f"<text x='24' y='28' class='title'>{html.escape(pg_name)}</text>")

    # Edges
    for e in edges:
        if e.src not in nodes or e.dst not in nodes:
            continue
        s = nodes[e.src]; d = nodes[e.dst]
        x1 = s.x + 96 + 8 if s.kind == "processor" else s.x + 24
        y1 = s.y + (96//2 if s.kind == "processor" else 12)
        x2 = d.x - 8 if d.kind == "processor" else d.x + 24
        y2 = d.y + (96//2 if d.kind == "processor" else 12)
        mx = (x1 + x2) / 2
        path = f"M{x1},{y1} C{mx},{y1} {mx},{y2} {x2},{y2}"
        parts.append(f"<path d='{path}' class='edge' marker-end='url(#arrow)'/>")

    # Nodes
    for n in nodes.values():
        if n.kind == "processor":
            href = icon_href(n, theme)
            if href:
                parts.append(f"<image href='{href}' x='{n.x}' y='{n.y}' width='96' height='96' />")
            else:
                parts.append(f"<rect x='{n.x}' y='{n.y}' width='96' height='96' rx='12' class='box' />")
            parts.append(f"<text x='{n.x+48}' y='{n.y+112}' text-anchor='middle' class='label'>{html.escape(n.name)}</text>")
        elif n.kind == "input_port":
            parts.append(f"<circle cx='{n.x+24}' cy='{n.y+12}' r='10' class='port' />")
            parts.append(f"<text x='{n.x+48}' y='{n.y+16}' class='label'>{html.escape(n.name)} (in)</text>")
        elif n.kind == "output_port":
            parts.append(f"<rect x='{n.x+14}' y='{n.y+2}' width='20' height='20' class='port' rx='4' />")
            parts.append(f"<text x='{n.x+40}' y='{n.y+16}' class='label'>{html.escape(n.name)} (out)</text>")
        elif n.kind == "process_group":
            # clickable group card linking to sub-group page
            card_w, card_h = 120, 90
            gx, gy = n.x, n.y
            g = (
                f"<a href='{html.escape(n.href or '#')}'><g cursor='pointer'>"
                f"<rect x='{gx}' y='{gy}' width='{card_w}' height='{card_h}' rx='12' class='box' />"
                # folder/tab indicator
                f"<rect x='{gx}' y='{gy}' width='{card_w}' height='18' rx='12' class='port' fill-opacity='0.2' />"
                f"<text x='{gx + card_w/2}' y='{gy + card_h + 16}' text-anchor='middle' class='label'>{html.escape(n.name)} (group)</text>"
                f"</g></a>"
            )
            parts.append(g)

    parts.append("</svg>")
    return "\n".join(parts)


def write_group_page(pg_name: str, svg: str, theme: str) -> str:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    fname = f"{safe_name(pg_name)}.html"
    html_path = OUT_DIR / fname
    bg = "#f7fafc" if theme == "light" else "#0b0c10"
    fg = "#111827" if theme == "light" else "#e6e6e6"
    border = "#e5e7eb" if theme == "light" else "#1a1b20"
    # Compute breadcrumb link
    parts = pg_name.split("/")
    if len(parts) > 1:
        parent_title = "/".join(parts[:-1])
        parent_href = f"{safe_name(parent_title)}.html"
        crumb = f"<a href='{parent_href}' style=\"color:{fg};text-decoration:none\">\u2190 Back to {parts[-2]}</a>"
    else:
        crumb = f"<a href='index.html' style=\"color:{fg};text-decoration:none\">\u2190 Back to Index</a>"
    doc = f"""
<!doctype html>
<html lang='en'>
  <meta charset='utf-8'>
  <meta name='viewport' content='width=device-width, initial-scale=1'>
  <title>{html.escape(pg_name)}</title>
  <body style=\"margin:0;background:{bg};color:{fg}\">
    <div style=\"position:sticky;top:0;padding:10px 16px;border-bottom:1px solid {border};background:{bg}\">{crumb}</div>
    {svg}
  </body>
</html>
"""
    html_path.write_text(doc, encoding="utf-8")
    return fname


def write_index(pages: List[Tuple[str, str]], theme: str) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    lis = "\n".join(
        [f"<li><a href='{fn}'>{html.escape(name)}</a></li>" for name, fn in pages]
    )
    bg = "#f7fafc" if theme == "light" else "#0b0c10"
    fg = "#111827" if theme == "light" else "#e6e6e6"
    index = f"""
<!doctype html>
<html lang='en'>
  <meta charset='utf-8'>
  <meta name='viewport' content='width=device-width, initial-scale=1'>
  <title>Flow Diagram Index</title>
  <body style=\"background:{bg};color:{fg};font:16px system-ui;margin:24px\">
    <h1 style=\"font:20px system-ui\">Flow Diagram Index ({theme})</h1>
    <ul>\n{lis}\n    </ul>
    <p style=\"color:{fg}\">Icons are loaded from <code>automation/assets/processor-icons/svg/{theme}</code>.</p>
  </body>
 </html>
"""
    (OUT_DIR / "index.html").write_text(index, encoding="utf-8")


def collect_groups(pg: dict, prefix: str = "") -> List[Tuple[str, dict]]:
    name = pg.get("name", "Unnamed Group")
    title = f"{prefix}{name}" if not prefix else f"{prefix}/{name}"
    out = [(title, pg)]
    for child in pg.get("process_groups", []) or []:
        out.extend(collect_groups(child, title))
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("spec", nargs="?", default=str(ROOT / "automation" / "flows" / "NiFi_Flow.yaml"))
    ap.add_argument("--theme", choices=["dark", "light"], default="dark")
    args = ap.parse_args()

    data = yaml.safe_load(Path(args.spec).read_text(encoding="utf-8"))
    root_pg = data.get("process_group") or {}
    groups = collect_groups(root_pg)

    pages: List[Tuple[str, str]] = []
    for title, pg in groups:
        nodes, edges = build_group_graph(pg, title)
        if not nodes:
            # Skip empty leaf groups
            continue
        topological_layers(nodes, edges)
        place(nodes)
        svg = render_svg(title, nodes, edges, args.theme)
        fn = write_group_page(title, svg, args.theme)
        pages.append((title, fn))
    write_index(pages, args.theme)
    print(f"Wrote {len(pages)} pages to {OUT_DIR}")


if __name__ == "__main__":
    main()
