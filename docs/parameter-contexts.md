# Understanding NiFi Parameter Contexts

Parameter Contexts are a fundamental feature in Apache NiFi for managing the configuration of dataflows. They provide a centralized way to define and manage key-value pairs, known as Parameters, that can be used throughout a NiFi flow. This allows for greater flexibility, easier environment promotion, and improved security.

## Core Concepts

### What is a Parameter?

A **Parameter** is a key-value pair consisting of:

-   **Name**: A unique identifier for the parameter within its context.
-   **Value**: The configuration value to be used.
-   **Sensitive Flag**: A boolean indicating whether the value is sensitive (e.g., a password or API key). Sensitive values are encrypted at rest and are not exposed in the UI after being set.
-   **Description**: An optional field to describe the parameter's purpose.

### What is a Parameter Context?

A **Parameter Context** is a named, globally-accessible collection of Parameters. Think of it as a configuration dictionary for your dataflow or a specific environment. You might have a `dev` context with connection details for development databases and a `prod` context with details for production systems.

### Binding to a Process Group

For any component (like a Processor or Controller Service) to use a Parameter, its parent **Process Group must be bound to a Parameter Context**.

-   Each Process Group can be bound to **exactly one** Parameter Context.
-   A single Parameter Context can be bound to **multiple** Process-Groups.
-   Child Process Groups inherit the Parameter Context of their parent unless explicitly overridden.
-   If you un-set a Parameter Context from a Process Group, it **does not** fall back to inheriting from its parent. Any components referencing parameters will become invalid.

### Inheritance

Parameter Contexts can inherit from one or more other contexts. This is useful for sharing common parameters.

-   The order of inherited contexts matters. If two inherited contexts have a parameter with the same name, the one from the context that is higher in the inheritance list takes precedence.
-   Parameters defined directly within a context always take precedence over any inherited parameters.

## Creating and Using Parameter Contexts

### 1. Creating a Parameter Context

1.  From the **Global Menu** (top-right), select **Parameter Contexts**.
2.  Click the `+` button to open the **Add Parameter Context** window.
3.  On the **Settings** tab, provide a unique **Name** and an optional **Description**.
4.  Switch to the **Parameters** tab and click `+` to add new parameters.
5.  For each parameter, define its **Name**, **Value**, **Sensitive** status, and **Description**.
6.  Click **Apply** to save the new context.

### 2. Assigning a Context to a Process Group

1.  Right-click on a Process Group and select **Configure**.
2.  In the **General** tab, use the **Parameter Context** dropdown to select the desired context.
3.  Click **Apply**.

### 3. Referencing a Parameter

Once a Process Group is bound to a context, you can reference parameters in any supported processor or controller service property within that group.

-   The syntax is `#{Parameter.Name}`.
-   The NiFi UI provides an auto-complete feature. In a supported property field, type `#{` and press `Ctrl+Space` to see a list of available parameters.
-   You can also create new parameters on-the-fly from a component's property configuration by clicking the "Convert to Parameter" icon.

**Important Notes:**

-   A sensitive property can only reference a sensitive Parameter.
-   A non-sensitive property can only reference a non-sensitive Parameter.
-   If a parameter is used within NiFi Expression Language (e.g., `${#{my-parameter}:toUpper()}`), the parameter is substituted *first*, and then the Expression Language is evaluated.

## Automation and the REST API

Parameter Contexts can be fully managed via the NiFi REST API, making them ideal for automated, CI/CD-driven workflows.

-   The base endpoint for all Parameter Context operations is `/nifi-api/parameter-contexts`.

### Example: Create a Parameter Context via `curl`

```bash
curl -X POST "http://localhost:8080/nifi-api/parameter-contexts" \
  -H 'Content-Type: application/json' \
  -d '{
    "revision": {"version": 0},
    "component": {
      "name": "api-created-context",
      "description": "Context for the API example",
      "parameters": [
        {"parameter": {"name": "hostname", "sensitive": false, "value": "api.example.com"}},
        {"parameter": {"name": "api.key", "sensitive": true,  "value": "super-secret-key"}}
      ]
    }
  }'
```

### Example: Assign a Context to a Process Group via `curl`

```bash
PG_ID="your-process-group-id"
PC_ID="your-parameter-context-id"

curl -X PUT "http://localhost:8080/nifi-api/process-groups/$PG_ID" \
  -H 'Content-Type: application/json' \
  -d '{
    "revision": {"version": 0},
    "component": {
      "id": "'"$PG_ID"'",
      "parameterContext": {"id": "'"$PC_ID"'"}
    }
  }'
```

## Environment Promotion and Versioning

Parameter Contexts are a cornerstone of promoting flows between environments (e.g., from development to testing to production).

-   When you version a Process Group in the NiFi Registry, the definition of the flow stores the *name* of the bound Parameter Context, but not its values.
-   When you import that versioned flow into a new NiFi instance, NiFi attempts to bind it to a Parameter Context with the same name.
-   If a context with that name exists, it is used. If not, a new, empty one is created.
-   Crucially, changing the parameters within a context **does not** mark a versioned Process Group as "locally modified." This allows you to have different parameter values in each environment while still tracking that the underlying flow is consistent with the version in the Registry.

## Governance and Best Practices

-   **Access Control**: Use NiFi's policies to control who can view or modify Parameter Contexts. Global policies control who can create them, and component-level policies can be set on each context for fine-grained read/write access.
-   **Logical Grouping**: Don't put all parameters into one giant context. Group them logically by service, dataflow, or function (e.g., `kafka-prod-cluster`, `sftp-customer-x`, `shared-database-logins`).
-   **Naming Conventions**: Adopt a clear naming convention for both contexts and parameters to avoid confusion and collisions.
-   **Parameter Providers**: For advanced use cases, explore **Parameter Providers**. These are extensions that can fetch parameters from external configuration systems like HashiCorp Vault, AWS Secrets Manager, or a database, and populate them into a NiFi Parameter Context.
