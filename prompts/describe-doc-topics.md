---
title: "Describe Repo Doc Topics (Project + Tools + Services, JSON Plans)"
description: "Analyze the repo and produce multiple JSON plans: one for the project itself, one per tool or tool-group, and one per detected service/runtime. Output to kb/plans/*.json with an index at kb/plans/index.json. Do not execute any scripts or read kb/."
author: "System Prompt Template"
version: "1.1"
---

## Objective

From the repository root:
- Discover documentation topics for the **project itself** (architecture, development, testing, security, deployment, ops, governance, etc.).
- Discover documentation topics for each **tool** shipped by this repo (CLIs, automation scripts, SDKs, extension packs), grouping tools where appropriate.
- Discover documentation topics for each **service/runtime** that this repo builds or deploys (servers, daemons, agents, long-running processes, APIs, webapps, containers).
- Write multiple machine-readable JSON plans suitable for programmatic fan-out into `/research-assistant`.

## Hard Rules

- Do NOT execute or import any scripts or programs.
- Do NOT read or transform any files under `kb/`.
- Write JSON files only to `kb/plans/`.
- Print nothing except the JSON file contents you write.
- All outputs must be valid UTF-8 JSON.
- If a runnable service/runtime is detected, you MUST write a dedicated service plan `kb/plans/service-<id>.json` and list it in `kb/plans/index.json` with `"kind": "service"`.

## Outputs

Create these files (overwriting if they exist):

### 1) `kb/plans/index.json`

Manifest listing all generated plans:

```json
{
  "version": "1",
  "generated_at": "<ISO8601 UTC>",
  "repo_root": ".",
  "plans": [
    {"id": "project", "path": "kb/plans/project.json", "kind": "project"},
    {"id": "service-main", "path": "kb/plans/service-main.json", "kind": "service"},
    {"id": "tool-core-cli", "path": "kb/plans/tool-core-cli.json", "kind": "tool"},
    {"id": "tool-automation-suite", "path": "kb/plans/tool-automation-suite.json", "kind": "tool-group"}
  ]
}
````

---

### 2) `kb/plans/project.json`

Topics about the project itself (20–40 total across architecture, development, testing, security, deployment, operations, governance, lifecycle, meta).

Schema:

```json
{
  "version": "1",
  "generated_at": "<ISO8601 UTC>",
  "repo_root": ".",
  "scope": "project",
  "topics": [
    {
      "id": "kebab-case-unique-id",
      "title": "Human Readable Title",
      "summary": "1–2 sentences of scope.",
      "category": "architecture|development|testing|security|deployment|operations|governance|data|ui|special|meta",
      "recommended_sources": ["src/", "docs/**/*.md", ".github/workflows/"],
      "dependencies": [],
      "priority": "high|medium|low",
      "tags": ["keywords"],
      "research_request": "Concise instruction for /research-assistant to generate this document."
    }
  ]
}
```

---

### 3) `kb/plans/tool-*.json`

Each file corresponds to a tool or tool-group (e.g., CLI family), focusing on how to use the tool (not how to build the project).

Schema (identical to project, with an additional `tool` object):

```json
{
  "version": "1",
  "generated_at": "<ISO8601 UTC>",
  "repo_root": ".",
  "scope": "tool",
  "tool": {
    "id": "tool-core-cli",
    "name": "Core CLI",
    "kind": "cli|sdk|bundle|automation",
    "entrypoints": ["automation/src/...", "toolkit/cli/"],
    "grouped_tools": ["tool-init-cli","tool-delete-cli"]  // optional
  },
  "topics": [ /* same topic schema as project */ ]
}
```

---

### 4) `kb/plans/service-*.json`

Each file corresponds to a **runtime service** (e.g., server, daemon, webapp, API, background agent, containerized service).

Schema (similar to project, with a `service` object):

```json
{
  "version": "1",
  "generated_at": "<ISO8601 UTC>",
  "repo_root": ".",
  "scope": "service",
  "service": {
    "id": "service-main",
    "name": "Primary Runtime Service",
    "kind": "service",
    "entrypoints": ["bin/start.sh","conf/app.properties","Dockerfile"],
    "ports": ["8080","8443"],
    "artifacts": ["*.tar.gz","Dockerfile","helm/"]
  },
  "topics": [ /* same topic schema as project */ ]
}
```

---

## Discovery Guidance

**Project scope** = how the product is designed, built, tested, secured, deployed, operated, and governed.
Examples to target: architecture overview, runtime topology, repositories, provenance, build/dependency management, CI/CD, testing, security, deployment, observability, support, backup/DR, upgrades, contribution, docs standards, glossary, roadmap.

**Tool scope** = how the repo’s tools are used by practitioners (commands, flags, config, workflows, examples, error handling, exit codes).

Detect tools by:

* CLI projects (e.g., `toolkit/cli/`, `automation/commands/`)
* SDKs or client libraries.
* Automation scripts under `automation/`, `scripts/`, `tools/`.
* Extension authoring toolchains (e.g., archetypes, plugin scaffolds).

Group tools when:

* Multiple commands share a UX (create/delete pairs).
* Shared packaging or README indicates a suite.

Each tool plan should include topics like:
Overview & Installation, Quickstart, Core Commands/APIs, Configuration & Profiles, Workflows/Recipes, Error Handling, Logging/Diagnostics, Integration Points, Security Considerations, Troubleshooting, Versioning.

---

**Service scope** = long-running software components (servers, daemons, APIs, containers) built or deployed by the repo.

Detect services by any of the following heuristics:

* Executable launch scripts (`bin/start.sh`, `bin/service.sh`, `run.sh`, `.bat`).
* Configuration files (`conf/*.properties`, `application.yml`, `bootstrap.conf`, `settings.xml`).
* Deployment assets (`Dockerfile`, `docker-compose.yml`, `Helm/`, `k8s/`, `charts/`, `systemd/`).
* Network exposure (`EXPOSE` lines, port configs, service.yaml, compose ports).
* Packaging modules (`*-assembly/`, `*-server/`, `*-runtime/`).
* Continuous or background nature (service process, agent, worker).

Examples of service topics:

* Install & Packaging
* Configuration & Secrets
* Runtime Architecture / Topology
* Networking & Ports
* Observability & Logging
* Scaling, HA, and Clustering
* Repositories / State Management
* Security Model
* Upgrade & Backup
* Extensions / Plugin Compatibility

If such patterns are detected, emit a service plan for each unique service runtime (e.g., `service-main`, `service-api`, `service-worker`).

---

## Repository Scan Scope

Start at `.`; ignore `kb/**`.

Examine:

* Source trees, modules, packages.
* Build/packaging files (`pom.xml`, `Makefile`, `Dockerfiles`, `setup.*`).
* CI/CD (`.github/workflows/`).
* IaC/infra (`Terraform`, `Helm`, `K8s` manifests).
* Docs (`docs/**/*.md`).
* Automation and script directories.

Use repo-relative paths only.
For directories, end with `/`.
For doc families, use globs like `docs/**/*.md`.

---

## Field Rules

* `id`: kebab-case, unique within each plan.
* `title`: concise and descriptive.
* `summary`: 1–2 sentences, specific and actionable.
* `category`: one of `architecture|development|testing|security|deployment|operations|governance|data|ui|special|meta`.
* `recommended_sources`: real paths/globs to guide `/research-assistant`; never include `kb/`.
* `dependencies`: optional topic id list.
* `priority`: high|medium|low.
* `tags`: 2–6 short keywords.
* `research_request`: standalone instruction string to feed `/research-assistant "{{research_request}}"`.

---

## Quality Controls

* Project plan: 20–40 topics covering full lifecycle.
* Each tool plan: 8–20 topics covering usage/config/workflows/troubleshooting.
* Each service plan: 10–25 topics covering runtime/deployment/security/ops.
* Topics must be disjoint and map to real files/dirs.
* Normalize paths: dirs end with `/`; use `**/*.md` for doc globs.
* No placeholders like “TBD”.
* All JSON valid; UTF-8.
* If service detection heuristics match but no service plan is emitted, still write `kb/plans/service-detection.json` summarizing evidence.

---

## Final Action

Write:

* `kb/plans/index.json`
* `kb/plans/project.json`
* `kb/plans/service-*.json` (one per detected service)
* `kb/plans/tool-*.json` (one per tool or tool-group)

Do not execute any scripts.
Do not read or transform `kb/`.
Write JSON only.

```
