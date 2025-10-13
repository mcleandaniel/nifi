# NiFi User Guide — LLM Notes

*Source*: `nifi-docs/src/main/asciidoc/user-guide.adoc` (reviewed 2025-10-13)

## Purpose
- Walks DataFlow Managers (DFMs) through the NiFi user interface, component model, and daily operations.
- Covers building flows, securing access, operating components, monitoring health, and auditing data movement.

## UI Primer
- **Browser Support**: Edge, Firefox, Chrome, and Safari (Current and Current‑1) are supported.
- **Core Terminology**: FlowFile (content + attributes), Processor, Connection, Process Group, Remote Process Group (RPG), Port, Funnel, Controller Service, Reporting Task, Bulletin.
- **UI Layout**: Global menu bar, breadcrumb navigator, component toolbar (drag items to canvas), status bar for cluster state and bulletins, queue counters with backpressure indicators.
- **Multi-Tenant Access**: With authorization enabled, users see only components they are allowed to view; restricted components display a lock icon until proper policies granted.

## Building a DataFlow
- Drag components from toolbar; dialogs allow filtering by tag cloud, name, or bundle.
- Context menu actions include Configure, Start/Stop, Run Once, Enable/Disable, View configuration/history, Copy/Paste, Group, Download flow definition, Empty queues, and Delete.
- **Component Types**:
  - *Processor*: Adds ingestion, routing, or transformation logic. Restricted processors marked with shield icon and require special policy.
  - *Input/Output Ports*: Expose ingress/egress within process groups or for Site-to-Site.
  - *Process Group*: Encapsulates subflows; breadcrumbs support drill-down; versioned groups can be tied to NiFi Registry.
  - *Remote Process Group*: Connects to external NiFi instances; supports secure Site-to-Site with load balancing across nodes.
  - *Funnel*: Consolidates multiple connections; helpful for prioritizers.
  - *Label*: Adds annotations to canvas.
- **Connections**: Configure source/destination, relationships, backpressure thresholds (count/size), prioritizers, and load-balancing strategy.
- **Templates / Download Flow**: Export subset of flow as template JSON (non-versioned) for sharing or registry import.

## Execution Engines
- **Traditional (default)**: Independent scheduling per component, durable queues (persisted on restart), respects backpressure, supports large parallelism.
- **Stateless**: Treats process group as single unit; each concurrent task walks an entire flow; queues not persisted; best for transactional single-source/single-destination use cases.
- Section provides scheduling, failure recovery, merging, and decision guidance for when to choose each engine.

## Command & Control
- Components start in *Stopped* state; must be valid and connected before starting.
- “Run Once” executes a processor a single time without fully starting scheduling.
- Disable processors/services to edit properties without receiving data; enable restores configuration.
- Bulletin icons flag validation errors, critical events, and warnings directly on components.
- Process Groups support start/stop/enable/disable for entire subflows, download definition, and empty queues.
- Controller Services can be enabled/disabled in Settings → Controller Services or per group; enabling triggers annotated lifecycle (`@OnEnabled`).

## Navigation & Management
- **Search**: Global search (Ctrl/Cmd+L) finds components by name, type, or property values; highlights results on canvas.
- **Breadcrumbs**: Jump between nested groups; “Operate Palette” offers quick navigation commands.
- **Operate Palette**: Provides summary view, bulletin board, provenance, controller service management, and reporting task control.

## Monitoring & Troubleshooting
- **Status History**: Right-click component → View Status History to graph metrics over time (FlowFiles in/out, bytes, task count).
- **Data Provenance**: Query lineage events, inspect content (if configured), replay FlowFiles, download event data for audit.
- **Counters**: Track processor-specific increments (e.g., items routed) and reset as needed.
- **Bulletin Board**: Centralizes warnings/errors with timestamps, component references, and node information.
- **Cluster View**: Displays node status (connected, disconnected, offload, remove) and allows coordinating actions.

## Versioning & Registry
- Integrates with NiFi Registry to save versions, compare diffs, revert, and promote flows across environments.
- Versioned process groups support change descriptions, parameter context binding, and flow snapshot download.

## Other Management Features
- **Accessing the UI**: Explains login sequence; if user lacks policy, UI prompts to request access from administrators.
- **Parameter Contexts**: Centralize environment-specific values; support sensitive parameters.
- **Queues & Prioritizers**: Configure FIFO, newest, oldest, attribute-driven, or custom prioritizers; backpressure thresholds stop upstream processors.
- **Experimental Features**: Flagged components/settings require caution; section lists current experimental capabilities and constraints.
- **Templates & Snippets**: Copy/paste across groups, use templates to bootstrap new flows.

## LLM Answering Tips
- When users ask “how do I add X?”, walk through toolbar → drag component → configure tabs (Settings, Scheduling, Properties) → apply → connect.
- For site-to-site questions, mention Remote Process Groups, enabling ports, and ensuring authorization on remote NiFi.
- For flow outages, suggest checking bulletins, queue sizes, processor validation errors, and status history metrics.
- Distinguish Start/Stop vs Enable/Disable vs Run Once when troubleshooting processor states.
- Mention execution engine choice when diagnosing queue persistence or stateless loss of data on restart.

## Cross-Doc Pointers
- **Administration Guide**: Provides the configuration and security groundwork that surfaces in UI authentication and restricted component policies.
- **Developer Guide**: Explains annotations and property metadata users see in configuration dialogs.
- **Expression Language Guide**: Many UI property editors support EL; reference syntax when helping with dynamic values.
- **NiFi In Depth**: Underpins queue persistence, provenance replay, and FlowFile concepts referenced throughout the UI guide.

## Anticipated FAQs
1. *Why can’t I start a processor?* → Check for invalid configuration (bulletin), missing relationships, or disabled controller services.
2. *How do I connect to another NiFi cluster?* → Add Remote Process Group, supply node URLs, configure Site-to-Site ports and security policies.
3. *How do I roll back a change?* → If version-controlled, open Version menu → Revert to previous snapshot; otherwise restore from template/backup.
4. *Where do I inspect data lineage?* → Use Operate Palette → Data Provenance; filter by component or attribute, replay if content still retained.
5. *What happens to data if NiFi restarts?* → Traditional engine queues persist; Stateless flows do not retain queued data—re-ingest from source.
