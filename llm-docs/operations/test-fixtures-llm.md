# Test Fixtures & Validation — LLM Notes

*Sources*: `nifi-docs/src/main/asciidoc/developer-guide.adoc` (Testing Components) and NiFi integration-testing patterns. Reviewed 2025-10-14.

## Testing Goals
- Ensure processors, controller services, and flows behave as expected before deploying to live NiFi instances.
- Provide deterministic sample data (fixtures) for regression and automation pipelines.
- Catch schema or configuration drift early in CI/CD.

## Unit Testing with `nifi-mock`
- Use `TestRunner` from `org.apache.nifi.util` to simulate NiFi runtime.
  - Instantiate via `TestRunners.newTestRunner(MyProcessor.class)`.
  - Configure processor properties and controller services programmatically.
  - Enqueue FlowFiles (`enqueue(byte[]|InputStream|Path, attributes)`), run (`run()` / `run(iterations)`), and assert transfers/attributes/content (`assertAllFlowFilesTransferred`, `getFlowFilesForRelationship`).
- `TestRunner` exposes utilities for:
  - Verifying provenance, state manager interactions, counters.
  - Testing multiple trigger invocations (`setThreadCount`, `run(iterations)`).
- For controller services, register via `runner.addControllerService(...)`, set properties, and enable with `runner.enableControllerService(...)`.

## Integration Testing Patterns
- **CLI/REST-driven**: spin up a NiFi instance (Docker, local install), deploy flow via REST or CLI, and validate via API queries.
- **End-to-End**: feed sample data into input ports or queues, wait for completion, and assert on output destinations (files, topics, DB rows).
- **Automation fixtures**:
  - YAML/JSON describing inputs, expected outputs, and environment prerequisites.
  - Scripts that orchestrate NiFi deployment, parameter context injection, and cleanup.
- Capture warnings/bulletins or invalid components post-deploy to fail tests early.

## Fixture Management
- Store sample FlowFiles (content + attributes) alongside flow modules (`tests/fixtures/{case}/`), including README describing purpose.
- Keep small, deterministic payloads to ensure quick tests and easy diffing.
- Document dependencies (mock services, temporary queues) so tests can be reproduced locally.

## CI/CD Tips
- Run unit tests (`mvn -Pcontrib-check` or `pytest` suites) on every commit.
- Gate integration tests behind environment variables/flags (e.g., `RUN_NIFI_INTEGRATION=1`) to avoid accidental live hits.
- Publish reports (JUnit XML, HTML) for assertion failures and bulletins.
- Lint fixtures/metadata to prevent drift (e.g., ensure every flow has matching test cases).

## Related Resources
- Flow metadata guidelines (`llm-docs/operations/metadata-and-docs-llm.md`).
- Controller services and parameters often require dedicated fixtures for configuration.
