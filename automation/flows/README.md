# Flow Build (groups‑md → NiFi_Flow_groups.yaml)

This folder contains flow specifications and the source-of-truth for building the
aggregate grouped flow YAML.

Status: experimental (under active development)
- The split‑MD “groups” workflow is not yet the primary deployment path.
- For any tests or processes exercising the wider solution, continue to use:
  - `automation/flows/NiFi_Flow.yaml` (aggregate)
  - `automation/flows/*.yaml` (single‑flow specs)
- Do not deploy the grouped output yet. Treat it as a build artifact for future work.

Key paths
- `automation/flows/groups-md/` – per-group Markdown files and per‑workflow YAML fragments
  - `Group_*.md` – group name (H1), description (first paragraph), membership via `nifidesc` blocks
  - `<GroupName>/flows/<WorkflowName>.yaml` – YAML fragments for each child process group
- `automation/flows/groups-md/NiFi_Flow_groups.yaml` – generated grouped aggregate (output)
- `automation/flows/NiFi_Flow.yaml` – legacy aggregate (not modified by this pipeline)

Important: tools that read Markdown in this folder must ignore any file named `README.md`.

Build: groups‑md → grouped YAML
- One‑time seed (during migration from single‑flow specs):
  - `python automation/scripts/seed_groups_yaml_from_single_flows.py \
     --md-dir automation/flows/groups-md \
     --flows-dir automation/flows \
     --out-md-dir automation/flows/groups-md`
- Build grouped YAML from groups‑md only:
  - `python automation/scripts/build_groups_yaml_from_md.py \
     --md-dir automation/flows/groups-md \
     --out automation/flows/groups-md/NiFi_Flow_groups.yaml \
     --root-name "NiFi Flow"`

Authoring phases (MD → stub → YAML → deploy)
- Write group docs in `groups-md/*.md` (H1 name, paragraph description, and `nifidesc` blocks per workflow).
- Generate stubs from MD (one command creates per‑workflow YAML files):
  - `python automation/scripts/generate_stubs_from_md.py --md-dir automation/flows/groups-md --out-md-dir automation/flows/groups-md --phase draft`
  - Each fragment starts as a stub:
    ```yaml
    name: MyWorkflow
    phase: draft
    description: |
      Overview: …
      Technical: …
    processors: []
    connections: []
    ```
- Fill the stub (human or LLM) into a full child PG spec (keep `phase: ready` when done).
- Build the grouped YAML from fragments (see commands above). Do not deploy this
  grouped file yet; continue deploying `NiFi_Flow.yaml` until group support is wired into the deployer.

Guidelines
- Keep group membership and descriptions in per‑group MD under `groups-md/`.
- Store finalized per‑workflow YAML fragments under `groups-md/<Group>/flows/` (phase: ready).
- The builder assembles the grouped output from `groups-md/` only; it does not read `automation/flows/*.yaml`.
- Inline `yaml` in MD is a fallback for early drafts — prefer fragment files for ongoing maintenance.

Parameter hints in Markdown (optional)
- You can add a `nifiparams` fenced block to a group MD file to declare parameters anticipated for workflows in that group. Example:
  ```
  ```nifiparams
  - name: API_URL
    description: Base endpoint
    sensitive: false
    scope: pg
    used_by:
      - processor: InvokeHTTP
        property: Remote URL
  - name: API_TOKEN
    description: Token for upstream service
    sensitive: true
    source: vault:kv/data/upstream#token
  ```
  ```
- These hints guide humans or LLMs when expanding stubs and can be consumed by the CLI parameter planner in the future.

Controller service Markdown (optional registry)
- Keep controller service docs under `automation/flows/controllers-md/` (one file per service). Example fenced block:
  ```
  ```controller-service
  name: ExampleHttpClient
  type: org.apache.nifi.processors.standard.InvokeHTTP
  description: Client to call Example API
  parameters:
    - name: EXAMPLE_USER
      sensitive: false
      source: vault:kv/data/example#user
    - name: EXAMPLE_PASSWORD
      sensitive: true
      source: vault:kv/data/example#password
  ```
  ```
- In flow YAML, you may add `doc_refs: ["controllers-md/ExampleHttpClient.md"]` at PG or component level. This is metadata only for now and helps readers locate credentials/usage.

Troubleshooting
- Missing fragment: the builder prints `[warn] flow '<Name>' not found in groups-md; inserting stub`.
- Unexpected membership: verify the `nifidesc` blocks have `name: <WorkflowName>` matching the fragment filenames.
- Build reproducibility: run the builder from repository root and commit both the MD and fragment changes.
