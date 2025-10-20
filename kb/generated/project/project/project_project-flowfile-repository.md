---
title: FlowFile Repository Architecture
claims:
  - id: claim-flowfile-state
    sources:
      - source-admin-flowfile-overview
  - id: claim-repo-implementations
    sources:
      - source-admin-flowfile-impl
  - id: claim-writeahead-wali
    sources:
      - source-writeahead-wali
  - id: claim-writeahead-init
    sources:
      - source-writeahead-init
  - id: claim-serialization-factory
    sources:
      - source-serialization-factory
  - id: claim-serialization-schema
    sources:
      - source-serialization-schema
  - id: claim-serialization-legacy
    sources:
      - source-serialization-legacy
  - id: claim-swap-interface
    sources:
      - source-swap-interface
  - id: claim-filesystem-swap-dir
    sources:
      - source-filesystem-swap-dir
  - id: claim-swap-filename
    sources:
      - source-filesystem-swap-ops
  - id: claim-swap-serialization
    sources:
      - source-filesystem-swap-ops
      - source-swap-serialization
      - source-swap-schema
  - id: claim-properties
    sources:
      - source-nifi-properties
  - id: claim-admin-writeahead-config
    sources:
      - source-admin-flowfile-impl
  - id: claim-swap-threshold
    sources:
      - source-admin-swap
  - id: claim-retain-orphaned
    sources:
      - source-writeahead-retain
      - source-writeahead-retain-behavior
  - id: claim-separate-content
    sources:
      - source-admin-content
  - id: claim-recovery
    sources:
      - source-writeahead-recovery
  - id: claim-swap-temp-cleanup
    sources:
      - source-filesystem-swap-ops
  - id: claim-usage-config
    sources:
      - source-admin-flowfile-overview
  - id: claim-usage-threshold
    sources:
      - source-admin-swap
  - id: claim-ref-admin
    sources:
      - source-admin-flowfile-impl
  - id: claim-ref-wali
    sources:
      - source-writeahead-wali
  - id: claim-ref-swap
    sources:
      - source-swap-interface
sources:
  - id: source-admin-flowfile-overview
    type: asciidoc
    title: "Apache NiFi Administration Guide"
    url: "nifi-docs/src/main/asciidoc/administration-guide.adoc"
    locator: "L2922-L2927"
  - id: source-admin-flowfile-impl
    type: asciidoc
    title: "Apache NiFi Administration Guide"
    url: "nifi-docs/src/main/asciidoc/administration-guide.adoc"
    locator: "L2928-L2950"
  - id: source-admin-swap
    type: asciidoc
    title: "Apache NiFi Administration Guide"
    url: "nifi-docs/src/main/asciidoc/administration-guide.adoc"
    locator: "L2951-L2965"
  - id: source-admin-content
    type: asciidoc
    title: "Apache NiFi Administration Guide"
    url: "nifi-docs/src/main/asciidoc/administration-guide.adoc"
    locator: "L2967-L2973"
  - id: source-nifi-properties
    type: code
    title: "NiFiProperties.java"
    url: "nifi-commons/nifi-properties/src/main/java/org/apache/nifi/util/NiFiProperties.java"
    locator: "L99-L106"
  - id: source-writeahead-wali
    type: code
    title: "WriteAheadFlowFileRepository.java"
    url: "nifi-framework-bundle/nifi-framework/nifi-framework-core/src/main/java/org/apache/nifi/controller/repository/WriteAheadFlowFileRepository.java"
    locator: "L60-L79"
  - id: source-writeahead-init
    type: code
    title: "WriteAheadFlowFileRepository.java"
    url: "nifi-framework-bundle/nifi-framework/nifi-framework-core/src/main/java/org/apache/nifi/controller/repository/WriteAheadFlowFileRepository.java"
    locator: "L148-L195"
  - id: source-writeahead-retain
    type: code
    title: "WriteAheadFlowFileRepository.java"
    url: "nifi-framework-bundle/nifi-framework/nifi-framework-core/src/main/java/org/apache/nifi/controller/repository/WriteAheadFlowFileRepository.java"
    locator: "L152-L156"
  - id: source-writeahead-retain-behavior
    type: code
    title: "WriteAheadFlowFileRepository.java"
    url: "nifi-framework-bundle/nifi-framework/nifi-framework-core/src/main/java/org/apache/nifi/controller/repository/WriteAheadFlowFileRepository.java"
    locator: "L758-L769"
  - id: source-writeahead-recovery
    type: code
    title: "WriteAheadFlowFileRepository.java"
    url: "nifi-framework-bundle/nifi-framework/nifi-framework-core/src/main/java/org/apache/nifi/controller/repository/WriteAheadFlowFileRepository.java"
    locator: "L703-L807"
  - id: source-serialization-factory
    type: code
    title: "StandardRepositoryRecordSerdeFactory.java"
    url: "nifi-framework-bundle/nifi-framework/nifi-flowfile-repo-serialization/src/main/java/org/apache/nifi/controller/repository/StandardRepositoryRecordSerdeFactory.java"
    locator: "L26-L54"
  - id: source-serialization-schema
    type: code
    title: "SchemaRepositoryRecordSerde.java"
    url: "nifi-framework-bundle/nifi-framework/nifi-flowfile-repo-serialization/src/main/java/org/apache/nifi/controller/repository/SchemaRepositoryRecordSerde.java"
    locator: "L74-L199"
  - id: source-serialization-legacy
    type: code
    title: "WriteAheadRepositoryRecordSerde.java"
    url: "nifi-framework-bundle/nifi-framework/nifi-flowfile-repo-serialization/src/main/java/org/apache/nifi/controller/repository/WriteAheadRepositoryRecordSerde.java"
    locator: "L43-L146"
  - id: source-swap-interface
    type: code
    title: "FlowFileSwapManager.java"
    url: "nifi-framework-api/src/main/java/org/apache/nifi/controller/repository/FlowFileSwapManager.java"
    locator: "L25-L112"
  - id: source-filesystem-swap-dir
    type: code
    title: "FileSystemSwapManager.java"
    url: "nifi-framework-bundle/nifi-framework/nifi-framework-core/src/main/java/org/apache/nifi/controller/FileSystemSwapManager.java"
    locator: "L109-L114"
  - id: source-filesystem-swap-ops
    type: code
    title: "FileSystemSwapManager.java"
    url: "nifi-framework-bundle/nifi-framework/nifi-framework-core/src/main/java/org/apache/nifi/controller/FileSystemSwapManager.java"
    locator: "L140-L339"
  - id: source-swap-serialization
    type: code
    title: "SchemaSwapSerializer.java"
    url: "nifi-framework-bundle/nifi-framework/nifi-framework-core/src/main/java/org/apache/nifi/controller/swap/SchemaSwapSerializer.java"
    locator: "L46-L99"
  - id: source-swap-schema
    type: code
    title: "SwapSchema.java"
    url: "nifi-framework-bundle/nifi-framework/nifi-framework-core/src/main/java/org/apache/nifi/controller/swap/SwapSchema.java"
    locator: "L115-L140"
---

## Introduction / Overview
<span id="claim-flowfile-state">The FlowFile repository records each FlowFile’s attributes and processing state and should be moved to its own storage volume whenever possible to reduce contention.</span>  
<span id="claim-repo-implementations">WriteAheadFlowFileRepository is the default implementation, and administrators can switch `nifi.flowfile.repository.implementation` to the volatile in-memory repository when they explicitly accept restart data loss.</span>

## Concepts / Architecture
<span id="claim-writeahead-wali">WriteAheadFlowFileRepository persists state using a WALI-backed write-ahead log and lets operators trade reliability for latency with the `nifi.flowfile.repository.always.sync` flag.</span>  
<span id="claim-writeahead-init">During initialization the repository reads `nifi.flowfile.repository.directory`, creates the required directories, and wires a SequentialAccessWriteAheadLog through its configured serde factory.</span>  
<span id="claim-serialization-factory">StandardRepositoryRecordSerdeFactory prefers the schema-based serializer and falls back to the legacy write-ahead serializer when older encoding names are encountered.</span>  
<span id="claim-serialization-schema">SchemaRepositoryRecordSerde encodes create, update, delete, and swap events with FlowFile identifiers, queue metadata, attributes, and claim references using versioned repository schemas.</span>  
<span id="claim-serialization-legacy">WriteAheadRepositoryRecordSerde version 9 continues to serialize FlowFile IDs, lineage timestamps, sizes, queue associations, content claim offsets, and optional attributes for backwards compatibility.</span>  
<span id="claim-swap-interface">FlowFileSwapManager defines the swap-out, peek, swap-in, recovery, partition, and summary operations that let queues spill FlowFiles from heap to external storage and back.</span>  
<span id="claim-filesystem-swap-dir">FileSystemSwapManager places swap files beneath the FlowFile repository path inside a dedicated `swap` directory it creates on startup.</span>  
<span id="claim-swap-filename">The swap manager filters `.swap` filenames by queue ID, discards unfinished `.swap.part` artifacts, and only returns locations acknowledged by the FlowFile repository.</span>  
<span id="claim-swap-serialization">Swap files start with the `SWAP` magic header and serializer name before SchemaSwapSerializer writes a summary record plus FlowFile entries encoded with FULL_SWAP_FILE_SCHEMA_V3 (queue identifier, counts, byte totals, timestamps, and resource-claim references).</span>

## Implementation / Configuration
<span id="claim-properties">NiFi exposes repository tuning through `nifi.flowfile.repository.implementation`, `nifi.flowfile.repository.always.sync`, `nifi.flowfile.repository.directory`, `nifi.flowfile.repository.checkpoint.interval`, `nifi.swap.manager.implementation`, and `nifi.queue.swap.threshold` keys in `nifi.properties`.</span>  
<span id="claim-admin-writeahead-config">The administration guide documents the write-ahead repository defaults: storing data in `./flowfile_repository`, checkpointing every 20 seconds, and noting that enabling `nifi.flowfile.repository.always.sync` increases durability at a heavy performance cost.</span>  
<span id="claim-swap-threshold">Swap management defaults to `org.apache.nifi.controller.FileSystemSwapManager`, begins swapping once queues hold 20 000 FlowFiles, and re-applies prioritizers only when swap data is pulled back into memory.</span>  
<span id="claim-retain-orphaned">The `nifi.flowfile.repository.retain.orphaned.flowfiles` flag defaults to true so recovered FlowFiles for removed queues stay in the repository and their resource claims keep valid reference counts.</span>

## Usage / Examples
<span id="claim-usage-config">Set `nifi.flowfile.repository.directory` to a dedicated mount (for example `/var/lib/nifi/flowfile`) before restart to isolate FlowFile metadata from other repositories.</span>  
<span id="claim-usage-threshold">Increase `nifi.queue.swap.threshold` above the default when you want NiFi to delay swapping queues to disk until they exceed the new FlowFile count.</span>

```ini
# nifi.properties overrides
nifi.flowfile.repository.directory=/var/lib/nifi/flowfile
nifi.flowfile.repository.checkpoint.interval=2 mins
nifi.flowfile.repository.always.sync=false
nifi.swap.manager.implementation=org.apache.nifi.controller.FileSystemSwapManager
nifi.queue.swap.threshold=50000
nifi.flowfile.repository.retain.orphaned.flowfiles=true
```

## Best Practices / Tips
<span id="claim-separate-content">Keep the FlowFile repository on different media from the content repository so that a content-disk exhaustion cannot corrupt FlowFile state.</span>

## Troubleshooting
<span id="claim-recovery">On restart the write-ahead repository reads WAL records, restores FlowFiles into their queues, manages orphaned entries, creates drop records for missing queues, and schedules a checkpoint once rehydration finishes.</span>  
<span id="claim-swap-temp-cleanup">Startup cleanup removes partial `.swap.part` files and skips unknown swap locations, logging manual cleanup guidance whenever the FlowFile repository cannot validate a swap file.</span>

## Reference / Related Docs
- <span id="claim-ref-admin">Administration Guide: FlowFile repository and swap management property tables.</span>
- <span id="claim-ref-wali">WriteAheadFlowFileRepository.java for implementation, property wiring, and recovery workflow.</span>
- <span id="claim-ref-swap">FlowFileSwapManager API for queue swap lifecycle semantics.</span>
