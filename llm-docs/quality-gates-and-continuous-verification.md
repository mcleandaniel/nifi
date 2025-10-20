---
title: Quality Gates and Continuous Verification
claims:
  - id: claim-code-compliance-triggers
    sources: [ghwf-code-compliance-triggers]
  - id: claim-code-compliance-validate-os
    sources: [ghwf-code-compliance-os]
  - id: claim-code-compliance-validate-java
    sources: [ghwf-code-compliance-java]
  - id: claim-code-compliance-validate-cmd
    sources: [ghwf-code-compliance-validate-cmd]
  - id: claim-contrib-profile-rat
    sources: [pom-contrib-check-rat]
  - id: claim-contrib-profile-checkstyle
    sources: [pom-contrib-check-checkstyle, pom-checkstyle-config]
  - id: claim-contrib-profile-pmd
    sources: [pom-contrib-check-pmd, pom-pmd-config]
  - id: claim-scan-codeql
    sources: [ghwf-code-compliance-scan-codeql-init, ghwf-code-compliance-codeql-analyze]
  - id: claim-scan-pmd
    sources: [ghwf-code-compliance-scan-pmd]
  - id: claim-sbom-generate
    sources: [ghwf-code-compliance-sbom-generate]
  - id: claim-sbom-scan-fail-build
    sources: [ghwf-code-compliance-sbom-scan]
  - id: claim-code-coverage-triggers
    sources: [ghwf-code-coverage-triggers]
  - id: claim-coverage-build
    sources: [ghwf-code-coverage-maven-cmd]
  - id: claim-coverage-codecov
    sources: [ghwf-code-coverage-codecov-upload]
  - id: claim-coverage-aggregate-profile
    sources: [nificc-profile-jacoco-aggregate]
  - id: claim-ci-triggers
    sources: [ghwf-ci-triggers]
  - id: claim-ci-concurrency
    sources: [ghwf-ci-concurrency]
  - id: claim-ci-verify-env
    sources: [ghwf-ci-verify-command-env]
  - id: claim-ci-ubuntu21
    sources: [ghwf-ci-ubuntu21-job, ghwf-ci-ubuntu21-verify]
  - id: claim-ci-jdk25
    sources: [ghwf-ci-jdk25-job, ghwf-ci-jdk25-verify]
  - id: claim-ci-macos-locale
    sources: [ghwf-ci-macos-locale]
  - id: claim-ci-windows-locale
    sources: [ghwf-ci-windows-locale]
  - id: claim-code-compliance-validate-cmd-example
    sources: [ghwf-code-compliance-validate-cmd]
  - id: claim-scan-pmd-example
    sources: [ghwf-code-compliance-scan-pmd]
  - id: claim-scan-codeql-ci
    sources: [ghwf-code-compliance-scan-codeql-init, ghwf-code-compliance-codeql-analyze]
  - id: claim-coverage-build-example
    sources: [ghwf-code-coverage-maven-cmd]
  - id: claim-coverage-codecov-path
    sources: [ghwf-code-coverage-codecov-upload]
  - id: claim-ci-verify-env-example
    sources: [ghwf-ci-verify-command-env]
sources:
  - id: ghwf-code-compliance-triggers
    title: GitHub Actions Workflow — code-compliance triggers
    url: .github/workflows/code-compliance.yml
    locator: "L18-L23"
  - id: ghwf-code-compliance-os
    title: GitHub Actions Workflow — code-compliance Validate runner
    url: .github/workflows/code-compliance.yml
    locator: "L45-L45"
  - id: ghwf-code-compliance-java
    title: GitHub Actions Workflow — code-compliance Java setup
    url: .github/workflows/code-compliance.yml
    locator: "L49-L54"
  - id: ghwf-code-compliance-validate-cmd
    title: GitHub Actions Workflow — code-compliance Validate command
    url: .github/workflows/code-compliance.yml
    locator: "L55-L63"
  - id: ghwf-code-compliance-scan-codeql-init
    title: GitHub Actions Workflow — code-compliance CodeQL init
    url: .github/workflows/code-compliance.yml
    locator: "L78-L81"
  - id: ghwf-code-compliance-codeql-analyze
    title: GitHub Actions Workflow — code-compliance CodeQL analyze
    url: .github/workflows/code-compliance.yml
    locator: "L95-L96"
  - id: ghwf-code-compliance-scan-pmd
    title: GitHub Actions Workflow — code-compliance PMD check
    url: .github/workflows/code-compliance.yml
    locator: "L87-L94"
  - id: ghwf-code-compliance-sbom-generate
    title: GitHub Actions Workflow — code-compliance SBOM generation
    url: .github/workflows/code-compliance.yml
    locator: "L99-L106"
  - id: ghwf-code-compliance-sbom-scan
    title: GitHub Actions Workflow — code-compliance SBOM scan
    url: .github/workflows/code-compliance.yml
    locator: "L107-L113"
  - id: ghwf-code-coverage-triggers
    title: GitHub Actions Workflow — code-coverage triggers
    url: .github/workflows/code-coverage.yml
    locator: "L18-L25"
  - id: ghwf-code-coverage-maven-cmd
    title: GitHub Actions Workflow — code-coverage Maven + JaCoCo
    url: .github/workflows/code-coverage.yml
    locator: "L59-L64"
  - id: ghwf-code-coverage-codecov-upload
    title: GitHub Actions Workflow — code-coverage Codecov upload
    url: .github/workflows/code-coverage.yml
    locator: "L65-L70"
  - id: nificc-profile-jacoco-aggregate
    title: nifi-code-coverage POM — report-code-coverage profile
    url: nifi-code-coverage/pom.xml
    locator: "L1590-L1604"
  - id: pom-contrib-check-rat
    title: Root POM — contrib-check runs RAT at validate
    url: pom.xml
    locator: "L1171-L1179"
  - id: pom-contrib-check-checkstyle
    title: Root POM — contrib-check runs Checkstyle at validate
    url: pom.xml
    locator: "L1182-L1201"
  - id: pom-contrib-check-pmd
    title: Root POM — contrib-check runs PMD at compile
    url: pom.xml
    locator: "L1203-L1214"
  - id: pom-checkstyle-config
    title: Root POM — Checkstyle plugin configuration
    url: pom.xml
    locator: "L1038-L1045"
  - id: pom-pmd-config
    title: Root POM — PMD plugin configuration
    url: pom.xml
    locator: "L1059-L1070"
  - id: ghwf-ci-triggers
    title: GitHub Actions Workflow — ci-workflow triggers
    url: .github/workflows/ci-workflow.yml
    locator: "L16-L18"
  - id: ghwf-ci-concurrency
    title: GitHub Actions Workflow — ci-workflow concurrency
    url: .github/workflows/ci-workflow.yml
    locator: "L48-L50"
  - id: ghwf-ci-verify-command-env
    title: GitHub Actions Workflow — ci-workflow verify command
    url: .github/workflows/ci-workflow.yml
    locator: "L39-L46"
  - id: ghwf-ci-ubuntu21-job
    title: GitHub Actions Workflow — Ubuntu JDK 21 job
    url: .github/workflows/ci-workflow.yml
    locator: "L58-L61"
  - id: ghwf-ci-ubuntu21-verify
    title: GitHub Actions Workflow — Ubuntu JDK 21 job verify
    url: .github/workflows/ci-workflow.yml
    locator: "L114-L116"
  - id: ghwf-ci-jdk25-job
    title: GitHub Actions Workflow — Ubuntu JDK 25 job
    url: .github/workflows/ci-workflow.yml
    locator: "L130-L161"
  - id: ghwf-ci-jdk25-verify
    title: GitHub Actions Workflow — Ubuntu JDK 25 job verify
    url: .github/workflows/ci-workflow.yml
    locator: "L186-L189"
  - id: ghwf-ci-macos-locale
    title: GitHub Actions Workflow — macOS JP locale verify
    url: .github/workflows/ci-workflow.yml
    locator: "L249-L264"
  - id: ghwf-ci-windows-locale
    title: GitHub Actions Workflow — Windows FR locale verify
    url: .github/workflows/ci-workflow.yml
    locator: "L321-L336"
---

# Quality Gates and Continuous Verification

## Introduction / Overview

<span id="claim-code-compliance-triggers">The `code-compliance` workflow runs on manual dispatch, a daily schedule, pull requests, and pushes.</span>

<span id="claim-code-coverage-triggers">The `code-coverage` workflow runs on manual dispatch, a daily schedule, and pull requests that touch its workflow file.</span>

<span id="claim-ci-triggers">The main `ci-workflow` runs on both `push` and `pull_request` events.</span>

These workflows provide complementary gates: static analysis and license/style checks, security scanning, coverage aggregation and publication, and multi‑platform verification.

## Concepts / Architecture

<span id="claim-code-compliance-validate-os">The `code-compliance` Validate job runs on `ubuntu-24.04`.</span>

<span id="claim-code-compliance-validate-java">The Validate job sets up Java 21 (Zulu distribution) with Maven caching.</span>

<span id="claim-code-compliance-validate-cmd">The Validate step executes Maven `validate` with the `contrib-check` profile.</span>

<span id="claim-contrib-profile-rat">The `contrib-check` profile runs `apache-rat-plugin:check` in the `validate` phase.</span>

<span id="claim-contrib-profile-checkstyle">The `contrib-check` profile runs `maven-checkstyle-plugin:check` at `validate`, with project and test sources configured and Checkstyle plugin configured globally to use `checkstyle.xml`.</span>

<span id="claim-contrib-profile-pmd">The `contrib-check` profile runs `maven-pmd-plugin:check` during `compile`, with the PMD plugin configured globally to include tests and use `pmd-ruleset.xml`.</span>

<span id="claim-scan-codeql">The `code-compliance` Scan job initializes CodeQL for Java and performs analysis.</span>

<span id="claim-scan-pmd">The Scan job runs `pmd:check` (with tests skipped) before packaging.</span>

<span id="claim-sbom-generate">The Scan job generates an SPDX JSON SBOM for the assembled binary using `anchore/sbom-action`.</span>

<span id="claim-sbom-scan-fail-build">The SBOM is scanned with `anchore/scan-action`, and the build fails on the `main` branch for medium‑severity (or higher) issues that have available fixes.</span>

<span id="claim-coverage-aggregate-profile">The `nifi-code-coverage` module defines a `report-code-coverage` profile that runs `jacoco-maven-plugin:report-aggregate` in the `verify` phase.</span>

<span id="claim-coverage-build">The `code-coverage` workflow builds with `jacoco:prepare-agent` and `verify`, activating `integration-tests` and `report-code-coverage` profiles.</span>

<span id="claim-coverage-codecov">Aggregated coverage is uploaded to Codecov from `nifi-code-coverage/target/site/jacoco-aggregate/jacoco.xml`.</span>

<span id="claim-ci-concurrency">The CI workflow enforces concurrency by grouping on workflow and ref and canceling in‑progress runs.</span>

<span id="claim-ci-verify-env">The CI environment sets `MAVEN_VERIFY_COMMAND` to `verify` with common flags and `-D dir-only`.</span>

<span id="claim-ci-ubuntu21">One CI job named “Ubuntu Corretto JDK 21 EN” runs on `ubuntu-24.04` and executes Maven Verify with `-P python-unit-tests`.</span>

<span id="claim-ci-jdk25">A second Linux job uses Corretto JDK 25 on `ubuntu-24.04` and also verifies with `-P python-unit-tests`.</span>

<span id="claim-ci-macos-locale">A macOS job uses Zulu JDK 21 and runs tests with Japanese locale and timezone settings applied via Surefire and environment overrides, verifying with `-P python-unit-tests`.</span>

<span id="claim-ci-windows-locale">A Windows job uses Zulu JDK 21 and runs tests with French locale and the `Europe/Paris` timezone applied via Surefire and environment overrides.</span>

## Implementation / Configuration

- Contrib checks (Maven):
  - Activate locally using `--activate-profiles contrib-check` or `-P contrib-check`.
  - Plugins/phases:
    - RAT check at `validate` (license headers).
    - Checkstyle check at `validate` (project + test sources).
    - PMD check at `compile`.

- Static analysis (workflows):
  - CodeQL init + analyze in Scan job.
  - PMD check (`pmd:check`) executed in Scan job.

- SBOM + vulnerability scan:
  - SPDX SBOM generated for the assembled binary.
  - Anchore scan enforces failure on `main` for medium‑severity issues with fixes.

- Coverage aggregation:
  - JaCoCo `report-aggregate` at `verify` through the `report-code-coverage` profile.
  - Codecov upload from the aggregated XML report path.

- CI execution model:
  - Concurrency enabled to avoid redundant runs per ref.
  - `MAVEN_VERIFY_COMMAND` includes `-D dir-only` and common flags.
  - Jobs cover multiple OS/JDK/locale combinations to surface cross‑environment issues.

## Usage / Examples

- Validate contributors’ checks (local mirror of the Validate step):

  <span id="claim-code-compliance-validate-cmd-example">Run: `./mvnw --show-version --no-snapshot-updates --no-transfer-progress --fail-fast --activate-profiles contrib-check validate`</span>

- Run Scan‑job equivalents locally:

  <span id="claim-scan-pmd-example">PMD check: `./mvnw --show-version --no-snapshot-updates --no-transfer-progress --fail-fast -DskipTests pmd:check package`</span>

  <span id="claim-scan-codeql-ci">CodeQL is initialized and analyzed in CI (see workflow for exact action usage).</span>

- Produce aggregated coverage + upload artifact path:

  <span id="claim-coverage-build-example">Coverage build: `./mvnw --fail-fast --no-snapshot-updates --no-transfer-progress --show-version -D include-python-integration-tests=true -P integration-tests -P report-code-coverage jacoco:prepare-agent verify`</span>

  <span id="claim-coverage-codecov-path">Coverage XML: `nifi-code-coverage/target/site/jacoco-aggregate/jacoco.xml`</span>

- CI verify configuration:

  <span id="claim-ci-verify-env-example">`MAVEN_VERIFY_COMMAND` includes `verify --show-version --no-snapshot-updates --no-transfer-progress --fail-fast -D dir-only`</span>

## Best Practices / Tips

- Run `./mvnw -P contrib-check validate` before pushing to catch RAT/Checkstyle/PMD issues early.
- Keep license headers consistent to satisfy RAT; use repo templates where applicable.
- Ensure tests are locale‑agnostic; CI runs with Japanese and French locales to catch assumptions.
- When adding modules, wire them into `nifi-code-coverage` aggregation so coverage remains representative.
- For performance, mirror CI flags locally (`--no-transfer-progress`, `--fail-fast`) when iterating.

## Troubleshooting

- Checkstyle/PMD failures: open the reported files and use `checkstyle.xml`/`pmd-ruleset.xml` as the source of truth.
- RAT failures: add/fix license headers and re‑run `-P contrib-check validate`.
- Missing coverage XML: ensure you ran `jacoco:prepare-agent` with `-P report-code-coverage` and `verify`.
- SBOM scan failures: reproduce locally by building the assembly and scanning the generated SPDX file with Anchore CLI/tools.

## Reference / Related Docs

- .github/workflows/code-compliance.yml:18-23
- .github/workflows/code-compliance.yml:45
- .github/workflows/code-compliance.yml:49-54
- .github/workflows/code-compliance.yml:55-63
- .github/workflows/code-compliance.yml:78-81
- .github/workflows/code-compliance.yml:87-96
- .github/workflows/code-compliance.yml:99-106
- .github/workflows/code-compliance.yml:107-113
- .github/workflows/code-coverage.yml:18-25
- .github/workflows/code-coverage.yml:59-64
- .github/workflows/code-coverage.yml:65-70
- nifi-code-coverage/pom.xml:1590-1604
- pom.xml:1038-1045
- pom.xml:1059-1070
- pom.xml:1171-1179
- pom.xml:1182-1201
- pom.xml:1203-1214
- .github/workflows/ci-workflow.yml:16-18
- .github/workflows/ci-workflow.yml:39-46
- .github/workflows/ci-workflow.yml:48-50
- .github/workflows/ci-workflow.yml:58-61
- .github/workflows/ci-workflow.yml:114-116
- .github/workflows/ci-workflow.yml:130-161
- .github/workflows/ci-workflow.yml:186-189
- .github/workflows/ci-workflow.yml:249-264
- .github/workflows/ci-workflow.yml:321-336
