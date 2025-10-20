---
claims:
  claim-implementation-default:
    sources:
      - nifi-admin-impl
  claim-volatile-fifo:
    sources:
      - nifi-admin-impl
  claim-noop:
    sources:
      - nifi-admin-impl
  claim-rollover-events:
    sources:
      - nifi-admin-impl
  claim-directory-partitions:
    sources:
      - nifi-admin-writeahead
  claim-retention-limits:
    sources:
      - nifi-admin-writeahead
  claim-prod-capacity:
    sources:
      - nifi-admin-writeahead
  claim-rollover-size:
    sources:
      - nifi-admin-writeahead
  claim-rollover-time:
    sources:
      - nifi-admin-persistent
  claim-compress-default:
    sources:
      - nifi-admin-writeahead
  claim-journal-count:
    sources:
      - nifi-admin-persistent
  claim-retention-controls:
    sources:
      - nifi-admin-writeahead
  claim-volatile-buffer-default:
    sources:
      - nifi-admin-volatile
  claim-index-thread-guidance:
    sources:
      - nifi-admin-writeahead
  claim-index-shard-guidance:
    sources:
      - nifi-admin-writeahead
  claim-concurrent-merge:
    sources:
      - nifi-admin-writeahead
  claim-warm-cache:
    sources:
      - nifi-admin-writeahead
  claim-index-bulletin:
    sources:
      - nifi-admin-persistent
  claim-always-sync-tradeoff:
    sources:
      - nifi-admin-writeahead
  claim-reference-admin-guide:
    sources:
      - nifi-admin-writeahead
sources:
  nifi-admin-impl:
    title: "Apache NiFi Administration Guide"
    href: "nifi-docs/src/main/asciidoc/administration-guide.adoc"
    locator: "L3017-L3030"
  nifi-admin-writeahead:
    title: "Apache NiFi Administration Guide"
    href: "nifi-docs/src/main/asciidoc/administration-guide.adoc"
    locator: "L3038-L3093"
  nifi-admin-persistent:
    title: "Apache NiFi Administration Guide"
    href: "nifi-docs/src/main/asciidoc/administration-guide.adoc"
    locator: "L3096-L3125"
  nifi-admin-volatile:
    title: "Apache NiFi Administration Guide"
    href: "nifi-docs/src/main/asciidoc/administration-guide.adoc"
    locator: "L3128-L3133"
---

# Data Provenance Storage and Retention

## Introduction / Overview
<span id="claim-implementation-default">Apache NiFi selects its provenance backend through the `nifi.provenance.repository.implementation` property, which defaults to `org.apache.nifi.provenance.WriteAheadProvenanceRepository`.</span>
<span id="claim-volatile-fifo">Setting the implementation to `org.apache.nifi.provenance.VolatileProvenanceRepository` keeps provenance events on the Java heap, evicting them first-in-first-out and losing all data on restart.</span>
<span id="claim-noop">Choosing `org.apache.nifi.provenance.NoOpProvenanceRepository` disables provenance event storage entirely to minimize resource usage.</span>
<span id="claim-rollover-events">Completed event files rotate once `nifi.provenance.repository.rollover.events` is reached, with the ceiling defaulting to `Integer.MAX_VALUE`.</span>

## Concepts / Architecture
<span id="claim-directory-partitions">Persistent repositories can span multiple volumes by defining additional `nifi.provenance.repository.directory.<suffix>` properties that each point at a distinct filesystem path.</span>
<span id="claim-retention-limits">Retention is jointly constrained by `nifi.provenance.repository.max.storage.time` (default 30 days) and `nifi.provenance.repository.max.storage.size` (default 10 GB).</span>
<span id="claim-prod-capacity">The administration guide notes that production deployments often provision 1–2 TB or more of provenance capacity because the repository grows quickly.</span>
<span id="claim-rollover-size">`nifi.provenance.repository.rollover.size` governs per-file size, defaulting to 100 MB and commonly raised to 1 GB for high-volume dataflows.</span>

## Implementation / Configuration
<span id="claim-rollover-time">Persistent repositories expose freshly captured events to the UI after the interval set in `nifi.provenance.repository.rollover.time`, which defaults to 10 minutes.</span>
<span id="claim-compress-default">NiFi compresses provenance event files at rollover by default via `nifi.provenance.repository.compress.on.rollover`.</span>
<span id="claim-journal-count">The `nifi.provenance.repository.journal.count` property defaults to 16 journals, trading higher write concurrency against more expensive journal merges.</span>

## Usage / Examples
<span id="claim-retention-controls">Adjusting `nifi.provenance.repository.max.storage.time` and `nifi.provenance.repository.max.storage.size` in `nifi.properties` directly determines how long events are retained and how much disk the repository may consume.</span>

```properties
# Persistent repository tuned for a weekly retention window
nifi.provenance.repository.implementation=org.apache.nifi.provenance.WriteAheadProvenanceRepository
nifi.provenance.repository.directory.default=/var/lib/nifi/provenance
nifi.provenance.repository.max.storage.time=7 days
nifi.provenance.repository.max.storage.size=512 GB
nifi.provenance.repository.rollover.size=1 GB
nifi.provenance.repository.rollover.time=5 mins

# Optional: switch to volatile mode for ephemeral testing
# nifi.provenance.repository.implementation=org.apache.nifi.provenance.VolatileProvenanceRepository
# nifi.provenance.repository.buffer.size=100000
```

<span id="claim-volatile-buffer-default">Volatile mode respects `nifi.provenance.repository.buffer.size`, which defaults to 100000 events.</span>

## Best Practices / Tips
- <span id="claim-index-thread-guidance">Configure at least one `nifi.provenance.repository.index.threads` worker per storage location and rarely exceed two to four threads per location.</span>
- <span id="claim-index-shard-guidance">Increase `nifi.provenance.repository.index.shard.size` toward 4–8 GB for production to improve search speed while keeping it below half of the maximum storage size because of heap impact.</span>
- <span id="claim-concurrent-merge">Keep `nifi.provenance.repository.concurrent.merge.threads` below the product of index threads and storage locations to prevent long pauses during Lucene segment merges.</span>
- <span id="claim-warm-cache">Enable `nifi.provenance.repository.warm.cache.frequency` only when spare CPU and disk I/O are available, because the warming cycle trades cacheable query speed for overall system load.</span>

## Troubleshooting
- <span id="claim-index-bulletin">When provenance indexing lags, NiFi emits a bulletin stating “The rate of the dataflow is exceeding the provenance recording rate,” signaling that `nifi.provenance.repository.index.threads` should be increased.</span>
- <span id="claim-always-sync-tradeoff">Setting `nifi.provenance.repository.always.sync=true` forces the OS to flush every update, reducing crash risk at the expense of significant throughput.</span>

## Reference / Related Docs
- <span id="claim-reference-admin-guide">Refer to the Apache NiFi Administration Guide provenance repository sections for comprehensive property descriptions and defaults.</span>
