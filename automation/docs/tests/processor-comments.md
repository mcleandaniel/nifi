# Processor Comments — Authoring Note (Manual)

Purpose
- Allow authors to add a short, human‑readable note explaining a processor’s intent when it isn’t obvious.
- This is a manual convention (not enforced by rules); use judgment.

Scope
- Applies to every processor entry in flow specs under `automation/flows/*.yaml` (including the aggregate `NiFi_Flow.yaml`).
- Excludes ports and process groups (handled separately if needed).

YAML Schema
- Optional `comments:` (string, multi‑line allowed) at the processor level:

```yaml
processors:
  - id: complex-query
    name: QueryRecord (Complex)
    type: org.apache.nifi.processors.standard.QueryRecord
    comments: |
      Selects records into high/low streams using reading_value threshold.
      Failure and unmatched routed to dedicated sink for diagnosis.
    properties:
      record-reader: json-reader
      record-writer: json-writer
      high: SELECT * FROM FLOWFILE WHERE reading_value >= 50
      low: SELECT * FROM FLOWFILE WHERE reading_value < 50
```

When to write a comment (guidance, not a rule)
- If the name and type don’t fully convey “what” and “why”.
- If key behavior depends on a predicate, schema, or external system (e.g., RouteOnAttribute with EL, ConvertRecord with specific readers/writers, InvokeHTTP calling an upstream).
- Keep it short; include the one detail future readers will care about (predicate, threshold, target).

Enforcement
- None. This is an authoring aid. Reviewers can request a comment when helpful.

Authoring Guidance
- Use multi‑line `|` block scalars for anything longer than a sentence.
- Co‑locate comments with processors; avoid repeating full documentation in the MD suite.
- If a processor’s `name` already conveys intent (e.g., “RouteOnAttribute (east/west by `route`)”), still prefer a short `comments` explaining the predicate.

Examples

Good
```yaml
- id: path-route
  name: Route On Attribute (path)
  type: org.apache.nifi.processors.standard.RouteOnAttribute
  comments: Routes east/west via Expression Language predicates on attribute `route`.
  properties:
    east: ${route:equals('east')}
    west: ${route:equals('west')}
```

Bad (missing comments on non‑trivial type)
```yaml
- id: cg-query
  name: QueryRecord (ok/other)
  type: org.apache.nifi.processors.standard.QueryRecord
  properties:
    record-reader: csv-reader
    record-writer: csv-writer
    ok: SELECT * FROM FLOWFILE WHERE route = 'success'
    other: SELECT * FROM FLOWFILE WHERE route <> 'success'
```

Test Plan
- None required for enforcement. Optional: add style checks later if the team wants advisories.

Adoption Notes
- Keep comments focused; avoid restating processor names.
