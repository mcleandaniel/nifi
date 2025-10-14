# NiFi Flows & Process Groups — LLM Notes

*Sources*: `nifi-docs/src/main/asciidoc/user-guide.adoc` (Process Groups, Versioned Flows) and `nifi-docs/src/main/asciidoc/programming-model.adoc` coverage, reviewed 2025-10-14.

## Purpose
- Organize related processors, ports, and connections into manageable units.
- Provide logical scoping for controller services, parameter contexts, and access policies.
- Support reuse by exporting/importing versioned flows via NiFi Registry or automation.

## Process Group Basics
- **Root Process Group**: top-level canvas created at install; all flows live under it.
- **Nested Groups**: act like subflows; contain their own components, controller services, and parameter context binding.
- **Ports**:
  - *Input/Output ports* (internal) connect components within the same NiFi instance.
  - *Remote ports* (on remote process groups) enable site-to-site communication.
- **Scope of resources**:
  - Controller services defined on a group apply to that group and descendants.
  - Parameter contexts are bound per process group; child groups inherit binding unless explicitly changed.
- **Version Control**: registering a process group with NiFi Registry captures its flow definition (components, controller services, parameter bindings, templates).
- **Execution Modes**: Traditional (default) vs Stateless; the entire group adopts the selected engine.

## Group Configuration Highlights
- *General tab*: name, comments, default flow-file expiration, backpressure defaults, execution engine, stateless timeout, and scheduling.
- *Controller Services tab*: define services scoped to the group tree.
- *Parameter Context*: choose which context is bound; optionally create new ones from the config dialog.
- *Access Policies*: apply multi-tenant permissions at group level, restricting who can view/modify components.

## Flow Assembly Patterns
- **Horizontal flows**: root contains high-level groups (ingest, enrich, publish) for clarity.
- **Nested subflows**: encapsulate reusable logic; reference them via process group instantiation.
- **Remote process groups**: connect to external NiFi instances using site-to-site.
- **Versioned bundles**: commit flows to Registry for promotion across environments.
- **Automation**: flows can be described declaratively (YAML/JSON) and deployed via REST or CLI; ensure top-level group hierarchy mirrors run-time expectations.

## Best Practices
- Keep component count per group reasonable; nest when complexity grows.
- Name groups with deployment context (`ingest/customer/normalize`) to ease automation.
- Store README or metadata alongside flow definitions to document purpose, dependencies, and parameters.
- Validate flows (no invalid processors, no unconnected relationships) before exporting/versioning.
- Use “download” or CLI exports to snapshot for auditing.

## Related Artefacts
- Controller services (`llm-docs/dataflow/controller-services-llm.md`)
- Parameter contexts (`llm-docs/dataflow/parameter-contexts-llm.md`)
- Reusable subflows/templates (`llm-docs/dataflow/subflows-and-templates-llm.md`)
