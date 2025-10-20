---
title: NiFi Stateless Engine Strategy
description: Deployment and orchestration guidance for running Apache NiFi flows with the stateless execution engine in serverless environments.
claims:
  claim-stateless-engine-overview:
    sources:
      - source-user-guide-stateless-overview
  claim-stateless-data-loss:
    sources:
      - source-user-guide-stateless-overview
  claim-stateless-replay-sources:
    sources:
      - source-stateless-readme-overview
  claim-stateless-interface:
    sources:
      - source-stateless-api-interface
  claim-runstateless-cli:
    sources:
      - source-runstateless
  claim-bootstrap-nar:
    sources:
      - source-stateless-bootstrap-unpack
  claim-engine-components:
    sources:
      - source-stateless-engine-factory
  claim-engine-files:
    sources:
      - source-stateless-readme-running
  claim-engine-dirs:
    sources:
      - source-stateless-readme-running
  claim-extension-clients:
    sources:
      - source-stateless-readme-extensions
  claim-dataflow-sourcing:
    sources:
      - source-stateless-readme-dataflow
  claim-parameter-context:
    sources:
      - source-stateless-readme-dataflow
  claim-transaction-thresholds:
    sources:
      - source-stateless-readme-thresholds
  claim-failure-port-config:
    sources:
      - source-stateless-readme-failure-ports
  claim-parameter-overrides-cli:
    sources:
      - source-stateless-readme-pass-parameters
  claim-parameter-providers:
    sources:
      - source-stateless-readme-pass-parameters
  claim-single-source:
    sources:
      - source-stateless-readme-overview
  claim-merging-limits:
    sources:
      - source-stateless-readme-overview
  claim-failure-handling:
    sources:
      - source-stateless-readme-overview
  claim-concurrency-caution:
    sources:
      - source-user-guide-stateless-overview
  claim-validation:
    sources:
      - source-runstateless
sources:
  source-user-guide-stateless-overview:
    title: "Apache NiFi User Guide"
    path: "nifi-docs/src/main/asciidoc/user-guide.adoc"
    locator: "L1649-L1699"
    accessed: 2024-07-04
  source-stateless-readme-overview:
    title: "Stateless NiFi Assembly README"
    path: "nifi-stateless/nifi-stateless-assembly/README.md"
    locator: "L58-L135"
    accessed: 2024-07-04
  source-stateless-readme-running:
    title: "Stateless NiFi Assembly README"
    path: "nifi-stateless/nifi-stateless-assembly/README.md"
    locator: "L170-L199"
    accessed: 2024-07-04
  source-stateless-readme-extensions:
    title: "Stateless NiFi Assembly README"
    path: "nifi-stateless/nifi-stateless-assembly/README.md"
    locator: "L221-L244"
    accessed: 2024-07-04
  source-stateless-readme-dataflow:
    title: "Stateless NiFi Assembly README"
    path: "nifi-stateless/nifi-stateless-assembly/README.md"
    locator: "L288-L320"
    accessed: 2024-07-04
  source-stateless-readme-thresholds:
    title: "Stateless NiFi Assembly README"
    path: "nifi-stateless/nifi-stateless-assembly/README.md"
    locator: "L329-L351"
    accessed: 2024-07-04
  source-stateless-readme-failure-ports:
    title: "Stateless NiFi Assembly README"
    path: "nifi-stateless/nifi-stateless-assembly/README.md"
    locator: "L355-L394"
    accessed: 2024-07-04
  source-stateless-readme-pass-parameters:
    title: "Stateless NiFi Assembly README"
    path: "nifi-stateless/nifi-stateless-assembly/README.md"
    locator: "L442-L502"
    accessed: 2024-07-04
  source-runstateless:
    title: "RunStatelessFlow Launcher"
    path: "nifi-stateless/nifi-stateless-bootstrap/src/main/java/org/apache/nifi/stateless/bootstrap/RunStatelessFlow.java"
    locator: "L40-L113"
    accessed: 2024-07-04
  source-stateless-bootstrap-unpack:
    title: "StatelessBootstrap NAR Handling"
    path: "nifi-stateless/nifi-stateless-bootstrap/src/main/java/org/apache/nifi/stateless/bootstrap/StatelessBootstrap.java"
    locator: "L100-L187"
    accessed: 2024-07-04
  source-stateless-api-interface:
    title: "StatelessDataflow Interface"
    path: "nifi-stateless/nifi-stateless-api/src/main/java/org/apache/nifi/stateless/flow/StatelessDataflow.java"
    locator: "L33-L113"
    accessed: 2024-07-04
  source-stateless-engine-factory:
    title: "StandardStatelessDataflowFactory"
    path: "nifi-stateless/nifi-stateless-bundle/nifi-stateless-engine/src/main/java/org/apache/nifi/stateless/flow/StandardStatelessDataflowFactory.java"
    locator: "L129-L182"
    accessed: 2024-07-04
---

## Introduction / Overview

<span id="claim-stateless-engine-overview">Apache NiFi's Stateless Execution Engine runs an entire process group as a single unit, triggering sources once and optionally cloning the flow for multiple concurrent tasks.</span>
<span id="claim-stateless-data-loss">Queues inside a stateless group are transient, so restarting the runtime drops any in-flight data.</span>
<span id="claim-stateless-replay-sources">Stateless NiFi assumes inputs are reliable and replayable because it buffers data in memory until the run finishes and only then acknowledges the source.</span>

## Concepts / Architecture

- <span id="claim-stateless-interface">The `StatelessDataflow` API supplies initialization, trigger, shutdown, queuing, counter, and state-access hooks so orchestrators can drive executions deterministically.</span>
- <span id="claim-runstateless-cli">The `RunStatelessFlow` launcher parses command-line arguments, loads engine properties, constructs the dataflow, and either loops continuously or triggers a single run before shutdown.</span>
- <span id="claim-bootstrap-nar">`StatelessBootstrap` unpacks the required NARs into a working directory and builds an allow-listed classloader so stateless extensions mirror the classpath they expect in full NiFi deployments.</span>
- <span id="claim-engine-components">`StandardStatelessDataflowFactory` assembles the stateless runtime by initializing the process scheduler, repositories, asset manager, extension discovery, and SSL-aware extension repository.</span>

## Implementation / Configuration

<span id="claim-engine-files">Launching the stateless script requires an engine configuration file, a dataflow configuration file, and the exported flow definition, as shown by the documented `bin/nifi.sh stateless -c -e ... -f ...` invocation.</span>

```bash
bin/nifi.sh stateless -c -e /var/lib/nifi/stateless/config/stateless.properties -f /var/lib/nifi/stateless/flows/jms-to-kafka.properties
```

<span id="claim-engine-dirs">Engine properties must at least point to the NAR directory, a writable working directory, and optionally a content repository path for large flow files.</span>
<span id="claim-extension-clients">The engine configuration can list writable and read-only extension directories and map Nexus extension clients so missing bundles download into the writable location automatically.</span>
<span id="claim-dataflow-sourcing">Dataflow configuration can reference a NiFi Registry flow, a local snapshot file, or a remote URL, all using the Versioned Flow Snapshot format exported by NiFi.</span>
<span id="claim-parameter-context">The same properties file can define parameter contexts and individual parameters that must match the names referenced by the flow.</span>
<span id="claim-transaction-thresholds">`nifi.stateless.transaction.thresholds.*` properties cap how many flow files, how many bytes, or how much time a single stateless invocation may admit before sources pause.</span>
<span id="claim-failure-port-config">`nifi.stateless.failure.port.names` declares output ports that, when hit, roll back the entire session so the source can be re-polled.</span>

## Usage / Examples

<span id="claim-parameter-overrides-cli">You can override parameters at launch with repeated `-p` flags in the form `[context:]name=value`, quoting strings that contain spaces or delimiters.</span>

```bash
bin/nifi.sh stateless -c \
  -p "Kafka Parameter Context:Kafka Brokers=kafka-01:9092,kafka-02:9092,kafka-03:9092" \
  -p "Kafka Parameter Context:Kafka Topic=Sensor Data" \
  /var/lib/nifi/stateless/config/stateless.properties \
  /var/lib/nifi/stateless/flows/jms-to-kafka.properties
```

<span id="claim-parameter-providers">Custom parameter value providers register through keyed properties that supply the provider name, class, bundle coordinate, and provider-specific settings such as secret or file locations.</span>

## Best Practices / Tips

- <span id="claim-single-source">Design stateless flows with a single source and sink to avoid duplicate deliveries when downstream processors roll back.</span>
- <span id="claim-merging-limits">Set bin size or age limits when using merge processors so a stateless run can finish without unbounded retries.</span>
- <span id="claim-failure-handling">Route unrecoverable conditions to dedicated output ports and treat them as failure ports instead of looping back to the same processor.</span>
- <span id="claim-concurrency-caution">When increasing concurrent tasks, remember that each copy of the flow keeps its own processor state, multiplying memory requirements.</span>

## Troubleshooting

<span id="claim-validation">The launcher initializes and validates the dataflow before first trigger and aborts if any component remains invalid.</span>

## Reference / Related Docs

- Apache NiFi User Guide – Stateless Execution Engine (`nifi-docs/src/main/asciidoc/user-guide.adoc`)
- Stateless NiFi Assembly README (`nifi-stateless/nifi-stateless-assembly/README.md`)
- Stateless runtime sources under `nifi-stateless/nifi-stateless-bootstrap` and `nifi-stateless/nifi-stateless-bundle`
