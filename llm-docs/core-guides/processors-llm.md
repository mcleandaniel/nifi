# NiFi Processors — LLM Notes

*Source focus*: `nifi-docs/src/main/asciidoc/user-guide.adoc` sections on configuring processors (updated 2025-10-13) plus supporting lifecycle details from the developer guide and processor REST resources.

## Role in the Platform
- Processors are the primary runtime components that ingest, route, transform, and egress FlowFiles. They operate inside Process Groups and are packaged via NARs so that custom processors can be added.
- Each Processor exposes relationships, properties, scheduling hints, and optional controller-service references; NiFi persists configuration and run state so restarts resume work.

## Lifecycle & States
- **States**: *Stopped* (valid but idle), *Running*, *Invalid* (configuration errors or missing connections), *Disabled* (excluded from group-level start/stop). UI icons in the top-left indicate validity.
- **Start/Stop/Run Once**: Components start only when valid; `Run Once` executes one trigger without entering the scheduled loop.
- **Thread Management**: Internal engine may spawn task threads per concurrent task; administrators can terminate hung threads via the Operate Palette when needed.
- **Stateless vs Traditional Execution**: Traditional queues between processors and persists FlowFiles; Stateless treats a Process Group like a transaction, rolling back on failures/timeouts and not persisting intermediate queues.

## Configuration Dialog Overview
1. **Settings tab**
   - Rename processor, toggle Enabled flag, view immutable type/bundle metadata.
   - Configure **Penalty Duration** (default `30 sec`) to delay penalized FlowFiles, and **Yield Duration** (default `1 sec`) to pause scheduling after systemic failures.
   - Set Bulletin log level (default `WARN`) to control which log events surface in the UI.
2. **Scheduling tab**
   - **Scheduling Strategy**: Timer-driven (default) runs at `Run Schedule` interval; CRON-driven accepts Quartz-style expressions for calendar schedules.
   - **Concurrent Tasks**: Controls parallel threads; some processors enforce max of 1.
   - **Execution**: `All Nodes` vs `Primary Node` for clustered deployments; primary-only processors auto-limit to one concurrent task.
   - **Run Duration** slider: Trade latency for throughput by keeping a thread active longer before relinquishing.
   - Retry controls (NiFi 2.x): Per-relationship retry count, backoff policy (Penalize vs Yield), and maximum backoff window.
3. **Properties tab**
   - Lists processor-specific properties with inline help icons showing description, default, valid values, and last-set history.
   - Supports user-defined properties on processors that opt-in; these can be marked sensitive so NiFi encrypts them in `flow.xml.gz` and omits from exports.
   - Properties often reference Controller Services; the UI allows on-the-spot creation/configuration of those services.
   - Some processors expose an **Advanced UI** (e.g., UpdateAttribute) accessible via an “Advanced” button when present.
4. **Relationships tab**
   - Shows every named relationship (success, failure, etc.). Each must be connected downstream or explicitly auto-terminated.
   - Retry toggles per relationship send FlowFiles back through the processor up to a configured attempt count before respecting success/failure routing.
   - Auto-termination removes FlowFiles from the flow after routing to that relationship.
5. **Comments tab**
   - Free-form notes persisted with the processor; useful for operator handoffs.

## Validation & Restricted Components
- NiFi performs live validation; processors with unmet requirements show a warning badge. Hovering reveals specific property or relationship issues. Processors must be valid before they can run.
- Relationships must either connect to another component or be set to auto-terminate; otherwise validation fails.
- **Restricted processors** (marked with a shield icon in the toolbar) require special authorization because they can execute scripts, access host resources, or bypass sandboxing. Administrators grant restrictions via multi-tenant policies.

## Interaction with Other Platform Features
- **Controller Services**: Shared resource providers (SSL contexts, DB pools) referenced by processors. Enabling/disabling services triggers lifecycle annotations (`@OnEnabled`, `@OnDisabled`).
- **Parameter Contexts**: Properties can reference `${parameter}` values to decouple environment-specific configuration.
- **State Management**: Processors use `StateManager` APIs for small key/value state (≤1 MB) stored locally or cluster-wide; consider implications when scaling stateless flows.
- **Provenance**: Implementations should emit provenance events for receives/sends/route/drop to maintain lineage; the UI surfaces them under Data Provenance.
- **Documentation Access**: Right-click → *Usage* or the global Help link opens the packaged processor usage docs generated from annotations (`@CapabilityDescription`, `@Tags`, etc.).

## Operational Tips for LLM Responses
- When users report a processor won’t start, check for validation errors (e.g., missing property, unconnected relationship, disabled controller service).
- For scheduling questions, highlight Timer vs CRON modes, concurrent tasks, and run-duration effects. Mention primary-node execution for cluster-only operations like interacting with external stores that must be single-writer.
- Troubleshooting retries: point to Relationships tab settings (retry count, backoff policy, max backoff) and Settings tab yield/penalty durations.
- Sensitive property handling: processors that allow user-defined properties can mark them sensitive; remind users that values then appear redacted in the UI and are encrypted on disk.
- For stateless behavior quirks (e.g., merged FlowFiles never trigger), remind that each concurrent task maintains its own internal state and transactions roll back on failure or timeout.
- Direct users needing custom logic to either configure scripting processors (with caution about restrictions) or develop/pack a new NAR following developer guide patterns.

## Quick FAQ References
1. **“How do I throttle a processor?”** → Adjust Run Schedule for timer-driven processors or use backpressure on downstream connections; Run Duration slider also influences throughput bursts.
2. **“Processor keeps retrying forever.”** → Check Relationships tab retry count/max backoff and ensure there’s a route (e.g., failure) without retry to break the loop.
3. **“Why does my processor show a lock icon?”** → It’s restricted; assign the user the necessary restriction policies in the Admin UI.
4. **“How do I edit a running processor?”** → Stop it (allow active threads to finish), make changes, then restart. The Configure option is disabled while running.
5. **“What’s the fastest way to jump to documentation for this processor?”** → Right-click → Usage or Help → Processors and search by tag/type.
