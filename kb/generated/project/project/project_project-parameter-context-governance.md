Added an annotated, verifiable doc covering creation, scoping, versioning, and automation hooks for Parameter Contexts.

Where to find it
- llm-docs/parameter-context-governance.md

What’s inside
- Introduction and concepts with precise syntax, escaping, inheritance, sensitive constraint, and EL evaluation.
- Implementation with API references and security policies.
- Runnable REST examples for creating contexts, assigning to process groups, and fetching/applying via Parameter Providers.
- Best practices for versioned flow promotion and environment handling.
- Troubleshooting for common issues.
- YAML front matter with claim-to-source mappings and exact locators into official NiFi docs and Java sources in this repo.

Highlights (all claims mapped to sources)
- Global scope and assignment constraints for Parameter Contexts.
- Parameter syntax `#{...}`, escaping `##`, and quoting support for names.
- Inheritance precedence and version increment semantics.
- Sensitive property rules and stop/disable behavior during updates.
- REST endpoints: /parameter-contexts, /process-groups/{id}, /parameter-providers/{id}/parameters/fetch-requests, /apply-parameters-requests.
- Versioned flows: storage of names and metadata, merge-by-name import, and no local-change for param context operations.

Want me to add a small script to automate create/assign/fetch/apply flows using your `.env` settings?
