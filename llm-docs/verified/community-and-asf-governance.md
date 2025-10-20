---
title: Community and ASF Governance
claims:
  - id: claim-project-issues-jira
    sources: [src-readme-contacts, src-asf-yaml-jira]
  - id: claim-github-issues-disabled
    sources: [src-asf-yaml-features]
  - id: claim-pr-jira-linking
    sources: [src-pr-template-issue-tracking, src-pr-template-title-commit]
  - id: claim-pr-branch-one-commit
    sources: [src-pr-template-branch-one-commit]
  - id: claim-build-maven-wrapper
    sources: [src-readme-developing-maven-wrapper]
  - id: claim-build-contrib-check
    sources: [src-readme-contrib-check, src-pr-template-build-contrib-check]
  - id: claim-pr-jdk-versions
    sources: [src-pr-template-build-contrib-check]
  - id: claim-licensing-new-deps-policy
    sources: [src-pr-template-licensing]
  - id: claim-license-apache-2
    sources: [src-readme-license-section]
  - id: claim-license-section5-contributions
    sources: [src-license-section5]
  - id: claim-license-section4-redistribution
    sources: [src-license-section4]
  - id: claim-notice-file-present
    sources: [src-notice-top]
  - id: claim-security-mailing-list
    sources: [src-security-reporting]
  - id: claim-security-pmc-monitors
    sources: [src-security-reporting]
  - id: claim-security-disclosure-policy
    sources: [src-security-policy]
  - id: claim-community-contacts-channels
    sources: [src-readme-contacts, src-readme-community-slack]
  - id: claim-notifications-mailing-lists
    sources: [src-asf-yaml-notifications]
  - id: claim-walkthroughs-jira-pr
    sources: [src-walkthroughs-contribute]
  - id: claim-asf-code-of-conduct-followed
    sources: [src-asf-coc]
sources:
  - id: src-readme-contacts
    url: README.md
    locator: "L39-L44"
  - id: src-readme-community-slack
    url: README.md
    locator: "L46-L49"
  - id: src-readme-developing-maven-wrapper
    url: README.md
    locator: "L117-L119"
  - id: src-readme-contrib-check
    url: README.md
    locator: "L131-L136"
  - id: src-readme-license-section
    url: README.md
    locator: "L208-L223"
  - id: src-pr-template-issue-tracking
    url: .github/PULL_REQUEST_TEMPLATE.md
    locator: "L24-L24"
  - id: src-pr-template-title-commit
    url: .github/PULL_REQUEST_TEMPLATE.md
    locator: "L28-L29"
  - id: src-pr-template-branch-one-commit
    url: .github/PULL_REQUEST_TEMPLATE.md
    locator: "L33-L34"
  - id: src-pr-template-build-contrib-check
    url: .github/PULL_REQUEST_TEMPLATE.md
    locator: "L42-L44"
  - id: src-pr-template-licensing
    url: .github/PULL_REQUEST_TEMPLATE.md
    locator: "L46-L49"
  - id: src-asf-yaml-features
    url: .asf.yaml
    locator: "L23-L26"
  - id: src-asf-yaml-jira
    url: .asf.yaml
    locator: "L31-L32"
  - id: src-asf-yaml-notifications
    url: .asf.yaml
    locator: "L33-L37"
  - id: src-license-section4
    url: LICENSE
    locator: "L90-L120"
  - id: src-license-section5
    url: LICENSE
    locator: "L131-L137"
  - id: src-notice-top
    url: NOTICE
    locator: "L1-L5"
  - id: src-security-reporting
    url: SECURITY.md
    locator: "L42-L43"
  - id: src-security-policy
    url: SECURITY.md
    locator: "L47-L50"
  - id: src-walkthroughs-contribute
    url: nifi-docs/src/main/asciidoc/walkthroughs.adoc
    locator: "L27-L27"
  - id: src-asf-coc
    url: https://www.apache.org/foundation/policies/conduct.html
    locator: "#reporting-guidelines"
---

# Community and ASF Governance

## Introduction / Overview

<span id="claim-project-issues-jira">Apache NiFi tracks issues in the Apache JIRA under the NIFI project.</span> <span id="claim-github-issues-disabled">GitHub Issues are disabled for this repository.</span> <span id="claim-license-apache-2">The project is licensed under the Apache License, Version 2.0.</span>

<span id="claim-community-contacts-channels">Community communication happens on the dev and users mailing lists and in the community Slack workspace.</span> <span id="claim-asf-code-of-conduct-followed">Project spaces follow the ASF Code of Conduct; concerns should be reported per the policy’s reporting guidelines.</span>

## Concepts / Architecture

- <span id="claim-pr-jira-linking">Each contribution should start with an Apache NiFi JIRA issue and link that issue in the pull request title and commit message.</span>
- <span id="claim-pr-branch-one-commit">Pull requests should be based on `main` and use a feature branch with a single squashed commit.</span>
- <span id="claim-build-maven-wrapper">Development uses the Maven Wrapper to run builds without requiring a separate Maven installation.</span>
- <span id="claim-build-contrib-check">Builds should include the `contrib-check` profile to run static analysis and confirm code and licensing compliance.</span>
- <span id="claim-pr-jdk-versions">The verification checklist includes building with JDK 21 and JDK 25.</span>
- <span id="claim-licensing-new-deps-policy">New dependencies must be compatible with the Apache License 2.0 according to the Apache Legal policy and must be recorded in project `LICENSE` and `NOTICE` files.</span>
- <span id="claim-notice-file-present">The repository includes a `NOTICE` file acknowledging ASF provenance and third‑party attributions.</span>
- <span id="claim-notifications-mailing-lists">Repository notifications send commits and pull request updates to project mailing lists.</span>

## Implementation / Configuration

- Create a JIRA: Use the NIFI project in Apache JIRA and capture scope and acceptance criteria. <span id="claim-walkthroughs-jira-pr">Project docs reference opening a JIRA and submitting a pull request for contributions.</span>
- Branch and title: Create a feature branch named after the issue (for example, `NIFI-12345-feature`) and title the PR with the issue key, e.g., `NIFI-12345: Short description`. <span id="claim-pr-jira-linking">Include the issue key at the beginning of the commit message.</span>
- Build and validate locally:
  ```shell
  ./mvnw clean install -T1C -P contrib-check
  ```
  <span id="claim-build-maven-wrapper">This uses the Maven Wrapper provided in the repository.</span> <span id="claim-build-contrib-check">The `contrib-check` profile runs static and license checks.</span>
- JDK verification: Build with supported JDKs before opening a PR. <span id="claim-pr-jdk-versions">The PR checklist enumerates JDK 21 and JDK 25.</span>
- Licensing updates: When adding dependencies, verify compatibility and update `LICENSE` and `NOTICE` as required. <span id="claim-licensing-new-deps-policy">The PR template lists these licensing duties explicitly.</span>

## Usage / Examples

- Example branch and commit:
  ```shell
  git checkout -b NIFI-12345-add-processor
  # ... make changes ...
  git add -A
  git commit -m "NIFI-12345: Add new processor with docs and tests"
  git push origin NIFI-12345-add-processor
  ```
  <span id="claim-pr-branch-one-commit">Submit the PR as a single, squashed commit based on `main`.</span>

- Example build and compliance check:
  ```shell
  ./mvnw clean install -T1C -P contrib-check
  ```
  <span id="claim-build-contrib-check">Use this profile to confirm code style and licensing compliance before opening a PR.</span>

- Example issue linkage in PR title and commit: `NIFI-12345: Improve logging in XYZ processor`. <span id="claim-pr-jira-linking">PR titles and commit messages should start with the JIRA key.</span>

## Best Practices / Tips

- Keep PRs focused and reviewable, and prefer a single squashed commit. <span id="claim-pr-branch-one-commit">The repository’s PR template documents this expectation.</span>
- Always run `contrib-check` locally before pushing to reduce CI churn. <span id="claim-build-contrib-check">This ensures license and static checks pass.</span>
- Verify third‑party licenses early and update attributions. <span id="claim-licensing-new-deps-policy">New dependencies must be ALv2‑compatible and listed in `LICENSE` and `NOTICE`.</span>
- Use project channels for design discussions and help. <span id="claim-community-contacts-channels">Mailing lists and Slack are the primary community venues.</span>

## Troubleshooting

- Licensing check failures: Inspect dependency licenses and update `LICENSE`/`NOTICE` as needed. <span id="claim-license-section4-redistribution">Apache License 2.0 Section 4 describes NOTICE and attribution requirements for redistribution.</span>
- Contribution terms: Remember that intentional submissions are under ALv2 by default. <span id="claim-license-section5-contributions">Apache License 2.0 Section 5 governs submission of contributions.</span>
- Security reports: Do not file vulnerabilities in public trackers; use the private security list. <span id="claim-security-mailing-list">Send reports to security@nifi.apache.org.</span> <span id="claim-security-pmc-monitors">The PMC monitors the list and responds to disclosures.</span>

## Reference / Related Docs

- <span id="claim-project-issues-jira">Issue tracking and contacts are linked from the project README.</span>
- <span id="claim-notifications-mailing-lists">ASF repository settings route notifications to mailing lists.</span>
- <span id="claim-security-disclosure-policy">NiFi follows ASF vulnerability disclosure guidance and announces resolved issues to standard channels.</span>
- <span id="claim-license-apache-2">License: Apache License, Version 2.0.</span>
- <span id="claim-notice-file-present">Attribution: Project NOTICE file.</span>

