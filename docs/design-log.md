# NiFi Flow Automation – Design Log

This log captures key decisions, ideas, and open questions as the automation evolves. Entries are chronological (latest first).

---
## 2025-10-14
- **Auto-layout strategy**: Default to an automated layout (initially a simple layered/linear algorithm) when positions are omitted. Provide spec/CLI overrides for manual positioning. Investigate graph-based layouts (e.g., networkx/dagre) for future iterations.
- **Spec versus FlowSnapshot**: Align YAML spec closely with NiFi FlowSnapshot JSON structure, but allow heavy use of defaults and human-readable IDs. This reduces impedance mismatch and eases import/export. Deployer populates required fields (bundle info, queue settings, positions) when omitted.
- **Processor metadata**: Retain plan to query NiFi’s metadata endpoints to validate properties, determine auto-terminable relationships, and discover controller-service requirements instead of hardcoding.
- **Plugin vs. REST**: Confirmed we will *not* build a NiFi plugin. Automation remains an external CLI interacting via REST, enabling easier deployment and tooling integration (e.g., MCP server).
- **Long-term vision**: Use this automation to power an MCP server capable of constructing flows programmatically and to generate clearer diagrams/layouts than the default UI export.

---
## 2025-10-13
- **Flow spec foundation**: Established initial YAML structure (`process_group`, `processors`, `connections`, `auto_terminate`). Positions default to `idx * 400` horizontal spacing; future layout engine will improve this.
- **CLI behaviors**: `deploy-flow` deletes existing process group with same name prior to reconstruction for idempotent runs. Prompts for credentials only when not provided via `.env`.
- **Auto-termination**: Spec supports `auto_terminate` shorthand; deployer applies via REST `PUT /processors/{id}` updates.
- **REST client updates**: Added helper methods to resolve processor bundles, create processors/connections, and update auto-termination. Connection payloads now include required queue/backpressure defaults to avoid NiFi 500 errors.

