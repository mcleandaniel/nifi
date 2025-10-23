Processor Icons (Experimental)
================================

Purpose
- Vector icons for rendering flow diagrams outside of NiFi based on our YAML specs.
- Generated programmatically to keep style consistent and make it easy to add new processors.

Layout
- `icons.yml` – list of processors, categories, and glyph types.
- `svg/` – generated SVGs (committed).
- `preview/index.html` – quick visual grid to browse icons.

Design System
- Canvas: 96×96, rounded 12px corner card with a colored header bar.
- Categories and colors:
  - source `#2ecc71`
  - sink `#9b59b6`
  - transform `#3498db`
  - route `#e67e22`
  - utility `#95a5a6`
  - network `#1abc9c`
  - messaging `#e91e63`
  - storage `#8e6b3a`
  - compute `#f1c40f`
- Strokes use `#ffffff` at 2.5px with rounded caps/joins for glyphs.

Usage
- Generate dark theme icons (default):
  - `python automation/scripts/generate_processor_icons.py --theme dark`
- Generate light theme icons:
  - `python automation/scripts/generate_processor_icons.py --theme light`
- Icons are written to `svg/<theme>/`. The preview page currently loads the `dark` manifest by default.
- Add new processors by appending entries to `icons.yml` with a recognized `glyph`.

Notes
- No trademarked logos are used. Kafka, S3, etc. are expressed with generic metaphors (queues, buckets, clouds).
- If we later need PNGs, we can add an optional dependency (e.g., `cairosvg`) and a conversion step, but SVG is preferred.
