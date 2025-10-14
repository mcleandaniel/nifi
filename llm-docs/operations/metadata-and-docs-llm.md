# Flow Metadata & Documentation — LLM Notes

*Sources*: NiFi best-practice guidance scattered across user/admin guides and Apache community recommendations. Reviewed 2025-10-14.

## Why Capture Metadata?
- Communicate intent, ownership, and dependencies of each flow/process group.
- Speed onboarding and troubleshooting.
- Provide context for automation tools (e.g., deployment order, required services/parameters).

## Recommended Artefacts
- **README** per flow module:
  - Purpose, data sources/destinations.
  - Owners/contact.
  - Deployment instructions (parameter contexts, controller services, external systems).
- **Changelog / Migration Notes**:
  - Track significant updates, especially schema changes or new dependencies.
  - Align with NiFi Registry version comments for quick diffing.
- **Schema/Contract References**:
  - Link to Avro/JSON schemas, REST specs, database DDL.
  - Note validation expectations (e.g., record readers/writers).
- **External Dependencies**:
  - Required parameter contexts or controller services.
  - External systems (Kafka cluster, SFTP host) with environment-specific names.
- **Operational Runbooks**:
  - Start/stop order, rollback guidance, common failure signatures.
- **Security & Compliance Notes**:
  - Sensitive data handling, encryption requirements, access policies.

## Storage & Structure
- Co-locate metadata with flow specs (same directory) for discoverability.
- Use Markdown (for humans) plus machine-readable manifests (YAML/JSON) for automation.
- Maintain an index (e.g., `docs/flow-index.md`) that links flows to their modules and registry coordinates.

## Integration with Automation
- Deployment tooling can parse metadata manifests to:
  - Ensure required parameters/controller services exist.
  - Register flows with correct registry buckets.
  - Generate release notes or compliance reports automatically.
- Provide hooks for CI (lint README, validate manifests) to keep documentation current.

## Tips
- Establish templates for README/manifests to standardize content.
- Encourage developers to update metadata alongside flow changes (pre-commit checks help).
- When importing third-party templates or subflows, annotate differences and local customizations.

## Related Topics
- Flow spec structure discussion (`docs/flow-spec-structure.md`).
- Test fixtures & validation (`llm-docs/operations/test-fixtures-llm.md`).
