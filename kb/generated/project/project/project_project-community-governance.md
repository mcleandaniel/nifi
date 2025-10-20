I added a verified, publication-ready governance doc with precise claim mappings.

- File: llm-docs/verified/community-and-asf-governance.md

Highlights
- Covers contributor onboarding (JIRA → PR flow, branch/commit expectations), licensing duties (ALv2 compatibility, LICENSE/NOTICE updates), and ASF governance channels (mailing lists, Slack, notifications).
- Every verifiable statement is wrapped in spans and mapped to local authoritative sources (README.md, .asf.yaml, LICENSE, NOTICE, SECURITY.md, PR template) with exact line locators; the ASF Code of Conduct is referenced with a precise section anchor.
- Includes runnable examples: git branch/commit flow and `./mvnw clean install -T1C -P contrib-check` builds.
- Clarifies key obligations from Apache License 2.0 Sections 4 and 5; shows where PRs must reference JIRA and be squashed.

Notable claims (examples)
- Issues tracked in Apache JIRA (NIFI) and GitHub Issues disabled. 
- PRs must start with a JIRA ticket and include the issue key in the PR title and commits.
- Verify changes with Maven Wrapper and `contrib-check`, including JDK 21/25 builds.
- New dependencies must be ALv2-compatible and documented in LICENSE/NOTICE.
- Use security@nifi.apache.org for vulnerability reports (PMC-monitored).
- ASF Code of Conduct governs behavior; follow reporting guidelines.

Want me to add a short README link to this doc or tailor it for the website build?
