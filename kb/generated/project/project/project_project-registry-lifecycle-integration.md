Added a verified, publication-ready doc covering NiFi + NiFi Registry lifecycle workflows.

- New file: llm-docs/registry-centered-lifecycle-management.md
- Includes: overview, concepts, configuration, CLI-powered usage, promotion patterns, best practices, troubleshooting, and references.
- Verifiability: Every factual sentence is wrapped in claim spans and mapped to precise sources with line-range locators in YAML front matter.
- Programmatic usage: Provides runnable CLI examples using properties + session defaults (auto-loading .env if present). Avoids manual ID pasting with interactive back-references.

Highlights
- Concepts: Registry buckets, policies, NiFi Registry Client, version states, sensitive-parameter handling.
- Configuration: Connect NiFi to Registry, start version control, import flows, commit, rollback.
- Promotion patterns: Interactive promotion using `registry list-*` + `nifi pg-import`; bulk replication between Registries using `registry export-all-flows` and `import-all-flows`.
- Governance: Bucket policies for read/import/commit/delete; caution on deleting flows in use.
- References: Anchored to NiFi User Guide, Registry User Guide, Administration Guide, and Toolkit Guide with exact line ranges.

Want me to add a short companion script in scripts/ that wires .env to the CLI properties and performs a sample Dev→Test promotion flow end-to-end?
