# NiFi Flow Automation – Design Log

This log captures key decisions, ideas, and open questions as the automation evolves. Entries are chronological (latest first).

---
## 2025-10-14
- **Metadata-driven validation**: Flow deployer now pulls processor definitions from `/flow/processor-definition/...` so property names, allowable values, and relationship lists are resolved per NiFi bundle. Spec entries must use UI-facing property names (e.g., `Batch Size`), and invalid/unknown properties fail fast before REST mutations.
- **Controller service stubs**: Planner inspects descriptors that expose `typeProvidedByValue` metadata and provisions placeholder controller services when a processor requires one but the spec omits it. Stub selection favours implementations with minimal required configuration and fills their required properties with defaults or placeholders, leaving services disabled for operators to wire later.
- **Auto-termination inference**: In absence of user overrides, any processor relationship without a downstream connection is auto-terminated automatically. Explicit `auto_terminate` entries are validated against known relationships so misconfigurations surface early.
- **Integration testing guardrails**: Added an opt-in pytest suite (`RUN_NIFI_INTEGRATION=1`) that deploys a flow against a live NiFi at `https://localhost:8443/nifi-api`, verifies inferred controller services, and tears the group back down. Keeps live checks isolated while unit tests cover planning logic.
- **Sub-process group refresh (deferred)**: Decided to postpone selective child process group refresh support; current automation continues to delete/recreate entire process groups until the override strategy is revisited in a later phase.
- **Component inventory docs**: Created `docs/components/` with stubs (`processors.md`, `controller-services.md`) to capture implementation requirements per processor/controller. Plan to auto-generate tables from NiFi metadata endpoints.
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
