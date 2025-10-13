# NiFi Toolkit CLI — LLM Notes

*Source*: `nifi-docs/src/main/asciidoc/toolkit-guide.adoc` (reviewed 2025-10-13)

## Purpose
- Command-line toolkit that automates NiFi and NiFi Registry administration: deploy flows, manage process groups, services, users, parameters, bundles, assets, etc.
- Supports both one-off commands (non-interactive) and an interactive shell with tab completion and back-references.

## CLI Basics
- Launch single command: `./bin/cli.sh <command> <args>`
- Enter interactive shell: `./bin/cli.sh`
- Help output: `./bin/cli.sh -h` or `<command> help`
- Command groups: `nifi`, `registry`, `session`, `demo`, `exit`, `help`.
- Hundreds of subcommands exist; highlight categories:
  - **Cluster control**: `nifi cluster-summary`, `connect-node`, `disconnect-node`, `offload-node`.
  - **Process groups**: `pg-list`, `pg-import`, `pg-start`, `pg-change-version`, `pg-get-services`, `pg-set-param-context`.
  - **Controller services/tasks**: `get-services`, `create-service`, `enable-services`, `get-reporting-tasks`, `create-reporting-task`.
  - **Versioned flows & Registry**: `registry list-buckets`, `create-bucket`, `list-flows`, `list-flow-versions`, `export-all-flows`, `import-all-flows`.
  - **Parameters & providers**: `list-param-contexts`, `create-param-context`, `merge-param-context`, `list-param-providers`, `fetch-params`.
  - **Security/auth**: `list-users`, `create-user`, `get-policy`, `update-policy`, `get-access-token`, `logout-access-token`.
  - **Bundles/Assets**: `upload-nar`, `delete-nar`, `create-asset`, `add-asset-reference`.

## Configuration Handling
- Most commands require `-u/--baseUrl`. Avoid repetition by using properties files with keys like `baseUrl`, `keystore`, `truststore`, etc.
- Supply properties per command (`-p /path/config.properties`) or set session defaults:
  - `./bin/cli.sh session set nifi.props /path/nifi.properties`
  - `./bin/cli.sh session set nifi.reg.props /path/registry.properties`
- Argument resolution order: CLI flag > `-p` properties file > session defaults (stored in `~/.nifi-cli.config`).

## Security & TLS
- CLI supports mutual TLS authentication and optional `proxiedEntity` header.
- Properties file fields:
  ```
  baseUrl=https://host:port
  keystore=/path/client.jks
  keystoreType=JKS
  keystorePasswd=*****
  keyPasswd=*****
  truststore=/path/truststore.jks
  truststoreType=JKS
  truststorePasswd=*****
  proxiedEntity=user@REALM (optional)
  ```
- Use proxied entity when the CLI is run with server certificates but commands should execute as another principal (requires NiFi/NiFi Registry proxy permissions).

## Interactive Mode Features
- Tab completion suggests commands, subcommands, and filesystem paths.
- Output types: `--outputType simple|json` (default `simple` in interactive mode, `json` in standalone).
- Back-references: use `&<position>` to reuse IDs from previous command results (`registry list-flows -b &1`).

## Export/Import Utilities
- `registry export-all-flows`: iterates buckets → flows → versions, writing snapshots to a target directory.
- `registry import-all-flows`: recreates buckets, flows, versions from export directory (`--input`, optional `--skipExisting`).
- Use cases:
  - Reconfigure an existing Registry (export, change persistence provider, import with `--skipExisting`).
  - Replicate data between registries for DR (export from source, import to destination).

## Extending the CLI
- Add custom NiFi commands by subclassing `AbstractNiFiCommand`; registry commands extend `AbstractNiFiRegistryCommand`.
- Register new command in `NiFiCommandGroup` or `NiFiRegistryCommandGroup`.

## LLM Answer Tips
- For automation questions, highlight relevant commands and note requirement to include `-u` or configure sessions.
- When TLS/auth errors occur, suggest verifying keystore/truststore paths, passwords, and proxied entity settings.
- Emphasize back-references for interactive workflows to avoid manual copy/paste of UUIDs.
- For migrating registries, recommend `export-all-flows` → `import-all-flows` and mention `--skipExisting`.
- Advise setting `--outputType json` when scripts need machine-readable output.

## Quick FAQs
1. **Set default connection info?** → Use `session set nifi.props` / `session set nifi.reg.props` with properties file.
2. **Run a command against secured NiFi?** → Provide TLS keystore/truststore (either in properties or via CLI flags).
3. **Automate flow deployment?** → Combine `registry list-flows`, `registry list-flow-versions`, then `nifi pg-import` / `pg-change-version`.
4. **List registry buckets via script?** → `./bin/cli.sh registry list-buckets -ot json`.
5. **Add custom CLI command?** → Create class extending `AbstractNiFiCommand`, register in command group, rebuild toolkit.
