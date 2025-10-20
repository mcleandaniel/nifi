```markdown
---
claims:
  claim-platform-components:
    sources:
      - source-nifi-overview-architecture
  claim-repository-immutability:
    sources:
      - source-nifi-in-depth-repositories
  claim-repository-roles:
    sources:
      - source-nifi-in-depth-repositories
  claim-cluster-zero-leader:
    sources:
      - source-nifi-overview-architecture
      - source-nifi-admin-cluster
  claim-cluster-roles:
    sources:
      - source-nifi-admin-cluster
  claim-site-to-site:
    sources:
      - source-nifi-overview-features
  claim-scaling-cluster:
    sources:
      - source-nifi-overview-features
  claim-minifi-edge:
    sources:
      - source-nifi-overview-features
  claim-toolkit-cli:
    sources:
      - source-nifi-admin-cluster
  claim-registry-versioning:
    sources:
      - source-nifi-user-registry
  claim-registry-client-setup:
    sources:
      - source-nifi-user-registry
  claim-registry-buckets:
    sources:
      - source-nifi-user-registry
  claim-guaranteed-delivery:
    sources:
      - source-nifi-overview-features
  claim-backpressure:
    sources:
      - source-nifi-overview-features
  claim-offload:
    sources:
      - source-nifi-admin-cluster
  claim-cli-node-commands:
    sources:
      - source-nifi-admin-cluster
sources:
  source-nifi-overview-architecture:
    title: Apache NiFi Overview
    url: https://github.com/apache/nifi/blob/main/nifi-docs/src/main/asciidoc/overview.adoc
    locator: L122-L150
    accessed: 2025-02-15
  source-nifi-overview-features:
    title: Apache NiFi Overview – High Level Features
    url: https://github.com/apache/nifi/blob/main/nifi-docs/src/main/asciidoc/overview.adoc
    locator: L190-L267
    accessed: 2025-02-15
  source-nifi-in-depth-repositories:
    title: Apache NiFi In Depth
    url: https://github.com/apache/nifi/blob/main/nifi-docs/src/main/asciidoc/nifi-in-depth.adoc
    locator: L22-L41
    accessed: 2025-02-15
  source-nifi-admin-cluster:
    title: Apache NiFi Administration Guide – Clustering
    url: https://github.com/apache/nifi/blob/main/nifi-docs/src/main/asciidoc/administration-guide.adoc
    locator: L1904-L2050
    accessed: 2025-02-15
  source-nifi-user-registry:
    title: Apache NiFi User Guide – Versioning a DataFlow
    url: https://github.com/apache/nifi/blob/main/nifi-docs/src/main/asciidoc/user-guide.adoc
    locator: L2544-L2575
    accessed: 2025-02-15
---

# End-to-End NiFi Platform Architecture

## Introduction / Overview
<span id="claim-platform-components">Apache NiFi runs in a JVM-based runtime that hosts an HTTP command web server, a flow controller, pluggable extensions, and repositories dedicated to FlowFile metadata, content, and provenance.</span>
NiFi’s platform approach then layers registries, edge agents, and tooling on top of this core runtime to cover the full dataflow lifecycle.

## Concepts / Architecture
<span id="claim-repository-roles">NiFi persists FlowFile metadata, payload content, and provenance history in separate repositories on local storage.</span>
<span id="claim-repository-immutability">FlowFile attributes and content are treated as immutable, with updates creating new copies to support replay and efficient storage.</span>
<span id="claim-cluster-zero-leader">NiFi clusters follow a zero-leader pattern in which ZooKeeper elects a coordinator that supplies the current flow and distributes work across nodes while each node processes a distinct slice of data.</span>
<span id="claim-cluster-roles">Cluster terminology distinguishes a coordinator that manages membership, processing nodes that execute the flow, and a ZooKeeper-elected primary node for isolated processors.</span>
<span id="claim-site-to-site">NiFi Site-to-Site is the preferred protocol for inter-instance movement of FlowFiles, supporting both socket and HTTP(S) transports and embeddable client libraries.</span>
<span id="claim-scaling-cluster">Clustering combined with Site-to-Site enables throughput to scale from hundreds of MB per second on a node to multi-GB per second across the cluster by balancing load with connected systems.</span>
<span id="claim-minifi-edge">MiNiFi targets first-mile edge data collection with a footprint suited to constrained hardware.</span>

## Implementation / Configuration
<span id="claim-toolkit-cli">The NiFi Toolkit CLI automates flow deployments to NiFi and NiFi Registry and manages process groups and cluster nodes.</span>
<span id="claim-registry-versioning">Linking NiFi to NiFi Registry provides process-group-level version control for dataflows.</span>
<span id="claim-registry-client-setup">Registry clients are added through Controller Settings by creating a Registry Client entry and configuring its settings and properties.</span>
<span id="claim-registry-buckets">Registry bucket policies determine which buckets users can import from or save versioned flows into.</span>

## Usage / Examples
Combine MiNiFi agents at the edge with Site-to-Site to stream field data into a clustered NiFi deployment, version the flow definition in NiFi Registry, and script promotion through environments with the CLI. This pattern keeps data capture, transport, and lifecycle management aligned with the runtime primitives described above.

## Best Practices / Tips
<span id="claim-guaranteed-delivery">Guaranteed delivery is achieved through the write-ahead FlowFile repository working in concert with the persistent content repository.</span>
<span id="claim-backpressure">Connection back-pressure policies pause upstream processors or expire aged FlowFiles when queue limits are reached.</span>
Build resilient pipelines by combining these guarantees with Registry-managed versioning and scripted deployments for reproducible releases.

## Troubleshooting
<span id="claim-offload">Offloading a disconnected node stops its processors, halts remote group transmissions, and rebalances remaining FlowFiles to healthy nodes before removal.</span>
<span id="claim-cli-node-commands">CLI commands such as nifi get-node, connect-node, offload-node, and delete-node support scripted node recovery workflows.</span>
Pair these actions with monitoring to ensure cluster membership stays aligned with operational expectations.

## Reference / Related Docs
- Apache NiFi Overview (core architecture and features)
- Apache NiFi In Depth (FlowFile model and repositories)
- Apache NiFi Administration Guide (clustering and operations)
- Apache NiFi User Guide (Registry integration and UI workflows)
```
