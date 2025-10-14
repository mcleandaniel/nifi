# NiFi Parameter Contexts — LLM Notes

*Sources*: `nifi-docs/src/main/asciidoc/user-guide.adoc` (Parameter Contexts section) and NiFi multi-tenant documentation. Reviewed 2025-10-14.

## Purpose
- Centralize configurable values (strings, numbers, sensitive credentials) used across processors, controller services, or reporting tasks.
- Simplify environment promotion (dev/test/prod) by binding different contexts to the same flow.
- Support multi-tenant governance—control who can view or edit specific parameters.

## Key Concepts
- **Parameter**: key/value pair with optional description and sensitivity flag. Sensitive parameters are encrypted at rest and masked in UI/logs.
- **Parameter Context**: named collection of parameters, globally accessible. Defined via Global Menu → *Parameter Contexts*.
- **Binding**: each process group can bind to a single parameter context. Child groups inherit the parent binding unless overridden.
- **Parameter Providers**: optional extensions that fetch parameters from external systems (e.g., Vault, Consul) and apply them to contexts.
- **Access Control**: policies exist for creating contexts and for read/write access per context; required for multi-tenant NiFi deployments.

## Lifecycle
1. **Create**: use *Parameter Contexts* dialog → `+` button. Configure name/description (Settings tab) and add parameters (Parameters tab).
2. **Assign**: open a process group’s configuration (Operate Palette or right-click → Configure) and select the context from the drop-down.
3. **Reference**: use Expression Language syntax `${param:your-parameter}` within supported component properties. NiFi resolves values at runtime based on the group’s bound context.
4. **Update**:
   - Modify parameters in the context dialog.
   - Apply changes → NiFi verifies referencing components, disabling/enabling as needed to propagate new values.
5. **Promote**: export/import contexts via REST/CLI or maintain them as declarative YAML/JSON to align with automation pipelines.

## Guidelines & Tips
- Group parameters logically (e.g., `customer-etl`, `sftp-prod`) to reduce multi-flow coupling.
- Use consistent naming conventions (prefix or domain) to avoid collisions and improve readability.
- Prefer parameters for values likely to change between environments (endpoints, credentials, file paths).
- Sensitive parameters cannot be viewed once set; keep metadata describing their purpose in documentation.
- Watch for properties that *cannot* reference parameters (certain controller services or reporting tasks); NiFi warns in the UI.
- When using parameter providers, schedule fetch/apply operations and monitor for drift between source and NiFi context.

## Automation Considerations
- Store context definitions alongside flow specs (one file per context or per environment).
- Automation should validate that required parameters exist before deploying flows.
- Provide tooling to diff contexts across environments to catch unexpected divergence.

## Related Resources
- Controller services often rely on parameters for credentials (`llm-docs/dataflow/controller-services-llm.md`).
- Flows and process groups select contexts (`llm-docs/dataflow/flows-and-process-groups-llm.md`).
