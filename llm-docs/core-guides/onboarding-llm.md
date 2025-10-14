# NiFi Onboarding Guides — LLM Notes

*Sources*: 
- `nifi-docs/src/main/asciidoc/overview.adoc`
- `nifi-docs/src/main/asciidoc/getting-started.adoc`
- `nifi-docs/src/main/asciidoc/walkthroughs.adoc`
(Reviewed 2025-10-13)

## Product Overview
- **Mission**: Automate secure, reliable data movement between systems (“dataflow”). Designed around Flow-Based Programming concepts.
- **Core Concepts**:
  - *FlowFile* (data + attributes), *Processor* (black box operation), *Connection* (queued buffer with back pressure), *Flow Controller* (scheduler), *Process Group* (composable subflow).
- **Architecture Highlights**:
  - Asynchronous, highly concurrent, resource-aware (back pressure, prioritizers).
  - Provenance tracking, data durability (repo-backed queues), visual UI for directed graphs.
- **Performance Considerations**:
  - Tuned for continuous ingestion; throughput governed by repository I/O, JVM resources, and back pressure settings.
  - Prioritizers and load-balancing enable time-sensitive processing.
- **Key Features**:
  - Rich processor library (ingestion, routing, transformation, enrichment).
  - Versioned flows (NiFi Registry integration), parameter contexts, secure multi-tenancy, provenance, monitoring dashboards.

## Getting Started Essentials
- **Installation**:
  - Download binary, unzip/untar, edit `conf/nifi.properties` (set `nifi.sensitive.props.key`), start via `bin/nifi.sh start` (Linux/macOS) or `bin\\nifi.cmd start` (Windows).
  - Default UI available at `http(s)://host:port/nifi`.
- **UI Tour**:
  - Canvas with component toolbar, status bar, breadcrumbs, Operate Palette.
  - Add processors by drag-and-drop; configuration dialog has Settings, Scheduling, Properties, Relationships, Comments tabs.
  - Connect components via connections: set source, destination, relationships, back pressure limits, prioritizers.
  - Start/stop processors, run once, enable/disable controller services.
- **Processor Categories**: Data transformation, routing/mediation, database, attribute extraction, system interaction, ingestion (files, messaging systems), egress, splitting/aggregation, HTTP, AWS integrations.
- **Attributes & Expression Language**:
  - Core attributes (`filename`, `path`, `uuid`, etc.), user-defined attributes via `UpdateAttribute`.
  - Expression Language in property values for dynamic routing (`${filename}`, `${fileSize:gt(1048576)}`).
- **Monitoring & Troubleshooting**:
  - Status bar for cluster/node health; component statistics for queued/processed counts.
  - Bulletins (warnings/errors) appear on components and in bulletin board.
  - Data Provenance: browse events, view/replay content, lineage graph.
- **Next Steps**:
  - Explore processor usage docs via right-click → Usage, or global Help.
  - Check NiFi Registry integration for version control.

## Walkthrough Highlights
- **Installing NiFi**: Step-by-step instructions for package extraction, directory layout, configuration updates, service scripts.
- **Building from Source**:
  - Requires JDK, Maven, Git; run `mvn -Pinclude-grpc -DskipTests clean install`.
  - Artifacts produced under `nifi-assembly/target`.
- **Starting & Configuring**:
  - `bin/nifi.sh start|stop|status|run`; configuration values in `conf/nifi.properties`, `conf/bootstrap.conf`, `conf/logback.xml`.
- **Securing NiFi with TLS**:
  - Rationale: encryption, integrity, enable authN/Z.
  - Walkthrough covers using provided certificates (PEM examples) or generating with `tls-toolkit`.
  - Configure keystore/truststore, enable HTTPS (`nifi.web.https.*`), set client auth, refresh Jetty context.
- **Cluster Deployment**:
  - DNS considerations (consistent hostnames), load balancers, ZooKeeper coordination.
  - Steps to configure node addresses, cluster ports, state providers, and replicate configs.
- **Additional Scenarios**:
  - Manual keystore generation (OpenSSL, keytool).
  - Using `dnsmasq` for local DNS resolution during cluster setup.

## LLM Answer Tips
- For new users: outline install → start → add processor → connect → start flow; mention Help/Usage links.
- When asked “Why NiFi?”, emphasize features from Overview (back pressure, provenance, security, rapid change).
- Installation issues: highlight required configs (`nifi.sensitive.props.key`, port settings), platform-specific start commands.
- TLS/setup questions: mention TLS is mandatory for auth; refer to `nifi.properties` keys (`nifi.web.https.host`, keystore/truststore).
- Cluster FAQs: note need for consistent configs across nodes, ZooKeeper ensemble, load-balanced Site-to-Site.
- Building from source: remind to use compatible JDK, Maven, and run full build with appropriate profile.

## Quick FAQs
1. **“How do I start NiFi?”** → Unpack, edit `conf/nifi.properties`, run `bin/nifi.sh start` (or Windows script).
2. **“Where do I find processor doc?”** → Right-click processor → Usage, or Help menu for full catalog.
3. **“Why secure NiFi?”** → TLS is required for auth; configure keystore/truststore and set HTTPS properties.
4. **“What’s the minimum to build from source?”** → JDK + Maven; run `mvn clean install` and use artifacts in `nifi-assembly/target`.
5. **“How do I monitor data movement?”** → Use Component Statistics, bulletins, and Data Provenance lineage/provenance views.
