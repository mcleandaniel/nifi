# NiFi Python API — LLM Notes

*Source*: `nifi-docs/src/main/asciidoc/python-developer-guide.adoc` (reviewed 2025-10-13)

## Purpose & Scope
- Enables authoring native Python processors that run inside Apache NiFi 2.x alongside Java extensions.
- Supplements the standard NiFi Developer Guide with Python-specific APIs, deployment guidance, and tooling notes.
- Python extensions currently cover processor-style components (`FlowFileTransform`, `RecordTransform`, `FlowFileSource`); controller services remain Java-only.

## Runtime Architecture
- NiFi (Java) talks to Python via local sockets using Py4J proxies. Every proxy call serializes the method invocation, so minimize round-trips when processing data.
- Java and Python processes run on localhost only; remote hosts cannot connect to the extension bridge, which preserves security boundaries.
- Java objects handed into Python are valid only for the duration of the call. Do **not** stash references (e.g., `self.process_context`); using them later raises `py4j.Py4JException: Target Object ID does not exist`.

## Processor APIs
- **FlowFileTransform**: operate on whole FlowFiles—return a `FlowFileTransformResult(relationship, contents=None, attributes=None)` with optional updated bytes/attributes.
- **RecordTransform**: iterate record-by-record (e.g., JSON/Avro) while the framework handles streaming/parsing.
- **FlowFileSource**: generate FlowFiles from external systems. `create(context)` returns `FlowFileSourceResult` or `None` (optionally call `context.yield_resources()` when idle).
- Each processor class must include two inner classes:
  - `class Java: implements = ['org.apache.nifi.python.processor.<Interface>']` to map the Py4J interface.
  - `class ProcessorDetails`: metadata (`version`, `description`, `tags`, optional `dependencies`).

## Working with FlowFiles
- `context` is a `nifiapi.properties.ProcessContext`; use `getName()`, `getProperties()`, and `getProperty(name)` to fetch configuration.
- `PythonPropertyValue` helpers: `.getValue()`, `.asInteger()`, `.asTimePeriod(TimeUnit)`, `.asControllerService()`, `.evaluateAttributeExpressions(flowfile)`.
- Input FlowFiles expose `getAttributes()`, `getAttribute(name)`, `getSize()`, `getContentsAsBytes()`, and `getContentsAsReader()` (prefer streaming readers to avoid double-buffering large payloads).

## Declaring Configuration
- Implement `getPropertyDescriptors(self)` to return a list of `PropertyDescriptor` objects (name, description, validators, default, required, controller service definition, etc.).
- Provide `getDynamicPropertyDescriptor(self, property_name)` when you want user-defined properties; otherwise NiFi marks the processor invalid if unknown properties appear.
- Reference Java controller services by setting `controller_service_definition='fully.qualified.Interface'` on a descriptor; obtain instances via `context.getProperty(...).asControllerService()`.
- Default relationships: FlowFile/Record transforms have `success`, `failure`, and framework-managed `original`; FlowFile sources expose `success`. Override `getRelationships()` to define custom outputs while keeping `failure/original` implicit.

## Logging, Lifecycle, and State
- Use the injected `self.logger` (available post-construction) so NiFi can surface messages as bulletins.
- Optional lifecycle hooks:
  - `onScheduled(context)`: initialize caches/clients once when the processor starts running.
  - `onStopped(context)`: tear down connections after all tasks finish.
- Access cluster or local state via `context.getStateManager()` and handle `StateException` for resilient error handling. State is expressed as Python dictionaries and supports `Scope.LOCAL`/`Scope.CLUSTER`.

## Built-in Documentation Decorators
- `@use_case(description, configuration, notes=None, keywords=None)` to advertise single-processor scenarios.
- `@multi_processor_use_case(description, configurations=[ProcessorConfiguration(...)], ...)` to document orchestrations involving multiple processors.
- These annotations enrich NiFi’s generated help and improve discoverability for LLM responses.

## Environment & Dependency Management
- Supported interpreters: Python 3.9, 3.10, 3.11, or 3.12 must be installed on the NiFi host.
- NiFi creates an isolated virtual environment per processor implementation/version under `$NIFI_HOME/work/python/extensions/<Processor>/<version>/`.
- Declare dependencies via one of:
  - `requirements.txt` inside a Python package directory (applied once per package).
  - `ProcessorDetails.dependencies = ['pandas', 'numpy==1.20.0']` for standalone modules.
- Air-gapped deployments can ship processors as NARs with dependencies pre-bundled under `NAR-INF/bundled-dependencies/`.

## Reloading, Deployment, and Layout
- NiFi hot-reloads Python source: edit the `.py` file, stop/start (or Run Once) the processor to pick up changes. If initial load failed, restart NiFi after fixing the code.
- Source layout options:
  - Drop single-file processors into `$NIFI_HOME/python/extensions` (configurable via `nifi.python.extensions.source.directory.*`).
  - For multi-module processors, create a subdirectory (package) so Python can import sibling modules.
  - Package as NAR and place in `lib/` for production distribution.

## Troubleshooting & Debugging
- Delete per-processor environments under `$NIFI_HOME/work/python/extensions/...` when dependency installations misbehave; NiFi will recreate them on next start.
- Remote debugging: use VSCode DebugPy (or similar) in listen mode, then connect from the processor code to the debugger; remember each concurrent task may spawn its own Python process.
- Common errors: object age-off (`Target Object ID does not exist`) indicates cached Java proxy reuse; dependency install failures logged during environment setup.

## LLM Answering Tips
- When users ask about Python processors failing to import modules, confirm Python version support and point to `ProcessorDetails.dependencies` or `requirements.txt` conventions.
- For performance questions, stress minimizing `getContentsAsBytes()` use, prefer streaming readers, and avoid repeated proxy calls inside tight loops.
- Troubleshooting reloads: remind to restart/Run Once after edits and to ensure the initial load succeeded; otherwise restart NiFi to re-discover the processor.
- Settings/location queries: cite `nifi.python.extensions.source.directory.<name>` and `nifi.python.working.directory` for customizing source/venv paths.
- Use-case documentation: encourage `@use_case`/`@multi_processor_use_case` to make processors self-describing in the NiFi UI and future LLM training corpora.

## Quick FAQs
1. **“How do I declare processor properties in Python?”** → Build `PropertyDescriptor` instances in `__init__`, return them via `getPropertyDescriptors`, and handle dynamic properties if needed.
2. **“Why does my processor lose access to context objects?”** → Java proxy objects expire after the method returns; fetch state within the scope of `transform/create` or persist only primitive data.
3. **“Can I call controller services?”** → Yes; reference the Java interface in a descriptor’s `controller_service_definition` and use `context.getProperty(...).asControllerService()`.
4. **“How do I bundle third-party libs?”** → Either include a `requirements.txt`, set `ProcessorDetails.dependencies`, or package as a NAR with `NAR-INF/bundled-dependencies`.
5. **“Where do I put my Python files in production?”** → Either ship a NAR to `lib/` or copy modules into configured `nifi.python.extensions.source.directory.*` paths; NiFi auto-discovers `.py` processors under those directories.
