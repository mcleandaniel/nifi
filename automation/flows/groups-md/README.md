# Groups MD Structure

This folder contains grouped flow specifications and group metadata. The builder
script assembles a single aggregate YAML (`NiFi_Flow_groups.yaml`) from:

- Group metadata files: `Group_*.md`
  - H1 header = group name
  - First paragraph = group description
  - Optional: `nifiparams` block with parameter hints
- Group flow fragments: `<GroupName>/flows/*.yaml`
  - Each file is a child process group spec (name, processors, connections, etc.)
- Default (non-grouped) flow fragments: `*.yaml` placed directly under `groups-md/`
  - These become `process_group.process_groups` in the aggregate (the “default” set).

Aggregate generation
- Build the aggregate with:
  ```bash
  python automation/scripts/build_groups_yaml_from_md.py \
    --md-dir automation/flows/groups-md \
    --out automation/flows/groups-md/NiFi_Flow_groups.yaml \
    --root-name "NiFi Flow"
  ```
- The builder includes:
  - `process_group.process_groups` from YAMLs at `groups-md/*.yaml` (default flows)
  - `process_group.groups[*]` from `Group_*.md` with descriptions and flows from `<Group>/flows/*.yaml`

Local README policy
- Each folder should include a short `README.md` explaining what lives there and how to use it (inputs/outputs, scripts).
- Link to or from the parent README where appropriate.

