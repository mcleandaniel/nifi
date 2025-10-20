Added a verified, publication-ready Markdown doc covering BOM roles, update workflows, and policies.

- File: llm-docs/bom-and-dependency-governance.md
- Structure: Introduction, Concepts/Architecture, Implementation/Configuration, Usage/Examples, Best Practices, Troubleshooting, Reference
- Verification: Every claim annotated with spans and mapped to precise file+line locators in YAML
- Sources: Local POMs (nifi-bom, nifi-extension-bom, root pom.xml, bundle BOMs/NARs, assembly POM)

Highlights
- Explains how nifi-bom governs core NiFi artifacts as provided and how nifi-extension-bom layers Jetty/EE dependencies as provided to align extensions.
- Shows aggregator modules inheriting nifi-extension-bom to keep versions consistent across bundles.
- Details the shared BOM/NAR pattern (e.g., nifi-standard-shared-bom and nifi-standard-shared-nar; service APIs via nifi-standard-services-api-bom and nifi-standard-services-api-nar).
- Maps version governance to root pom properties and vendor BOM imports (Jetty, SLF4J, Jackson).
- Provides scripted update workflows and POM examples aligned to the repository patterns.

Want me to add a short “how to validate changes locally” section (limited-scope mvn commands) or expand the policy section with more bundle-specific examples?
