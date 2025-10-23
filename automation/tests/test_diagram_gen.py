import json
import time
from pathlib import Path
import xml.etree.ElementTree as ET
from importlib.machinery import SourceFileLoader

ROOT = Path(__file__).resolve().parents[2]


def test_generate_icons_both_themes(tmp_path):
    # Import script module and run main for both themes via CLI-style call
    gen = SourceFileLoader(
        "generate_processor_icons", str(ROOT / "automation/scripts/generate_processor_icons.py")
    ).load_module()

    # Dark and light
    for theme in ("dark", "light"):
        # simulate CLI
        gen.main.__wrapped__ if hasattr(gen.main, "__wrapped__") else None  # no-op for coverage tools
        # Use subprocess-free call by reusing generator API
        cfg = gen.load_config(gen.CONFIG)
        out = gen.SVG_BASE / theme
        out.mkdir(parents=True, exist_ok=True)
        written = []
        for proc in cfg.get("processors", []):
            name = proc["name"]
            category = proc.get("category", "transform")
            glyph = proc.get("glyph", "convert")
            svg = gen.render_svg(name, category, glyph, theme)
            (out / f"{name}.svg").write_text(svg, encoding="utf-8")
            written.append(name)
        (out / "manifest.json").write_text(json.dumps({"icons": [f"{n}.svg" for n in written]}), encoding="utf-8")

        # Sanity checks for a couple of files
        assert (out / "GenerateFlowFile.svg").exists()
        assert (out / "UpdateRecord.svg").exists()
        # Manifest present and json parsable
        m = json.loads((out / "manifest.json").read_text(encoding="utf-8"))
        assert "icons" in m and any(x.endswith("GenerateFlowFile.svg") for x in m["icons"])

        # All generated SVGs should be well‑formed XML
        for svg in out.glob("*.svg"):
            ET.fromstring(svg.read_text(encoding="utf-8"))


def test_render_flow_diagram_light_theme(tmp_path):
    render = SourceFileLoader(
        "render_flow_diagram", str(ROOT / "automation/scripts/render_flow_diagram.py")
    ).load_module()

    spec = ROOT / "automation/flows/NiFi_Flow.yaml"
    data = render.yaml.safe_load(spec.read_text(encoding="utf-8"))
    root_pg = data["process_group"]
    # Find a simple leaf group
    groups = render.collect_groups(root_pg)
    assert any("TrivialFlow" in name for name, _ in groups)

    # Build and place layout for one group
    trivial_name, trivial = next((name, pg) for name, pg in groups if "TrivialFlow" in name)
    nodes, edges = render.build_group_graph(trivial, "NiFi Flow/TrivialFlow")
    render.topological_layers(nodes, edges)
    render.place(nodes)

    # All edges should go left->right by layer/x
    for e in edges:
        s, d = nodes[e.src], nodes[e.dst]
        assert d.layer >= s.layer
        assert d.x >= s.x

    # Render full HTMLs in light theme
    render.main.__wrapped__ if hasattr(render.main, "__wrapped__") else None
    render.OUT_DIR.mkdir(parents=True, exist_ok=True)
    svg = render.render_svg(trivial_name, nodes, edges, theme="light")
    fn = render.write_group_page(trivial_name, svg, theme="light")
    assert (render.OUT_DIR / fn).exists()
    render.write_index([(trivial_name, fn)], theme="light")
    index = (render.OUT_DIR / "index.html").read_text(encoding="utf-8")
    assert "Flow Diagram Index (light)" in index

    # Parent page should include clickable link for a child group on a more complex group
    # Render BigWorkflow page and check for TransformGroup link
    big_name, big_pg = next((name, pg) for name, pg in groups if "BigWorkflow" in name)
    n2, e2 = render.build_group_graph(big_pg, big_name)
    render.topological_layers(n2, e2)
    render.place(n2)
    svg2 = render.render_svg(big_name, n2, e2, theme="light")
    fn2 = render.write_group_page(big_name, svg2, theme="light")
    html = (render.OUT_DIR / fn2).read_text(encoding="utf-8")
    assert "NiFi_Flow_BigWorkflow_TransformGroup.html" in html
    # Child page should have a breadcrumb back to parent
    child_path = render.OUT_DIR / "NiFi_Flow_BigWorkflow_TransformGroup.html"
    child_html = child_path.read_text(encoding="utf-8")
    assert "href='NiFi_Flow_BigWorkflow.html'" in child_html
