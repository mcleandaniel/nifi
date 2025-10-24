# Layout Orientation Toggle (Horizontal/Vertical) per Process Group

- Status: Draft
- Owner: @assistant
- Approvers: <add reviewers>
- Links: https://github.com/mcleandaniel/nifi/issues/1
- Date: 2025-10-24

## Context
Today our auto-layout produces a horizontal flow (left→right) with router-aware placement and input/output gutters. We want the option to render flows vertically (top→bottom) without breaking existing flows or explicit coordinates. This unlocks density and readability options and helps when embedding flows in dashboards.

## Goals / Non‑Goals
- Goals
  - Add a per-flow (process group) toggle to choose horizontal (default) or vertical layout.
  - Keep explicit positions authoritative regardless of orientation.
  - Preserve overlap checks and layout heuristics (router centering, sink stacking) across orientations.
- Non‑Goals
  - Full-fledged constraint solver or diagram engine.
  - Replacing existing heuristics beyond axis selection.

## Current Architecture (as‑is)
- Placement logic is localized in two helpers (automation/src/nifi_automation/flow_builder.py):
  - `_layout_child_groups(groups, child_columns)` – places child PGs on a grid/column layout.
  - `_layout_group_components(group)` – places processors/ports with router-aware heuristics.
- These run just before deploy, honor explicit positions, and do not bleed into NiFi REST client code.

## Proposal (to‑be)
### API/Schema changes
- YAML: optional layout directive on any process group. Root cascades to children unless overridden.
```yaml
process_group:
  name: NiFi Flow
  layout:
    direction: horizontal   # or vertical (default: horizontal)
  process_groups:
    - name: MyWorkflow
      layout:
        direction: vertical
```
- Internal: introduce `Orientation = {HORIZONTAL, VERTICAL}` on `ProcessGroupSpec` (in-memory), defaulting to HORIZONTAL.

### Algorithms / Components
- Thread `orientation` through layout entry points:
  - `_layout_child_groups(groups, orientation)`
  - `_layout_group_components(group, orientation)`
- Axis-agnostic helpers
  - Define `primary_step` and `secondary_step` derived from `(spacing_x, spacing_y, orientation)`.
  - Map gutters: input/output gutters select min/max of the primary axis depending on orientation.
- Horizontal mode (current behavior)
  - Primary axis: X. Router at center; sinks stacked on +X; parents on −X; input ports on left gutter; output on right gutter.
- Vertical mode (rotated 90°)
  - Primary axis: Y. Router at center; sinks stacked on +Y; parents on −Y; input ports at top gutter; outputs at bottom gutter.
  - Child group layout becomes row-first (or lane-first) using `spacing_y` as primary stride.
- Explicit positions remain authoritative under both orientations.

### Compatibility / Migration
- Backward compatible by default (no YAML change → horizontal).
- Explicit coordinates continue to work unchanged. Orientation only affects components without explicit positions.

## Testing Plan
- Unit-ish checks on layout helpers (no NiFi calls):
  - Tiny graphs asserting relative ordering: in vertical, sinks are below router; in horizontal, sinks are to the right.
  - Verify no overlaps via existing validator in both orientations on complex and nested flows.
- Integration: deploy a representative flow twice (horizontal/vertical) and confirm placement differences and zero overlaps.

## Rollout Plan
1. Add `Orientation` enum and YAML parsing; cascade root → children.
2. Implement axis swap + gutters in both `_layout_child_groups` and `_layout_group_components` (feature behind default horizontal).
3. Add tests; run existing integration suite; document the new YAML.
4. Optional: add a CLI override flag later (e.g., `--layout vertical`) for quick experiments.

## Risks & Mitigations
- Heuristic edge cases (deeply nested routers, many sinks): cover with a couple of stress graphs; ensure fallback grid still orients correctly.
- Diagrams/readme drift: keep examples minimal; rely on overlap validator rather than exact pixel snapshots.

## Alternatives Considered
- Full rewrite into a constraint-based layout engine: more power, much higher cost.
- Post-processing rotation of coordinates: simpler but breaks gutters and port placement semantics.

## Open Questions
- Do we want per-subgroup overrides to refine orientation within a larger flow? (Current design supports this.)
- Should spacing be user-configurable per orientation (`spacing_x/spacing_y` in YAML)? (Future extension.)
