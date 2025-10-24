# Group Labels — Positioning and Sizing Rules

This document describes how group “wrap” labels are positioned and sized on the
root canvas after groups are flattened for deployment. Labels are cosmetic and
are created after all child Process Groups (PGs) have been deployed.

## Goals
- Visual grouping: wrap each group’s column(s) with a translucent label.
- Consistent alignment across groups: uniform top and bottom baselines.
- Configurable spacing: tie padding to existing PG spacing (no magic numbers).

## Inputs
- PG layout:
  - Intra-group horizontal spacing: `spacing_x` (default ~700)
  - Intra-group vertical spacing: `spacing_y` (default ~450)
- Group membership map: top-level child PG name -> group name (Default for non-grouped children).
- Column mapping: top-level child PG name -> column index (0 for Default, left-to-right for groups).
- Group descriptions: map of group name -> description.
- Label style: background color per group (eventually from config).

## Calculation
1. Determine positions
   - Use each child PG’s computed position (`(x, y)`).
   - For each group, collect all child PG positions.

2. Compute lanes and rows (per group)
   - Lanes (columns within the group): `lanes = max(round((x - min_x)/spacing_x)) + 1`.
   - Rows: `rows = max(round((y - min_y)/spacing_y)) + 1`.

3. Compute global top and tallest group
   - `global_min_y = min(min_y across all groups)`.
   - `rows_max = max(rows across all groups)`.

4. Padding and extra margins
   - Top padding: `top_pad = 0.25 * spacing_y` (for name/description).
   - Right extra: `right_extra = 0.25 * spacing_x`.
   - Bottom extra: `bottom_extra = 0.25 * spacing_y`.
   - Left padding: `left_pad = 0.25 * spacing_x`.

5. Final label bounds per group
   - Left: `x = min_x - left_pad`.
   - Top: `y = global_min_y - top_pad`.
   - Width: `lanes * spacing_x + right_extra`.
   - Height: `rows_max * spacing_y + top_pad + bottom_extra`.

This ensures:
- Left edge has 0.25×spacing_x padding.
- Right edge extends exactly 0.25×spacing_x beyond the group’s rightmost column.
- Top aligned globally with 0.25×spacing_y padding for name/desc across labels.
- Bottom aligned globally (tallest rows across all groups) with 0.25×spacing_y extra.

## Edge Cases
- Groups with missing positions: skip label creation.
- Groups with empty children: do not create label.
- “Really big” descriptions: TODO — wrap, truncate, or increase `top_pad` based on rendered text metrics.
  - Add a config key for maximum label text lines before truncation.

## Config
- Spacing defaults (`spacing_x`, `spacing_y`) come from layout defaults; surface them from `config/flow-defaults.yaml`.
- Colors: add a list under `label_colors` in the same config (cycled across groups).

## Runtime
- Labels are best-effort and created at the root PG after deployment; failures are ignored.
- Clear-down: labels must be deleted as part of purge.
  - The purge now deletes labels (see cleanup helpers) before other components.

## Known Issues / Open Questions
- The right and bottom spacing may still appear larger than desired depending on actual NiFi PG dimensions vs our logical `spacing_x/spacing_y` grid. We currently use:
  - Right: `lanes * spacing_x + 0.25 * spacing_x`
  - Bottom: `rows_max * spacing_y + 0.25 * spacing_y (top) + 0.25 * spacing_y (bottom)`
- Improvement path:
  - Fetch real PG/label dimensions from NiFi defaults or stylesheet (once exposed) and adjust bounds accordingly.
  - Expose `label_padding_top/left/right/bottom` in config to tune per-environment without code changes.
  - Consider measuring rendered text height for descriptions to set `top_pad` more precisely.

## Future Improvements
- Read label styles/colors from config with per-group overrides.
- Smarter description wrapping (measure text height to adjust `top_pad`).
- Optional “border” around grouped columns with rounded corners.
