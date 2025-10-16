# Flow Metadata & Documentation — LLM Notes

*Sources*: NiFi best-practice guidance scattered across user/admin guides and Apache community recommendations. Reviewed 2025-10-14. [1]

## Why Capture Metadata?
- Communicate intent, ownership, and dependencies of each flow/process group. [?1]
- Speed onboarding and troubleshooting. [?2]
- Provide context for automation tools (e.g., deployment order, required services/parameters). [?3]

## Recommended Artefacts
- **README** per flow module:
  - Purpose, data sources/destinations. [?4]
  - Owners/contact. [?4]
  - Deployment instructions (parameter contexts, controller services, external systems). [?4]
- **Changelog / Migration Notes**:
  - Track significant updates, especially schema changes or new dependencies. [?5]
  - Align with NiFi Registry version comments for quick diffing. [2]
- **Schema/Contract References**:
  - Link to Avro/JSON schemas, REST specs, database DDL. [?6]
  - Note validation expectations (e.g., record readers/writers). [?6]
- **External Dependencies**:
  - Required parameter contexts or controller services. [?7]
  - External systems (Kafka cluster, SFTP host) with environment-specific names. [?7]
- **Operational Runbooks**:
  - Start/stop order, rollback guidance, common failure signatures. [?8]
- **Security & Compliance Notes**:
  - Sensitive data handling, encryption requirements, access policies. [?9]

## Storage & Structure
- Co-locate metadata with flow specs (same directory) for discoverability. [?10]
- Use Markdown (for humans) plus machine-readable manifests (YAML/JSON) for automation. [?11]
- Maintain an index (e.g., `docs/flow-index.md`) that links flows to their modules and registry coordinates. [?12]

## Integration with Automation
- Deployment tooling can parse metadata manifests to:
  - Ensure required parameters/controller services exist. [?13]
  - Register flows with correct registry buckets. [?13]
  - Generate release notes or compliance reports automatically. [?13]
- Provide hooks for CI (lint README, validate manifests) to keep documentation current. [?14]

## Tips
- Establish templates for README/manifests to standardize content. [?15]
- Encourage developers to update metadata alongside flow changes (pre-commit checks help). [?16]
- When importing third-party templates or subflows, annotate differences and local customizations. [?17]

## Related Topics
- Flow spec structure discussion (`docs/flow-spec-structure.md`).
- Test fixtures & validation (`llm-docs/operations/test-fixtures-llm.md`).

---
## References
[1] General software development best practices.
[2] `nifi-frontend/src/main/frontend/apps/nifi/src/app/pages/flow-designer/ui/canvas/items/flow/save-version-dialog/save-version-dialog.component.html`

## Claims without references
[?1] General software development best practice.
[?2] General software development best practice.
[?3] General software development best practice.
[?4] General software development best practice.
[?5] General software development best practice.
[?6] General software development best practice.
[?7] General software development best practice.
[?8] General software development best practice.
[?9] General software development best practice.
[?10] General software development best practice.
[?11] General software development best practice.
[?12] General software development best practice.
[?13] General software development best practice.
[?14] General software development best practice.
[?15] General software development best practice.
[?16] General software development best practice.
[?17] General software development best practice.
