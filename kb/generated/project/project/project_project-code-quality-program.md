Created a verified doc with precise anchors and runnable examples.

- File: llm-docs/quality-gates-and-continuous-verification.md
- Focus: linting (RAT, Checkstyle, PMD), coverage aggregation/publication (JaCoCo + Codecov), and CI job structure across OS/JDK/locale.
- Verification: Every factual sentence wrapped in claim spans; YAML maps claims to exact line ranges in:
  - .github/workflows/code-compliance.yml
  - .github/workflows/code-coverage.yml
  - .github/workflows/ci-workflow.yml
  - pom.xml (contrib-check, Checkstyle/PMD config)
  - nifi-code-coverage/pom.xml (JaCoCo aggregate)

Highlights
- Static analysis gates:
  - contrib-check profile runs RAT at validate, Checkstyle at validate, PMD at compile.
  - CodeQL init/analyze and PMD check executed in code-compliance “Scan”.
  - SPDX SBOM generation and Anchore scan; build fails on main for fixed, medium+ issues.
- Coverage:
  - report-code-coverage profile runs JaCoCo report-aggregate at verify.
  - Codecov upload from nifi-code-coverage/target/site/jacoco-aggregate/jacoco.xml.
- CI structure:
  - Concurrency enabled; verify uses -D dir-only.
  - Jobs: Ubuntu (JDK 21), Ubuntu (JDK 25), macOS (JP locale), Windows (FR locale), each running verify (with python-unit-tests where specified).

Want me to add a short badge/README pointer to this doc or expand with a local “make-like” script to reproduce the workflows end-to-end?
