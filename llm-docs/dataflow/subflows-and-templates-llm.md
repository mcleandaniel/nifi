# NiFi Subflows & Templates — LLM Notes

*Sources*: NiFi user guide (process groups, versioned flows, template import/export) and NiFi Registry docs, reviewed 2025-10-14. [1]

## Purpose
- Encapsulate reusable chunks of logic so they can be assembled into larger flows. [?1]
- Promote consistency and reuse across teams/projects. [?2]
- Support modular automation where subflows are versioned and imported programmatically. [?3]

## Terminology
- **Process Group (subflow)**: nested group used as a building block. Encouraged over legacy templates for NiFi 1.10+ because they work naturally with versioned flows. [2]
- **Versioned Flow**: process group tracked in NiFi Registry; can be pulled into other environments or groups. [3]
- **Template (legacy XML)**: static snapshot of components/positions. Still supported but superseded by Registry flows. [4]
- **Snippet**: ad-hoc copy/paste selection on the canvas; useful for quick reuse but not a packaging format. [?4]

## Reuse Strategies
1. **Versioned Subflows (Recommended)**
   - Develop a process group locally.
   - Register it with NiFi Registry (assign bucket/flow).
   - Other flows import/change version via the UI or CLI (`nifi pg-change-version`).
   - Supports diffing, comments, and promotion pipelines. [3]
2. **Library Process Groups**
   - Maintain a catalog of reusable groups in a dedicated area of the canvas or automation repo.
   - Automation references them by ID/name and instantiates within parent flows. [?5]
3. **Legacy Templates**
   - Export via *Operate Palette → Download Flow* (creates XML). [4]
   - Import via *Operate Palette → Upload Template*. [4]
   - Useful when Registry unavailable, but lacks version history and parameter context binding. [4]

## Best Practices
- Design subflows with clear input/output ports; treat them like functions with defined contracts. [?6]
- Minimize hard-coded properties—use parameters or controller services passed from the parent. [?7]
- Document dependencies (required services, parameters) in README metadata. [?8]
- Use naming conventions (`lib-`, `common-`) to distinguish reusable groups from flow-specific ones. [?9]
- When leveraging Registry, adopt semantic versioning and descriptive change comments. [?10]
- Test subflows independently where possible (unit tests with `nifi-mock`, integration tests in isolated PGs). [5]

## Automation Considerations
- Store reusable subflow specs separately (e.g., `shared/subflows/`), including their metadata and registry coordinates. [?11]
- Provide scripts/CLI to sync subflow libraries to target environments. [?12]
- Validate that parent flows use compatible versions before deployment. [?13]

## Related Docs
- Flow/Process Group overview (`llm-docs/dataflow/flows-and-process-groups-llm.md`).
- Controller services & parameters (often consumed by subflows).

---
## References
[1] `nifi-docs/src/main/asciidoc/user-guide.adoc`, `nifi-registry/nifi-registry-core/nifi-registry-docs/src/main/asciidoc/user-guide.adoc`
[2] `nifi-docs/src/main/asciidoc/user-guide.adoc`
[3] `nifi-docs/src/main/asciidoc/user-guide.adoc#versioning_dataflow`
[4] `nifi-docs/src/main/asciidoc/user-guide.adoc`
[5] `nifi-mock/src/main/java/org/apache/nifi/util/TestRunner.java`

## Claims without references
[?1] General software development best practice.
[?2] General software development best practice.
[?3] General software development best practice.
[?4] UI feature.
[?5] Design pattern.
[?6] General software development best practice.
[?7] General software development best practice.
[?8] General software development best practice.
[?9] General software development best practice.
[?10] General software development best practice.
[?11] General software development best practice.
[?12] General software development best practice.
[?13] General software development best practice.
