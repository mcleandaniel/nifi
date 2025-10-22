# Flow Spec Build Pipeline (Groups MD → Grouped YAML)

This document defines the current and target processes for building the grouped
NiFi flow specification from Markdown. The goal is to make `groups-md/` the
single source-of-truth, avoiding direct reads of `automation/flows/*.yaml` in
the builder pipeline.

Status: experimental (under development)
- For end‑to‑end tests and day‑to‑day deployment, keep using `automation/flows/NiFi_Flow.yaml`
  and `automation/flows/*.yaml` until the deployer is group‑aware.
- The grouped output is a build artifact for future work and should not be deployed yet.

## Source of Truth

- Group metadata and ordering live in per‑group Markdown files under
  `automation/flows/groups-md/*.md`. Each file must include:
  - H1 header: group name
  - First paragraph: group description
  - One or more fenced `nifidesc` blocks with `name: <WorkflowName>` to list
    the workflows belonging to the group (order preserved).
- Per‑workflow YAML fragments live under
  `automation/flows/groups-md/<GroupName>/flows/<WorkflowName>.yaml`.
  These fragments contain each child process group spec (processors, connections,
  auto-terminate, etc.).

## Build (Current)

1. Seed fragments (one-time or as needed during migration):
   - Use existing single‑flow specs under `automation/flows/*.yaml` to seed
     per‑workflow fragments into `groups-md/` based on the group membership
     declared in the group Markdown files:
   - Command:
     - `python automation/scripts/seed_groups_yaml_from_single_flows.py \
        --md-dir automation/flows/groups-md \
        --flows-dir automation/flows \
        --out-md-dir automation/flows/groups-md`

2. Build grouped YAML from `groups-md/` (write under the groups‑md folder):
   - Command:
     - `python automation/scripts/build_groups_yaml_from_md.py \
        --md-dir automation/flows/groups-md \
        --out automation/flows/groups-md/NiFi_Flow_groups.yaml \
        --root-name "NiFi Flow"`
    - This assembles a single `NiFi_Flow_groups.yaml` using only `groups-md/`:
      - Group names/descriptions/ordering from the `.md` files
      - Child specs from `groups-md/<Group>/flows/*.yaml`
      - (Optional) Parameter hints from `nifiparams` blocks in group MD may be used by tooling in future to plan parameter contexts
   - `NiFi_Flow.yaml` is not modified by this pipeline.

## Target (After Migration)

- Authors add/update:
  - Group files in `groups-md/*.md` (membership via `nifidesc` blocks)
  - (Optional) Parameter hints in `nifiparams` blocks in group MD
  - (Optional) Controller service docs in `automation/flows/controllers-md/*.md`
  - Generate YAML stubs from MD:
    - `python automation/scripts/generate_stubs_from_md.py --md-dir automation/flows/groups-md --out-md-dir automation/flows/groups-md --phase draft`
  - Per‑workflow fragments in `groups-md/<Group>/flows/*.yaml` (edit stubs to full specs; set `phase: ready`)
- The builder (`build_groups_yaml_from_md.py`) remains the only tool used to
  generate the grouped aggregate. It never reads `automation/flows/*.yaml`.

## Optional Inline YAML (Fallback)

- For convenience during early authoring, the builder can also extract a
  `yaml` fenced block from a workflow’s section in the group `.md` when a
  fragment file is missing. This is a fallback. The recommended structure is
  to keep YAML in fragment files under `groups-md/<Group>/flows/`.

## Relationship to test-workflow-suite.md

- High‑level documentation and diagrams remain in
  `automation/flows/test-workflow-suite.md`.
- Descriptions inside individual YAML specs are kept in sync using
  `automation/scripts/sync_descriptions.py`; `groups-md` files remain the
  grouping source and do not need to duplicate all details.

## Commands Summary

- Seed (one-time migration):
  - `python automation/scripts/seed_groups_yaml_from_single_flows.py --md-dir automation/flows/groups-md --flows-dir automation/flows --out-md-dir automation/flows/groups-md`
- Build grouped YAML:
- `python automation/scripts/build_groups_yaml_from_md.py --md-dir automation/flows/groups-md --out automation/flows/groups-md/NiFi_Flow_groups.yaml --root-name "NiFi Flow"`
