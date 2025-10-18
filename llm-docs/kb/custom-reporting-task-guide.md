---
claims:
  - id: claim-reporting-task-purpose
    sources: [src-nifi-user-guide]
  - id: claim-reporting-task-interface
    sources: [src-nifi-dev-guide-reporting]
  - id: claim-reporting-context
    sources: [src-nifi-dev-guide-reporting]
  - id: claim-controller-service-binding
    sources: [src-nifi-dev-guide-reporting]
  - id: claim-reporting-eventaccess
    sources: [src-nifi-dev-guide-reporting]
  - id: claim-nar-packaging
    sources: [src-nifi-dev-guide-nar]
  - id: claim-service-loader-registration
    sources: [src-nifi-meta-reporting]
  - id: claim-rest-create
    sources: [src-nifi-rest-create]
  - id: claim-rest-update
    sources: [src-nifi-rest-update]
  - id: claim-rest-validate
    sources: [src-nifi-rest-update]
  - id: claim-rest-runstatus
    sources: [src-nifi-rest-runstatus]
  - id: claim-rest-state
    sources: [src-nifi-rest-runstatus]
  - id: claim-bulletin-practice
    sources: [src-nifi-dev-guide-reporting]
  - id: claim-eventaccess-practice
    sources: [src-nifi-dev-guide-reporting]
  - id: claim-rest-validate-troubleshoot
    sources: [src-nifi-rest-update]
  - id: claim-rest-state-troubleshoot
    sources: [src-nifi-rest-runstatus]
  - id: claim-reference-userguide
    sources: [src-nifi-user-guide]
  - id: claim-reference-devguide
    sources: [src-nifi-dev-guide-reporting]
  - id: claim-reference-rest
    sources: [src-nifi-rest-update]
sources:
  - id: src-nifi-user-guide
    title: "Apache NiFi User Guide"
    url: "https://github.com/apache/nifi/blob/main/nifi-docs/src/main/asciidoc/user-guide.adoc"
    locator: "L96-L104"
  - id: src-nifi-dev-guide-reporting
    title: "Apache NiFi Developer Guide"
    url: "https://github.com/apache/nifi/blob/main/nifi-docs/src/main/asciidoc/developer-guide.adoc"
    locator: "L2003-L2036"
  - id: src-nifi-dev-guide-nar
    title: "Apache NiFi Developer Guide"
    url: "https://github.com/apache/nifi/blob/main/nifi-docs/src/main/asciidoc/developer-guide.adoc"
    locator: "L2418-L2445"
  - id: src-nifi-meta-reporting
    title: "nifi-standard-reporting-tasks Service Loader"
    url: "https://github.com/apache/nifi/blob/main/nifi-extension-bundles/nifi-standard-bundle/nifi-standard-reporting-tasks/src/main/resources/META-INF/services/org.apache.nifi.reporting.ReportingTask"
    locator: "L13-L15"
  - id: src-nifi-rest-create
    title: "NiFi REST API (Reporting Tasks)"
    url: "https://nifi.apache.org/docs/nifi-docs/rest-api/"
    locator: "L7344-L7386"
  - id: src-nifi-rest-update
    title: "NiFi REST API (Reporting Tasks)"
    url: "https://nifi.apache.org/docs/nifi-docs/rest-api/"
    locator: "L7462-L7477"
  - id: src-nifi-rest-runstatus
    title: "NiFi REST API (Reporting Tasks Lifecycle)"
    url: "https://nifi.apache.org/docs/nifi-docs/rest-api/"
    locator: "L7591-L7619"
---

# Custom Reporting Tasks in Apache NiFi 2.6

## Introduction / Overview
<span id="claim-reporting-task-purpose">Reporting Tasks run in the background to publish NiFi instance metrics to destinations such as log files, email systems, and remote services.</span>

This guide explains how to implement, package, and operate a custom Reporting Task for Apache NiFi v2.6, using repository resources and REST automation.

## Concepts / Architecture
<span id="claim-reporting-task-interface">The ReportingTask interface exposes NiFi-managed lifecycle hooks for configuration, validation, initialization, and a framework-invoked onTrigger method.</span>

<span id="claim-reporting-context">During onTrigger, NiFi injects a ReportingContext that exposes component configuration, a BulletinRepository for operator notices, and ControllerServiceLookup access.</span>

<span id="claim-controller-service-binding">Controller services should be obtained by referencing them in PropertyDescriptor definitions instead of fetching them directly from the lookup.</span>

<span id="claim-reporting-eventaccess">ReportingContext.getEventAccess surfaces ProcessGroupStatus metrics and ProvenanceEventRecord data that a Reporting Task can aggregate.</span>

## Implementation / Configuration
- <span id="claim-nar-packaging">Set the module’s Maven packaging to nar and apply the nifi-nar-maven-plugin to produce a NiFi Archive bundle.</span>
- <span id="claim-service-loader-registration">Register the task’s fully qualified class name in META-INF/services/org.apache.nifi.reporting.ReportingTask so NiFi’s ServiceLoader can discover it.</span>

Example `pom.xml` fragment:

```xml
<project>
  <modelVersion>4.0.0</modelVersion>
  <groupId>com.example</groupId>
  <artifactId>nifi-cluster-metrics-reporting-task</artifactId>
  <version>1.0.0</version>
  <packaging>nar</packaging>
  <properties>
    <nifi.version>2.6.0</nifi.version>
  </properties>
  <build>
    <plugins>
      <plugin>
        <groupId>org.apache.nifi</groupId>
        <artifactId>nifi-nar-maven-plugin</artifactId>
        <version>${nifi.version}</version>
        <extensions>true</extensions>
      </plugin>
    </plugins>
  </build>
</project>
```

Service registration file (`src/main/resources/META-INF/services/org.apache.nifi.reporting.ReportingTask`):

```text
com.example.reporting.ClusterMetricsReportingTask
```

Sample implementation outline:

```java
@Tags({"metrics", "cluster"})
@CapabilityDescription("Publishes aggregated NiFi cluster metrics to an external REST endpoint.")
public class ClusterMetricsReportingTask extends AbstractReportingTask {

    private volatile MetricsClient client;

    @OnScheduled
    public void onScheduled(final ReportingContext context) {
        client = new MetricsClient(getLogger(), context);
    }

    @OnStopped
    public void onStopped() {
        client = null;
    }

    @Override
    public List<PropertyDescriptor> getSupportedPropertyDescriptors() {
        final List<PropertyDescriptor> descriptors = new ArrayList<>();
        descriptors.add(new PropertyDescriptor.Builder()
                .name("Destination URL")
                .description("HTTPS endpoint that receives aggregated metrics.")
                .required(true)
                .addValidator(StandardValidators.URL_VALIDATOR)
                .build());
        return descriptors;
    }

    @Override
    public void onTrigger(final ReportingContext context) {
        final ProcessGroupStatus status = context.getEventAccess().getControllerStatus();
        final Map<String, Object> payload = Map.of(
                "timestamp", System.currentTimeMillis(),
                "flowFilesIn", status.getFlowFilesIn(),
                "bytesIn", status.getBytesIn());
        client.publish(payload);
    }
}
```

## Usage / Examples
Build and install the NAR into the NiFi `lib` directory, then restart NiFi or use hot-deploy if you are developing inside a containerized environment.

- <span id="claim-rest-create">POST /reporting-tasks creates a reporting task when you supply the component metadata and properties in the request body.</span>
- <span id="claim-rest-update">PUT /reporting-tasks/{id} persists configuration updates to an existing reporting task.</span>
- <span id="claim-rest-validate">PUT /reporting-tasks/{id}/validate runs server-side verification for the current configuration.</span>
- <span id="claim-rest-runstatus">PUT /reporting-tasks/{id}/run-status transitions the task between STOPPED and RUNNING states.</span>
- <span id="claim-rest-state">PUT /reporting-tasks/{id}/state manages the component’s stored state, including clear and describe actions.</span>

Create the task:

```bash
curl -u "$NIFI_AUTH" \
  -H 'Content-Type: application/json' \
  -X POST "https://nifi.example.com/nifi-api/reporting-tasks" \
  -d '{
        "revision": {"version": 0},
        "component": {
          "name": "Cluster Metrics",
          "type": "com.example.reporting.ClusterMetricsReportingTask",
          "schedulingPeriod": "1 min",
          "schedulingStrategy": "TIMER_DRIVEN",
          "properties": {
            "Destination URL": "https://metrics.example.com/api"
          }
        }
      }'
```

Update properties (increment revision.version from the last response):

```bash
curl -u "$NIFI_AUTH" \
  -H 'Content-Type: application/json' \
  -X PUT "https://nifi.example.com/nifi-api/reporting-tasks/${TASK_ID}" \
  -d '{
        "revision": {"version": 1},
        "component": {
          "id": "'"${TASK_ID}"'",
          "schedulingPeriod": "30 sec",
          "properties": {
            "Destination URL": "https://metrics.example.com/api/v2"
          }
        }
      }'
```

Validate and start:

```bash
curl -u "$NIFI_AUTH" \
  -H 'Content-Type: application/json' \
  -X PUT "https://nifi.example.com/nifi-api/reporting-tasks/${TASK_ID}/validate" \
  -d '{"revision":{"version":2},"component":{"id":"'"${TASK_ID}"'"}}'

curl -u "$NIFI_AUTH" \
  -H 'Content-Type: application/json' \
  -X PUT "https://nifi.example.com/nifi-api/reporting-tasks/${TASK_ID}/run-status" \
  -d '{"revision":{"version":3},"state":"RUNNING"}'
```

## Best Practices / Tips
- <span id="claim-bulletin-practice">Use the BulletinRepository from ReportingContext to surface task health issues to operators.</span>
- <span id="claim-eventaccess-practice">Leverage EventAccess statistics and provenance records to emit actionable metrics snapshots.</span>

Keep your Reporting Task idempotent, guard outbound calls with timeouts, and emit structured logs so NiFi’s bulletin board stays informative.

## Troubleshooting
<span id="claim-rest-validate-troubleshoot">Re-run PUT /reporting-tasks/{id}/validate to obtain field-level diagnostics before scheduling.</span>

<span id="claim-rest-state-troubleshoot">Use PUT /reporting-tasks/{id}/state to clear or inspect component state after schema or destination changes to avoid stale caches.</span>

Inspect NiFi app logs for stack traces, compare task state with the latest run-status response payload, and re-deploy the NAR if classpath conflicts appear during initialization.

## Reference / Related Docs
- <span id="claim-reference-userguide">Apache NiFi User Guide — component overview and UI management for reporting tasks.</span>
- <span id="claim-reference-devguide">Apache NiFi Developer Guide — detailed ReportingTask SPI and extension packaging workflow.</span>
- <span id="claim-reference-rest">NiFi REST API — REST endpoints for configuring and scheduling reporting tasks.</span>
