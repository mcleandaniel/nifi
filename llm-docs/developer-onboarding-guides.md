---
title: Developer Onboarding Guides
topic_id: project_project-developer-onboarding
category: development
claims:
  claim-java21-required:
    - source: admin-guide
      locator: "L81-L81"
  claim-standard-build-command:
    - source: developer-guide
      locator: "L2714-L2717"
  claim-maven-profiles-overview:
    - source: developer-guide
      locator: "L2698-L2710"
  claim-maven-git-used:
    - source: developer-guide
      locator: "L2727-L2729"
  claim-nar-packages:
    - source: developer-guide
      locator: "L2410-L2416"
  claim-nifi-nar-plugin-required:
    - source: developer-guide
      locator: "L2418-L2420"
  claim-nar-plugin-snippet:
    - source: developer-guide
      locator: "L2435-L2437"
  claim-custom-dist-mirrors-note:
    - source: admin-guide
      locator: "L79-L79"
  claim-custom-dist-build-steps:
    - source: admin-guide
      locator: "L83-L87"
  claim-start-windows:
    - source: getting-started
      locator: "L77-L78"
  claim-start-linux-foreground:
    - source: getting-started
      locator: "L86-L88"
  claim-start-linux-background:
    - source: getting-started
      locator: "L90-L91"
  claim-wait-for-init-flag:
    - source: getting-started
      locator: "L93-L95"
  claim-default-creds-generated:
    - source: getting-started
      locator: "L102-L105"
  claim-change-single-user-creds:
    - source: getting-started
      locator: "L109-L111"
  claim-ui-url-default:
    - source: getting-started
      locator: "L113-L116"
  claim-self-signed-expiry:
    - source: getting-started
      locator: "L117-L120"
  claim-agents-programmatic-workflows:
    - source: agents-handbook
      locator: "L3-L3"
  claim-agents-no-manual-env-vars:
    - source: agents-handbook
      locator: "L4-L4"
  claim-agents-focused-workflow:
    - source: agents-handbook
      locator: "L5-L5"
  claim-agents-skim-automation-readme:
    - source: agents-handbook
      locator: "L6-L6"
  claim-automation-uses-httpx-typer:
    - source: automation-readme
      locator: "L7-L9"
  claim-automation-requirements:
    - source: automation-readme
      locator: "L12-L13"
  claim-automation-venv-setup:
    - source: automation-readme
      locator: "L17-L23"
  claim-automation-install-editable:
    - source: automation-readme
      locator: "L25-L28"
  claim-automation-env-vars:
    - source: automation-readme
      locator: "L30-L35"
  claim-automation-cli-examples:
    - source: automation-readme
      locator: "L37-L44"
  claim-automation-run-tests:
    - source: automation-readme
      locator: "L46-L50"
  claim-automation-integration-script:
    - source: automation-readme
      locator: "L52-L58"
  claim-automation-local-nifi-docker:
    - source: automation-readme
      locator: "L66-L77"
  claim-automation-base-url-assumption:
    - source: automation-readme
      locator: "L80-L80"
  claim-clean-deploy-purge:
    - source: automation-readme
      locator: "L113-L118"
  claim-clean-deploy-deploy:
    - source: automation-readme
      locator: "L119-L125"
sources:
  - id: developer-guide
    title: Apache NiFi Developer Guide (Asciidoc)
    url: nifi-docs/src/main/asciidoc/developer-guide.adoc
  - id: getting-started
    title: Getting Started with Apache NiFi (Asciidoc)
    url: nifi-docs/src/main/asciidoc/getting-started.adoc
  - id: admin-guide
    title: Apache NiFi Administration Guide (Asciidoc)
    url: nifi-docs/src/main/asciidoc/administration-guide.adoc
  - id: agents-handbook
    title: Agent Handbook
    url: AGENTS.md
  - id: automation-readme
    title: NiFi REST Automation (Phase 1) README
    url: automation/README.md
---

# Developer Onboarding Guides

## Introduction / Overview

- <span id="claim-java21-required">Use Java 21 to build and run NiFi.</span>
- <span id="claim-maven-git-used">NiFi builds with Apache Maven and uses Git for version control.</span>
- <span id="claim-standard-build-command">Run the standard build with `mvn clean install -Pcontrib-check`.</span>
- <span id="claim-maven-profiles-overview">Optional Maven profiles add capabilities such as Hadoop, IoTDB, ASN.1, Graph, Media, QuestDB, Snowflake, and SQL Reporting, plus `contrib-check` for contribution validations.</span>

## Concepts / Architecture

- <span id="claim-nar-packages">Deploy NiFi extensions as NAR packages.</span>
- <span id="claim-nifi-nar-plugin-required">Package NAR artifacts using the `nifi-nar-maven-plugin`.</span>
- <span id="claim-nar-plugin-snippet">The root POM configures the NAR plugin; child modules inherit it.</span>
- <span id="claim-custom-dist-mirrors-note">Binary distributions from mirrors omit some NARs; enable profiles to include extras.</span>

## Implementation / Configuration

- <span id="claim-custom-dist-build-steps">Build a custom distribution from `nifi-assembly` using the Maven wrapper and desired profiles (example shows gRPC, Graph, and Media).</span>
  - Example:
    - `cd nifi-assembly`
    - `./mvnw clean install -Pinclude-grpc,include-graph,include-media`

## Usage / Examples

Build and verify locally

- <span id="claim-standard-build-command">Build the full project with contribution checks using `mvn clean install -Pcontrib-check`.</span>
- <span id="claim-maven-profiles-overview">Activate optional profiles (e.g., `-Pinclude-hadoop`, `-Pinclude-media`) to include additional bundles in the build.</span>

Run a built NiFi

- <span id="claim-start-windows">On Windows, run `bin\nifi.cmd start` from the installation `bin` directory.</span>
- <span id="claim-start-linux-foreground">On Linux/macOS, run `bin/nifi.sh run` to start in the foreground and stop with Ctrl-C.</span>
- <span id="claim-start-linux-background">Run `bin/nifi.sh start` to start in the background and use `bin/nifi.sh status` or `bin/nifi.sh stop` to manage the service.</span>
- <span id="claim-wait-for-init-flag">Use `bin/nifi.sh start --wait-for-init <seconds>` to wait for component scheduling before the script exits.</span>
- <span id="claim-default-creds-generated">A default installation generates a random username and password and writes them to `logs/nifi-app.log`.</span>
- <span id="claim-change-single-user-creds">Change single-user credentials with `bin/nifi.sh set-single-user-credentials <username> <password>`.</span>
- <span id="claim-ui-url-default">Open the UI at `https://localhost:8443/nifi` (default port 8443, configurable in `conf/nifi.properties`).</span>
- <span id="claim-self-signed-expiry">The default self-signed certificate is intended for development and expires after 60 days.</span>

Automation CLI (repo tooling)

- <span id="claim-agents-programmatic-workflows">Prefer scripted, programmatic flows for repeatability.</span>
- <span id="claim-agents-no-manual-env-vars">Avoid asking contributors to set shell variables manually when scripts can do it.</span>
- <span id="claim-agents-focused-workflow">When repeated attempts fail, switch to a focused, test-first workflow.</span>
- <span id="claim-agents-skim-automation-readme">When working under `automation/`, skim `automation/README.md` before running commands.</span>
- <span id="claim-automation-uses-httpx-typer">The automation CLI uses `httpx` with TLS configuration and a Typer-based interface with subcommands.</span>
- <span id="claim-automation-requirements">Use Python 3.13 and `uv` for local CLI development.</span>
- <span id="claim-automation-venv-setup">Create and activate the per-project virtual environment in `automation/`.</span>
- <span id="claim-automation-install-editable">Install the package in editable mode with dev tooling.</span>
- <span id="claim-automation-env-vars">Configure NiFi connection via `NIFI_BASE_URL`, `NIFI_USERNAME`, and `NIFI_PASSWORD` environment variables or the repo `.env`.</span>
- <span id="claim-automation-cli-examples">Run `nifi-automation auth-token` and `nifi-automation flow-summary` to validate connectivity.</span>
- <span id="claim-automation-run-tests">Run unit tests with `pytest`.</span>
- <span id="claim-automation-integration-script">Run the integration suite with `scripts/run_integration_suite.sh`.</span>
- <span id="claim-automation-local-nifi-docker">For integration tests, run a local NiFi 2.x container exposing 8443 with single-user credentials.</span>
- <span id="claim-automation-base-url-assumption">Integration tests assume `https://localhost:8443/nifi-api` and the configured single-user credentials.</span>
- <span id="claim-clean-deploy-purge">Purge the root group and controller services before each deploy using the provided purge script.</span>
- <span id="claim-clean-deploy-deploy">Deploy flows via `nifi-automation deploy-flow` or scripts under `automation/scripts/`.</span>

## Best Practices / Tips

- <span id="claim-standard-build-command">Run `-Pcontrib-check` locally to surface required quality checks before contributing.</span>
- <span id="claim-maven-git-used">Use Maven for builds and Git for branch and change management.</span>
- <span id="claim-nar-packages">Package extensions as NARs to ensure correct classloading and isolation.</span>
- <span id="claim-agents-programmatic-workflows">Script your local setup steps to reduce drift and speed reviews.</span>

## Troubleshooting

- <span id="claim-java21-required">If builds fail early, verify that Java 21 is installed and active.</span>
- <span id="claim-custom-dist-mirrors-note">If components seem missing in a binary, rebuild with the appropriate Maven profiles enabled.</span>
- <span id="claim-default-creds-generated">After first start, locate generated credentials in `logs/nifi-app.log`.</span>
- <span id="claim-ui-url-default">If the UI does not load, confirm port 8443 and the `nifi.properties` configuration.</span>
- <span id="claim-self-signed-expiry">Replace the self-signed certificate for long-lived or production use cases.</span>

## Reference / Related Docs

- <span id="claim-maven-profiles-overview">Developer Guide – Build Options and Maven Profiles.</span>
- <span id="claim-standard-build-command">Developer Guide – Standard Build Instructions.</span>
- <span id="claim-custom-dist-build-steps">Administration Guide – Build a Custom Distribution.</span>
- <span id="claim-start-linux-background">Getting Started – Starting NiFi.</span>
- <span id="claim-default-creds-generated">Getting Started – Default credentials and changing them.</span>
- <span id="claim-agents-skim-automation-readme">Repo – automation/README.md for local CLI setup and workflows.</span>
