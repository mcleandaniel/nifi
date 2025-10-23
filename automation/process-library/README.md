# Process Group Library

Reusable, self-contained Process Group (PG) fragments that can be injected into flows at deploy time.

Guiding principles
- Each library PG exposes one or more `input_ports` and `output_ports` so parent flows can wire them.
- Fragments are stored under `automation/process-library/` as standalone YAML files with a top-level `process_group` key.
- For early iterations we compose flows using a small preprocessor script that inlines library PGs into a harness flow.
  Later, the deployer may learn native `library_includes` support.

Quick example
- `EchoLogger.yaml`: input → LogAttribute → output
- `AttributeTagger.yaml`: input → UpdateAttribute (adds `lib.tagged=true`) → output

See `automation/flows/library/http_library_harness.yaml` and the composer script
`automation/scripts/compose_with_library.py` for a runnable harness that embeds these PGs behind a simple HTTP endpoint.

