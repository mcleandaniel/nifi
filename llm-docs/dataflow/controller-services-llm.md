# NiFi Controller Services — LLM Notes

*Primary sources*: `nifi-docs/src/main/asciidoc/user-guide.adoc` (Controller Services section) and `nifi-docs/src/main/asciidoc/developer-guide.adoc` (ControllerService API details). Content reviewed 2025-10-14.

## Purpose
- Provide shared, reusable configuration or runtime state (e.g., SSL contexts, database pools, lookup tables) to processors, reporting tasks, parameter providers, and other controller services.
- Allow operators to configure sensitive or verbose settings once and reference them from many components, improving consistency and maintenance.

## Core Concepts & Scope
- **Controller-level vs. dataflow-level**:
  - *Controller (global) services* live under *Controller Settings → Management Controller Services* and can be used by controller-scope components (reporting tasks, flow analysis rules, other controller services).
-  - *Process-group services* are configured on the Controller Services tab of a process group (root or nested) and are available only within that group hierarchy.
- **Hierarchy visibility**:
  - Adding a service at the **root process group** makes it visible to all nested groups and the processors within them.
  - Adding a service at a **child process group** scopes it to that group and its descendants only; parent or sibling groups cannot reference it.
  - This cascading visibility mirrors the process-group tree, so plan service placement according to reuse needs (global vs localized configuration).
- **Lifecycle**:
  - Created in *Disabled* state → configure properties → *Enable* (optionally enable all referencing components).
  - To edit, disable the service (NiFi offers to disable referencing components automatically), adjust properties, then re-enable.
- **Security & access**:
  - Visibility and edit permissions depend on multi-tenant policies. Users without access cannot see or reference a service.
- **Bulletins**:
  - Each service has a configurable bulletin level (default WARN); violations or runtime issues surface in the UI.

## Configuration Workflow (UI)
1. Open the *Controller Services* tab at the applicable scope (controller settings or process group).
2. Click the `+` button to open the **Add Controller Service** dialog (supports tag filtering and bundle/vendor filtering).
3. Select a service type, add it, and use the **Configure** button to open settings/properties/comments.
4. Apply changes, then click **Enable**. During enable, NiFi prompts to also enable/start referencing components.
5. Once enabled, processors can reference the service via property descriptors that declare `identifiesControllerService(...)`.

### Referencing from processors and other components
- Properties that reference controller services display a picker; if no suitable service exists, DFMs can create one in-place.
- Services are resolved by interface (e.g., `DBCPService`, `SSLContextService`). Multiple implementations may satisfy the same interface.
- If a referencing service is disabled, dependent processors become *Invalid* until the service is enabled.

## Developer Notes
- A controller service is defined as an interface extending `ControllerService`; implementations reside in NiFi Archives (NARs).
- Processors interact with services via the interface to keep classloader isolation between NARs.
- Property descriptors flag dependencies with `.identifiesControllerService(MyServiceInterface.class)`. NiFi injects the selected service at runtime.
- Services share the same initialization/validation lifecycle as processors but have no `onTrigger` and no relationships—they are not scheduled components.
- Services can themselves reference other services (e.g., a lookup service using a DBCP service).

## Operational Tips & Troubleshooting
- **Invalid processors**: If a processor shows “Controller Service is disabled/unconfigured,” enable or configure the referenced service.
- **Scope awareness**: Define services at the lowest scope needed—global scope for cross-flow reuse, process group scope for flow-specific configuration.
- **Change management**: Disabling a service to edit it can cascade; use the disable dialog to pause referencing components automatically, then re-enable everything together.
- **Common examples**:
  - `StandardSSLContextService` for TLS client/server configuration.
  - `DBCPConnectionPool` for database access.
  - Lookup services (Properties file, CSV, DistributedMapCache) for enrichment processors like `LookupAttribute`.
- **Versioning**: NiFi Registry snapshots capture controller-service definitions and property values; sensitive properties remain protected.

## Quick FAQ
1. **Why is my processor invalid after deployment?**  
   Usually the referenced controller service is disabled or missing. Enable it or ensure the correct interface/type is provided.
2. **Can one service be reused by multiple process groups?**  
   Yes—define it at the root process-group level (or controller level for management services) so descendants inherit it.
3. **How do I update a service without downtime?**  
   Disable the service (NiFi prompts to disable dependents), change properties, then re-enable; consider redundant flows for zero-downtime.
4. **Can services depend on other services?**  
   Yes; property descriptors inside a controller service can reference another service interface. NiFi manages the dependency graph during enable/disable.
5. **Do services support parameters or expression language?**  
   Some do, but note the user guide restrictions: parameters aren’t available in management-level services, and certain properties may block EL usage—check each descriptor.

## Cross-Doc Pointers
- *User Guide* → Controller Services (creation, enabling, scope) and Controller Settings UI walkthrough.
- *Developer Guide* → ControllerService API, lifecycle, best practices for implementing and referencing services.
- *Processors Guide* → highlights processors requiring services (e.g., database, lookup, SSL).

Use this reference when answering LLM queries about controller services: scope, lifecycle, UI actions, and development patterns are the most frequent points of confusion.
