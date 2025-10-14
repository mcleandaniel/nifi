# Test Fixtures & Validation — LLM Notes

*Sources*: `nifi-docs/src/main/asciidoc/developer-guide.adoc` (Testing Components) and NiFi integration-testing patterns. Reviewed 2025-10-14. [1]

## Testing Goals
- Ensure processors, controller services, and flows behave as expected before deploying to live NiFi instances. [?1]
- Provide deterministic sample data (fixtures) for regression and automation pipelines. [?2]
- Catch schema or configuration drift early in CI/CD. [?3]

## Unit Testing with `nifi-mock`
- Use `TestRunner` from `org.apache.nifi.util` to simulate NiFi runtime. [2]
  - Instantiate via `TestRunners.newTestRunner(MyProcessor.class)`. [3]
  - Configure processor properties and controller services programmatically. [4]
  - Enqueue FlowFiles (`enqueue(byte[]|InputStream|Path, attributes)`), run (`run()` / `run(iterations)`), and assert transfers/attributes/content (`assertAllFlowFilesTransferred`, `getFlowFilesForRelationship`). [4]
- `TestRunner` exposes utilities for:
  - Verifying provenance, state manager interactions, counters. [4]
  - Testing multiple trigger invocations (`setThreadCount`, `run(iterations)`). [4]
- For controller services, register via `runner.addControllerService(...)`, set properties, and enable with `runner.enableControllerService(...)`. [5]

## Integration Testing Patterns
- **CLI/REST-driven**: spin up a NiFi instance (Docker, local install), deploy flow via REST or CLI, and validate via API queries. [?4]
- **End-to-End**: feed sample data into input ports or queues, wait for completion, and assert on output destinations (files, topics, DB rows). [?5]
- **Automation fixtures**:
  - YAML/JSON describing inputs, expected outputs, and environment prerequisites. [?6]
  - Scripts that orchestrate NiFi deployment, parameter context injection, and cleanup. [?7]
- Capture warnings/bulletins or invalid components post-deploy to fail tests early. [?8]

## Fixture Management
- Store sample FlowFiles (content + attributes) alongside flow modules (`tests/fixtures/{case}/`), including README describing purpose. [?9]
- Keep small, deterministic payloads to ensure quick tests and easy diffing. [?10]
- Document dependencies (mock services, temporary queues) so tests can be reproduced locally. [?11]

## CI/CD Tips
- Run unit tests (`mvn -Pcontrib-check` or `pytest` suites) on every commit. [6]
- Gate integration tests behind environment variables/flags (e.g., `RUN_NIFI_INTEGRATION=1`) to avoid accidental live hits. [?12]
- Publish reports (JUnit XML, HTML) for assertion failures and bulletins. [6]
- Lint fixtures/metadata to prevent drift (e.g., ensure every flow has matching test cases). [?13]

## Related Resources
- Flow metadata guidelines (`llm-docs/operations/metadata-and-docs-llm.md`).
- Controller services and parameters often require dedicated fixtures for configuration.

---
## References
[1] `nifi-docs/src/main/asciidoc/developer-guide.adoc`
[2] `nifi-mock/src/main/java/org/apache/nifi/util/TestRunner.java`
[3] `nifi-mock/src/main/java/org/apache/nifi/util/TestRunners.java`
[4] `nifi-mock/src/main/java/org/apache/nifi/util/TestRunner.java` and various test files.
[5] `nifi-mock/src/main/java/org/apache/nifi/util/TestRunner.java` and various test files.
[6] `pom.xml`

## Claims without references
[?1] General testing best practice.
[?2] General testing best practice.
[?3] General testing best practice.
[?4] General integration testing pattern.
[?5] General integration testing pattern.
[?6] General integration testing pattern.
[?7] General integration testing pattern.
[?8] General testing best practice.
[?9] Project convention.
[?10] General testing best practice.
[?11] General testing best practice.
[?12] Common CI/CD practice.
[?13] General testing best practice.
