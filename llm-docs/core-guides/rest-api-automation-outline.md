# NiFi REST API Automation Outline — LLM Notes

This document expands the REST API option referenced in `programmatic-flow-generation.md`, detailing how to build a program that materializes a NiFi process group from scratch. It focuses on the creation path (no incremental updates) and assumes flows will be deleted and recreated when changes are needed.

## 1. Prerequisites & Setup
- **Target NiFi Version:** Document tested NiFi version (e.g., 2.0.x) because endpoints and DTOs can change.
- **Authentication:** Decide on mechanism (Bearer token via `/access/token`, mutual TLS, or proxied-entity headers). Store credentials securely.
- **HTTP Client:** Use a library that supports JSON serialization, TLS config, retry logic (e.g., OkHttp/Retrofit, Python requests, Go net/http with wrapper).
- **JSON Models:** Generate DTO classes from NiFi swagger or hand-craft lightweight representations for objects you POST/PUT (ProcessorDTO, ProcessorConfigDTO, ConnectionEntity, etc.).

## 2. High-Level Workflow
1. **Resolve Root IDs:** `GET /flow/process-groups/root` to fetch the root process group ID and existing context.
2. **Create Process Group:** `POST /process-groups/{parentId}/process-groups` with `ProcessGroupEntity` payload (name, position).
3. **Create Parameter Context (optional):**
   - `POST /parameter-contexts`
   - `PUT /process-groups/{id}/parameter-context`
4. **Provision Controller Services:**
   - `POST /process-groups/{id}/controller-services`
   - Configure via `PUT /controller-services/{id}`; enable once references are ready.
5. **Create Processors:** For each processor definition:
   - `POST /process-groups/{id}/processors`
   - `PUT /processors/{id}` with `component.config` update to set properties, scheduling strategy, concurrent tasks.
6. **Create Ports (if needed):** `POST /process-groups/{id}/input-ports` or `output-ports`.
7. **Create Connections:**
   - `POST /process-groups/{id}/connections` specifying source, destination, selected relationships, queue settings.
8. **Referencing Controller Services:** Update each processor’s config with controller service IDs (when available).
9. **Enable Controller Services:** `PUT /controller-services/{id}` with state = `ENABLED` after all dependencies linked.
10. **Start Components:**
    - `PUT /processors/{id}` with `component.state = RUNNING`
    - For group-level actions: `PUT /flow/process-groups/{id}` (`runStatus = RUNNING/STOPPED`, `maxConcurrentTasks`, etc.).
11. **Verification:** Optional `GET /flow/process-groups/{id}` to confirm component status, queue counts.

## 3. Detailed Payload Planning
- **Revision Handling:**
  - Every mutable call must include the latest `revision.version` for the entity. Use the revision returned from the previous response; NiFi increments after each successful change.
  - Consider a helper function to merge incoming revision info into outgoing payloads.
- **Positioning:** Processors/ports require `component.position` (x,y). Define deterministic layout (e.g., grid) to maintain consistent diagrams.
- **Relationships:** When creating connections, specify selected relationships; retrieve available relationships from processor DTOs (`component.relationships`) if dynamic.
- **Properties:** For complex properties (JSON, lists), ensure correct serialization and use parameter references where appropriate.

## 4. Program Structure Suggestions
- **Definition Schema:** Keep a declarative definition (YAML/JSON) describing processors, services, connections, parameters. Example:
  ```yaml
  processGroup:
    name: TrivialFlow
    parameterContext: null
    processors:
      - id: generate
        type: org.apache.nifi.processors.standard.GenerateFlowFile
        position: [0,0]
        properties:
          GenerateFlowFile.BatchSize: "1"
        scheduling:
          strategy: TIMER_DRIVEN
          period: "0 sec"
      - id: log
        type: org.apache.nifi.processors.standard.LogAttribute
        position: [400,0]
    connections:
      - source: generate
        relationship: success
        destination: log
  ```
- **Builder Pattern:** Translate the definition into API calls through a builder module that resolves references, ensures creation order, and captures IDs.
- **Error Handling:** If a step fails, log the NiFi response (status, body). Provide teardown logic (`DELETE /process-groups/{id}?recursive=true`) to clean partial deployments.
- **Idempotency:** For destructive recreate-mode, always delete target group before creating (`GET` to check existence, then `DELETE`).

## 5. Endpoint Reference Cheat Sheet
| Operation | Endpoint | Notes |
|-----------|----------|-------|
| Get root PG | `GET /flow/process-groups/{id}` | `/root` for overall summary, `/process-groups/{id}` for details |
| Create PG | `POST /process-groups/{id}/process-groups` | parent ID = target group |
| Create processor | `POST /process-groups/{id}/processors` | Body includes type (bundle info) |
| Update processor config | `PUT /processors/{id}` | `component.config` block |
| Create connection | `POST /process-groups/{id}/connections` | Need source/destination DTOs |
| Create controller service | `POST /process-groups/{id}/controller-services` | Type + bundle |
| Enable controller service | `PUT /controller-services/{id}` | `component.state = ENABLED` |
| Update PG run status | `PUT /flow/process-groups/{id}` | Change run status for components |
| Delete PG | `DELETE /process-groups/{id}?version=X&clientId=...` | Include revision |

## 6. Testing Strategy
- **Unit Tests:** Mock HTTP client to ensure payloads are assembled correctly.
- **Integration Tests:** Run against disposable NiFi instance (dockerized). Sequence: create → verify component status via `/flow/process-groups/{id}` → delete.
- **Assertions:** Check processors in `RUNNING` state, queue sizes (expected zero), controller services `ENABLED`.
- **Teardown:** Clean external resources (files, mock endpoints) after each run.

## 7. Future Enhancements
- Add update/diff logic for incremental changes (requires comparing definitions with live state).
- Generate NiFi versioned snapshots after creation for auditing.
- Support nested process groups by recursion on the definition schema.
- Integrate with CI/CD pipelines (trigger recreation on commit).

Use this outline as a blueprint for implementing and refining the REST API automation path before committing to alternative strategies.
