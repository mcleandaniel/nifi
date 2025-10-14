# NiFi In Depth — LLM Notes

*Source*: `nifi-docs/src/main/asciidoc/nifi-in-depth.adoc` (reviewed 2025-10-13)

## Purpose
- Explains low-level NiFi internals: FlowFile model, repository design, content claims, queueing, provenance lineage.
- Helps reason about performance, durability, and failure recovery beyond surface configuration.

## Key Topics
- **FlowFile Abstraction**: Immutable record combining pointer to content with attribute map and provenance chain; supports copy-on-write semantics.
- **Repositories**:
  - *FlowFile Repository*: Write-Ahead Log (WAL) of FlowFile metadata; snapshots plus deltas enable crash recovery.
  - *Content Repository*: Stores actual bytes in claim files; optimized for sequential IO and archiving.
  - *Provenance Repository*: Tracks lineage events (RECEIVE, SEND, CLONE, DROP, etc.) for replay and audit.
- **Content Claims & Resource Claims**: FlowFiles reference claims; content writes append to `.partial` files, atomically swapped when synchronized; Resource Claim Manager tracks reference counts and cleanup/archival policy.
- **Memory vs Disk**: Active FlowFiles map held in JVM heap, while repositories persist metadata/content to disk for resilience.
- **Life of a FlowFile**:
  - Ingress creates FlowFile, attributes set, content claimed.
  - Processor interactions create provenance events, update repo deltas.
  - Relationships route FlowFiles; queue back pressure protects memory.
  - Egress triggers DROP event, releasing content claims post-checkpoint.
- **Failure Handling**: WAL ensures restart resumes from last acknowledged delta; archiving retains content for replay; checkpoints guard against claim deletion before metadata persisted.
- **Concurrency Model**: Sessions provide transactional boundary for FlowFile changes; references guard against premature content cleanup.
- **Data Association**: `ProvenanceReporter.associate()` pairs FlowFile UUIDs with external identifiers (e.g., filenames) to link multi-system flows.
- **Deletion Workflow**: After checkpoint, FlowFile repository signals Resource Claim Manager to free unreferenced claims; background threads enforce archive retention limits (`nifi.content.repository.archive.enabled`).
- **Site-to-Site & Backpressure Insights**: Discussion of load balancing, queue priorities, and how repository design supports high throughput while retaining durability.

## Practical Applications
- Diagnose repo corruption → check FlowFile WAL snapshots and ensure disk reliability; replay deltas if abrupt shutdown occurred.
- Size disks → allocate separate volumes for content vs flowfile/provenance; consider archiving retention to manage disk utilization.
- Understand replay → provenance plus content archiving enables resubmission of FlowFiles after downstream failure.
- Optimize performance → leverage immutable content references to avoid copying; ensure `nifi.content.repository.archive.enabled` aligns with retention needs.

## Cross-Doc Pointers
- **Administration Guide**: Uses repository knowledge when tuning disks, antivirus exclusions, and backup/restore processes.
- **Developer Guide**: Processor best practices (session commits, provenance reporting) rely on these repository behaviors.
- **User Guide**: Explains queue behavior and provenance UI built on these internals.

## Anticipated FAQs
1. *Why is NiFi designed around FlowFiles instead of raw files?* → FlowFiles enable metadata-rich routing, copy-on-write updates, and durable provenance.
2. *How does NiFi recover after a crash?* → FlowFile repo snapshots + WAL deltas rebuild state; content repo retains bytes; provenance restates lineage.
3. *When are content claims deleted?* → After FlowFile DROP, once checkpoints release claims and no other FlowFiles reference them, respecting archive settings.
4. *How can I link NiFi events with upstream IDs?* → Set `alternate.identifier` or call `ProvenanceReporter.associate()` to relate FlowFile UUID to external keys.
5. *Why is archiving optional?* → Archiving retains content for replay but consumes disk; disable when storage constrained or sensitive data should be purged immediately.
