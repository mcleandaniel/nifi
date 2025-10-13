# NiFi Developer Guide — LLM Notes

*Source*: `nifi-docs/src/main/asciidoc/developer-guide.adoc` (reviewed 2025-10-13)

## Purpose
- Deep dive for extension authors (Processors, Controller Services, Reporting Tasks, Parameter Providers, UI extensions).
- Documents APIs, lifecycle annotations, state handling, provenance, packaging, and contribution workflow.

## Section Highlights
- **NiFi Components**: Defines the core extension points (Processors manipulate FlowFiles, Controller Services supply shared resources, Reporting Tasks emit metrics/events, Parameter Providers populate parameter contexts).
- **Processor API**: Encourages extending `AbstractProcessor`; explains ServiceLoader requirements (`META-INF/services/org.apache.nifi.processor.Processor` listing).
- **Supporting API**: Key classes include `FlowFile`, `ProcessSession`, `ProcessContext`, `Relationship`, `PropertyDescriptor`, `ProvenanceReporter`, `ComponentLog`.
- **AbstractProcessor Utilities**: Thread-safety expectations, scheduling, property/relationship declarations, annotation-based metadata.
- **Component Lifecycle Annotations**: `@OnAdded`, `@OnEnabled`, `@OnScheduled`, `@OnUnscheduled`, `@OnStopped`, `@OnRemoved`, `@OnShutdown`, `@OnPrimaryNodeStateChange` inform framework callbacks.
- **Component Notification**: Use `ComponentLog`, bulletins, Yield/penalization APIs, and `ReportingInitializationContext`.
- **Restricted Components**: Apply `@Restricted` to guard privileged operations; admins must grant per-restriction access.
- **State Manager**: `StateManager` API stores `Map<String,String>` either `Scope.LOCAL` (per node) or `Scope.CLUSTER` (ZooKeeper-backed, <1 MB total).
- **Reporting Processor Activity**: Emit provenance events via `ProvenanceReporter` (fork/join, send/receive) and bulletins for operator visibility.
- **Documentation Annotations**: `@Tags`, `@CapabilityDescription`, `@WritesAttributes`, `@ReadsAttributes`, `@DynamicProperty`, `@DynamicRelationship` describe components for UI and generated docs.
- **Provenance Events & Patterns**: Guidance for reporting `SEND`, `RECEIVE`, `FORK`, `JOIN`, `ROUTE`, `DROP` events consistently.
- **Common Processor Patterns**: Content claim management, streaming best practices, session rollback scenarios, penalization, relationships for success/failure.
- **Error Handling**: Use `ProcessSession.rollback()` with `yield`, `penalize`, and `rollback(true)` for retries; differentiate transient vs permanent failures.
- **Controller Services & Reporting Tasks**: Lifecycle, configuration, capability descriptions, dependency injection for external resources.
- **UI Extensions**: React/JS toolkit usage, packaging watchers, handshake with NiFi UI (web content).
- **Testing**: `nifi-mock` module (`TestRunner`, `TestRunners.newTestRunner`) for unit testing processors/services; methods to enqueue FlowFiles, assert transfers, verify provenance.
- **NiFi Archives (NARs)**: Package extensions with `nar` packaging, `nifi-nar-maven-plugin`, classloader isolation, dependency scoping.
- **Per-Instance ClassLoading**: Explains component-level classloaders, context classloading, and isolation boundaries.
- **Deprecation Workflow**: `@DeprecationNotice` usage, documenting alternatives, migration expectations.
- **Build Options and Contribution**: Maven modules, `mvn -Pcontrib-check`, CLA/ICLA, pull request expectations.

## Extension Development Checklist
- Create a module with `nar` packaging that depends on one or more processor/service modules; include ServiceLoader entries.
- Extend `AbstractProcessor` or relevant base; declare static `REL_SUCCESS`/`REL_FAILURE`, property descriptors in `init`.
- Use `onTrigger(ProcessContext, ProcessSession)` with streaming, try-with-resources, and minimal heap usage.
- Emit provenance events to reflect external IO (`provenanceReporter.receive`, `send`, `route`), especially when creating/dropping FlowFiles.
- Mark privileged components with `@Restricted` and supply justification string; document dynamic props/relationships when applicable.
- Provide meaningful default scheduling (Primary vs All Nodes), run duration hints, and back pressure considerations.
- Populate `@Tags`, `@CapabilityDescription`, `@WritesAttributes`, `@ReadsAttributes` for searchable catalog and toolkits.
- Validate property values via `PropertyDescriptor.Builder().addValidator()`; use `StandardValidators` where possible; mark `sensitive(true)` when storing secrets.
- Handle state through `StateManager` only for small maps; fetch with `getState(scope)`, update via `setState`/`replace` atomically.

## Testing & QA Notes
- Add dependency on `org.apache.nifi:nifi-mock` to leverage `TestRunner`.
- `TestRunner.enqueue()` supports byte arrays, streams, paths, or FlowFiles with attribute maps.
- `run(int iterations)` will invoke lifecycle annotations; `assertTransferCount`, `getFlowFilesForRelationship` verify outputs.
- Mock external systems by subclassing processor in test and overriding protected client factory methods.
- Use `TestRunner.clearTransferState()` when running multiple sequential test phases.

## Packaging & Deployment Reminders
- Each NAR should include only compatible dependency versions to avoid classloader conflicts; prefer shading when necessary.
- Declare additional resources (schemas, scripts) inside NAR under `src/main/resources`; mark with `@RequiresInstanceClassLoading` if runtime isolation needed.
- Controller Services shared across modules should live in dedicated NARs to avoid duplication.

## LLM Answering Tips
- When asked “how do I build a processor that X?”, check Processor API, lifecycle, and common patterns sections above.
- Questions about annotations: map to `org.apache.nifi.annotation.*` packages (lifecycle, capability, restriction, bulletins).
- For stateful designs, mention `StateManager` limits (<=1 MB, ZooKeeper cluster scope) and fallback to external DB for larger datasets.
- For provenance discrepancies, advise on reporting via `ProvenanceReporter` methods in `ProcessSession`.
- For testing guidance, cite `nifi-mock` usage and mention verifying relationships/bulletins.

## Cross-Doc Pointers
- **Administration Guide**: Aligns with Restricted component governance and state provider configuration referenced here.
- **Expression Language Guide**: Use when documenting property expression support; many property descriptors reference EL evaluation capabilities.
- **User Guide**: Shows how documented tags/capabilities appear in UI, especially for restricted components and bulletins.
- **NiFi In Depth**: Background on repositories helps explain provenance and FlowFile behavior described in processor patterns.

## Anticipated FAQs
1. *Why is my processor not discoverable?* → Confirm ServiceLoader entry in `META-INF/services/org.apache.nifi.processor.Processor` and proper `@Tags`/`@CapabilityDescription` usage.
2. *How do I schedule setup/cleanup logic?* → Use lifecycle annotations (`@OnScheduled`, `@OnStopped`, etc.) and be mindful of thread-safety.
3. *How can I store rolling offsets or checkpoint information?* → `StateManager` with `Scope.CLUSTER` for shared offsets; keep map small and update via `replace` for atomic writes.
4. *What’s the right way to test external services?* → Use `TestRunner` plus mocked clients; avoid hitting live endpoints in unit tests.
5. *How do I package multiple processors that share libraries?* → Put them in a single NAR or multiple NARs with shared dependencies, leveraging classloader isolation and the NAR Maven plugin.
