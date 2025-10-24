# Feature Design Documents

This folder collects concise, reviewable design docs for new features and substantial changes. The goal is to keep ideas scoped, decisions explicit, and implementation smooth.

## Workflow (lightweight but explicit)
- Propose: copy `docs/features/TEMPLATE.md` as `docs/features/YYYY-MM-DD-short-title.md`.
- Write: fill in Context, Goals/Non‑Goals, Proposal, Schema/API changes, Testing, Rollout, Risks, Open Questions.
- Review: open a PR; tag with `design` and request reviewers. Decisions are recorded in the doc’s Status section.
- Implement: link the doc from the PR(s) that implement it. Keep the doc updated if scope changes.
- Close loop: set Status to `Accepted` and later to `Implemented` once merged and verified.

### Issue tracking policy (single source of truth)
- Create a GitHub Issue to track status and cross-link PRs, but do not duplicate the doc’s contents in the issue body.
- The issue body should be a short pointer to the canonical doc (path in this repo). All updates happen in the doc, not in the issue.
- Optionally, a bot/Action can comment when the doc changes; until then, maintainers update the doc and add a brief comment to the issue.

## Naming and metadata
- Filenames: `YYYY-MM-DD-short-title.md` (UTC). Example: `2025-10-24-layout-orientation-toggle.md`.
- Top-of-file fields (required):
  - Status: Draft | Review | Accepted | Implemented | Rejected
  - Owner: GitHub handle(s)
  - Approvers: list of reviewers who must sign off
  - Links: issue/PR references

## Structure (recommended)
- Context
- Goals / Non‑Goals
- Current Architecture (as-is)
- Proposal (to-be)
  - API/Schema changes
  - Data model / config changes
  - Algorithms / components touched
- Migration / Compatibility
- Testing Plan
- Rollout Plan
- Risks & Mitigations
- Alternatives Considered
- Open Questions

## Tips
- Keep it 1–3 pages. Link to deeper notes if needed.
- Include concrete examples (YAML, CLI snippets) and success criteria.
- Prefer diagrams only when they clarify flow or dependencies.
