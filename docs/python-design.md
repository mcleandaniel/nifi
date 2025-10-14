## Recommended Guides & Articles

| Title                                                         | What it covers / what’s good about it                                              | Notes                                                               |
| ------------------------------------------------------------- | ---------------------------------------------------------------------------------- | ------------------------------------------------------------------- |
| *Structuring Your Project* (The Hitchhiker’s Guide to Python) | modules, package layout, imports, repo structure, tests                            | A well-known, practical starting point ([docs.python-guide.org][1]) |
| *How to Structure Python Projects* (Dagster blog)             | 9 best practices for structuring code, naming, version control, dependencies, etc. | Good “checklist / rules of thumb” format ([dagster.io][2])          |
| *Modern Good Practices for Python Development* (Stuart Ellis) | formatting, linting, type hints, test tools, packaging, dependency files           | Helps bring a “modern tooling” perspective ([stuartellis.name][3])  |
| *Implementing Robust App Architecture on Python*              | Hexagonal / Clean architecture, ports & adapters, DI, separation of concerns       | Useful for building maintainable modular systems ([shakuro.com][4]) |
| *Production-Level Coding Practices in Python*                 | general coding best practices (SoC, modularity, reuse)                             | Good for reminding of core principles ([Medium][5])                 |
| *Best Practices for Structuring a Python Project Like a Pro!* | conventional layout, modular code, DRY, env management, etc.                       | Good overview for standard (non-exotic) cases ([Medium][6])         |

---

## Key Principles & Patterns for Large Python Project Architecture

Here’s a distilled set of principles and patterns drawn from the guides above (and common industry practice). Use them as a guiding philosophy rather than rigid rules.

| Principle                                                       | Explanation / Rationale                                                                                                                                               | Common Pitfalls to Avoid                                                      |
| --------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------- |
| **Separation of Concerns / Single Responsibility**              | Each module, class, function should have one reason to change. That helps keep code understandable and testable.                                                      | Overloading modules with unrelated responsibilities; tangled dependencies     |
| **Modular / Pluggable Design**                                  | You want to isolate subsystems (e.g. domain logic, data access, APIs) so they can evolve independently.                                                               | Tight coupling across layers; “God classes”                                   |
| **Clean / Hexagonal / Onion / Layered Architecture**            | Define clear interfaces (ports/adapters) between layers (e.g. domain → application → infrastructure) so that core business logic doesn’t depend on framework details. | Business logic leaking framework code; circular dependencies                  |
| **Dependency Injection / Inversion of Control**                 | Instead of code “pulling in” dependencies, inject them through constructors or factories. This aids testability and flexibility.                                      | Using global state or singletons everywhere; hard to mock or replace          |
| **Package / Module Structure Discipline**                       | Use a consistent and intuitive directory layout (e.g. `src/`, `app/`, `api/`, `services/`, `domain/`). Keep related code close; avoid deep nesting.                   | Scattering related code across many places; naming collisions                 |
| **Use Modern Tooling (linting, formatting, type checking, CI)** | Tools like Black (or Ruff), mypy / pyright, pytest, pre-commit, continuous integration pipelines help maintain code hygiene across a large team.                      | Neglecting consistency, letting “style wars” slow development                 |
| **Isolated Environments & Dependency Locking**                  | Use virtual environments, lock dependency versions (e.g. `poetry.lock`, `pip-tools` with hash verification)                                                           | Version conflicts, “works on my machine” problems                             |
| **Testing Strategy (unit, integration, contract, end-to-end)**  | Coverage across layers; mock external dependencies; enforce tests in CI                                                                                               | Insufficient test depth; brittle tests; dependencies that are not mockable    |
| **Incremental Refactoring / Evolution**                         | Recognize that you may need to reorganize code as requirements evolve (especially in a large codebase)                                                                | Trying to foresee all structure ahead of time; overengineering early          |
| **Documentation & Onboarding**                                  | Clear README, architecture docs (e.g. diagrams), module-level docstrings, design decision records (DDR)                                                               | Code-only “self-documenting” expectation; orphaned modules nobody understands |

---

## Example Skeleton Layout (Template)

Here’s an example of a “large-project” directory structure you can use as a starting point. You can adapt or rename parts according to your domain:

````
my_project/
├── pyproject.toml
├── README.md
├── LICENSE
├── docs/
│   └── architecture.md
├── src/
│   └── my_project/              ← main package root
│       ├── __init__.py
│       ├── cli/                 ← command line interface (if any)
│       ├── api/                 ← HTTP / RPC / external interface layer
│       ├── application/         ← use-case / orchestration logic
│       ├── domain/              ← core business logic / domain model
│       ├── infrastructure/      ← database, external APIs, persistence
│       ├── config/               ← config loading / environment
│       └── utils/                ← shared utilities & helpers
├── tests/
│   ├── unit/
│   ├── integration/
│   └── conftest.py
├── scripts/                      ← tooling, deployment, maintenance scripts
├── .github/ or .gitlab/           ← CI / workflows
└── .gitignore
```
### Where the NiFi automation CLI fits into this layout

The current repository mirrors much of the pattern above:

```
nifi/
├── automation/
│   ├── pyproject.toml
│   ├── README.md
│   ├── scripts/                       ← tooling (e.g., generate_component_lists.py)
│   └── src/nifi_automation/           ← main package
│       ├── __init__.py
│       ├── cli.py                     ← Typer entry points
│       ├── auth.py                    ← authentication logic
│       ├── client.py                  ← REST wrappers
│       ├── flow_builder.py            ← spec parsing & deployment orchestration
│       ├── config.py                  ← pydantic settings
│       └── ...
├── docs/
│   ├── automation-flow-builder.md     ← design overview for the CLI
│   ├── design-log.md                  ← chronological decision log
│   └── components/                    ← processor/controller inventories
└── ...
``

Key takeaways:
- Package code under `automation/src/nifi_automation/` aligns with the `src/` layout best practice.
- Supporting scripts live in `automation/scripts/`, mirroring the "scripts" directory concept.
- Architecture and decision docs reside in `docs/` alongside the code.
- Tests (currently unit-level) can grow parallel to `src/nifi_automation`, matching the recommended layout.



Some notes on the layout:

* Placing your code under `src/` helps avoid issues where test code accidentally imports from the project root directory rather than installed package.
* The separation `api / application / domain / infrastructure` is inspired by clean/hexagonal architecture.
* `tests/` is parallel to `src/` so that tests are clearly separated.
* `docs/` for architecture, design decisions, onboarding guides.
* You may include modules like `logging/`, `monitoring/`, `events/`, depending on cross-cutting concerns.

---

## Checklist for Reviewing / Improving a Large Python Project

Use this as a diagnostic when evaluating architecture or when scaling up:

1. Is there a single “core domain” part of the system, and is it isolated from framework details?
2. Are dependencies between modules mostly one way (high-level modules depend on lower-level ones) or are there circular dependencies?
3. Are interfaces (e.g. boundary abstractions) clearly defined and obeyed?
4. Is DI used (or at least inversion of control) so that implementations can be swapped or mocked?
5. Are type hints used (especially on public APIs) and are type checks (mypy, pyright) integrated?
6. Is there adequate test coverage across the layers (unit, integration)?
7. Do you have CI pipelines that enforce formatting, linting, testing?
8. Are configuration & secrets handled appropriately (environment variables, config files, no hardcoding)?
9. Are cross-cutting concerns (logging, error handling, metrics) handled in a consistent, centralized way?
10. Is there a documented architecture, with module diagrams and decision rationale?
11. Can new modules or features be plugged in without breaking existing systems?
12. Are dependency versions locked, and reproduction of builds guaranteed?
13. Is there a plan for evolving structure (e.g. refactoring, modularization) over time?

---


[1]: https://docs.python-guide.org/writing/structure/?utm_source=chatgpt.com "Structuring Your Project - The Hitchhiker's Guide to Python"
[2]: https://dagster.io/blog/python-project-best-practices?utm_source=chatgpt.com "How to Structure Python Projects - Dagster"
[3]: https://www.stuartellis.name/articles/python-modern-practices/?utm_source=chatgpt.com "Modern Good Practices for Python Development - Stuart Ellis"
[4]: https://shakuro.com/blog/app-architecture-on-python?utm_source=chatgpt.com "Implementing Robust App Architecture on Python - Shakuro"
[5]: https://medium.com/red-buffer/python-production-level-coding-practices-4c39246e0233?utm_source=chatgpt.com "Python: Production-Level Coding Practices | by Ahmad Sachal"
[6]: https://medium.com/the-pythonworld/best-practices-for-structuring-a-python-project-like-a-pro-be6013821168?utm_source=chatgpt.com "Best Practices for Structuring a Python Project Like a Pro! - Medium"

