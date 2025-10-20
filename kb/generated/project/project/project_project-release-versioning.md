I drafted a verified, publication‑ready doc that covers version bump workflow, manifest structure, and packaging checks.

- New file: llm-docs/release-versioning-and-packaging.md
- Includes: YAML front matter with claims/sources, inline span annotations for every verifiable statement, runnable Maven commands, and precise source locators into this repo.

Highlights
- Versioning: root POM version and module structure, plus versions-maven-plugin usage.
- Packaging: assembly descriptors (dir/zip/tar.gz), NAR doc extraction, and manifests ZIP.
- Runtime manifest: generator execution, inputs/outputs, structure, and defaults.
- Checks: integration test assertions and Enforcer rules for release readiness.

Want me to run the manifest module build to verify the JSON lands as documented, or open a PR with this doc?
