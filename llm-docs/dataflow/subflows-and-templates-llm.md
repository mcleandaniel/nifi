# NiFi Subflows & Templates — LLM Notes

*Sources*: NiFi user guide (process groups, versioned flows, template import/export) and NiFi Registry docs, reviewed 2025-10-14.

## Purpose
- Encapsulate reusable chunks of logic so they can be assembled into larger flows.
- Promote consistency and reuse across teams/projects.
- Support modular automation where subflows are versioned and imported programmatically.

## Terminology
- **Process Group (subflow)**: nested group used as a building block. Encouraged over legacy templates for NiFi 1.10+ because they work naturally with versioned flows.
- **Versioned Flow**: process group tracked in NiFi Registry; can be pulled into other environments or groups.
- **Template (legacy XML)**: static snapshot of components/positions. Still supported but superseded by Registry flows.
- **Snippet**: ad-hoc copy/paste selection on the canvas; useful for quick reuse but not a packaging format.

## Reuse Strategies
1. **Versioned Subflows (Recommended)**
   - Develop a process group locally.
   - Register it with NiFi Registry (assign bucket/flow).
   - Other flows import/change version via the UI or CLI (`nifi pg-change-version`).
   - Supports diffing, comments, and promotion pipelines.
2. **Library Process Groups**
   - Maintain a catalog of reusable groups in a dedicated area of the canvas or automation repo.
   - Automation references them by ID/name and instantiates within parent flows.
3. **Legacy Templates**
   - Export via *Operate Palette → Download Flow* (creates XML).
   - Import via *Operate Palette → Upload Template*.
   - Useful when Registry unavailable, but lacks version history and parameter context binding.

## Best Practices
- Design subflows with clear input/output ports; treat them like functions with defined contracts.
- Minimize hard-coded properties—use parameters or controller services passed from the parent.
- Document dependencies (required services, parameters) in README metadata.
- Use naming conventions (`lib-`, `common-`) to distinguish reusable groups from flow-specific ones.
- When leveraging Registry, adopt semantic versioning and descriptive change comments.
- Test subflows independently where possible (unit tests with `nifi-mock`, integration tests in isolated PGs).

## Automation Considerations
- Store reusable subflow specs separately (e.g., `shared/subflows/`), including their metadata and registry coordinates.
- Provide scripts/CLI to sync subflow libraries to target environments.
- Validate that parent flows use compatible versions before deployment.

## Related Docs
- Flow/Process Group overview (`llm-docs/dataflow/flows-and-process-groups-llm.md`).
- Controller services & parameters (often consumed by subflows).
