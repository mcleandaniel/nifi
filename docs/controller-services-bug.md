# Controller Service Manifest Failures – Root Cause & Reference

## Why This Document Exists

The NiFi integration tests began failing as soon as we added `automation/flows/simple.yaml`. The failure occurred during the manifest reconciliation step, before any flow deployment began:

```
httpx.HTTPStatusError: Client error '400 Bad Request'
for url 'https://localhost:8443/nifi-api/controller-services/<uuid>'
body: Cannot modify configuration … state of ENABLING …
'Schema Access Strategy' validated against 'Infer Schema'
is invalid because 'Schema Access Strategy' is not a supported property …
```

Despite deleting and recreating the controller services, NiFi continually reported the services in `ENABLING/INVALID` state. The REST payload looked correct at first glance, but NiFi rejected it because we used **display names** (“Schema Access Strategy”, “Do Not Write Schema”) rather than the **canonical property keys and values** declared in the source. NiFi retains the invalid entries and refuses to exit ENABLING, which cascades into deployment failures and slow 400 responses.

This document captures:

* The **canonical property descriptors** for `JsonTreeReader` and `JsonRecordSetWriter`.
* Which properties are required, their default values, and the accepted canonical values.
* The dependencies that NiFi enforces (e.g., “Schema Name” requires a schema registry).
* The operational rule that controller services must be **disabled** before updating properties via REST.

With this reference, manifests can be generated without hitting the invalid-state loop again.

---

## Evidence Pulled From Source

| Component / File | What it defines |
| --- | --- |
| `nifi-extension-bundles/nifi-standard-services/nifi-record-serialization-services-bundle/nifi-record-serialization-services/src/main/java/org/apache/nifi/json/JsonTreeReader.java` | Adds JSON-specific descriptors such as `starting-field-strategy` and overrides schema access defaults. |
| `nifi-extension-bundles/nifi-standard-services/nifi-record-serialization-services-bundle/nifi-record-serialization-services/src/main/java/org/apache/nifi/json/JsonRecordSetWriter.java` | Defines writer-specific descriptors (`suppress-nulls`, `compression-format`, etc.). |
| `nifi-extension-bundles/nifi-extension-utils/nifi-record-utils/nifi-avro-record-utils/src/main/java/org/apache/nifi/serialization/SchemaRegistryService.java` | Base class for all record-aware controller services; declares shared schema access properties and validation logic. |
| `nifi-extension-bundles/nifi-extension-utils/nifi-record-utils/nifi-avro-record-utils/src/main/java/org/apache/nifi/serialization/SchemaRegistryRecordSetWriter.java` | Adds schema write strategy descriptors required by writer services. |
| `nifi-extension-bundles/nifi-standard-services/nifi-record-serialization-services-bundle/nifi-record-serialization-services/src/main/java/org/apache/nifi/serialization/DateTimeTextRecordSetWriter.java` | Adds optional date/time format properties inherited by JSON writer. |
| `nifi-extension-bundles/nifi-extension-utils/nifi-record-utils/nifi-avro-record-utils/src/main/java/org/apache/nifi/schema/access/SchemaAccessUtils.java` | Declares canonical `AllowableValue` instances and property descriptors for schema access strategies; the canonical values we must send over REST live here. |

All canonical property *names* (`PropertyDescriptor::name`) and allowable value *values* (`AllowableValue::value`) come straight from these classes.

---

## Canonical Property Reference – JsonTreeReader

`JsonTreeReader` extends `SchemaRegistryService`, so it inherits all base schema properties in addition to JSON-specific ones.

### Shared Schema Access Properties (from `SchemaRegistryService`)

| Canonical Key | Display Name (UI) | Required | Default | Allowable Values (canonical → display) | Notes / Dependencies |
| --- | --- | --- | --- | --- | --- |
| `schema-access-strategy` | Schema Access Strategy | ✔ | `schema-name` (**Use 'Schema Name' Property**) | `schema-name`, `schema-text-property`, `schema-reference-reader` | Determines which other properties are required. |
| `schema-registry` | Schema Registry | depends | — | Controller service ref | Required when strategy is `schema-name` **or** `schema-reference-reader`. |
| `schema-name` | Schema Name | depends | `${schema.name}` | Free-form string | Requires strategy `schema-name`; EL supported. |
| `schema-version` | Schema Version | optional | — | Free-form string | Only valid with strategy `schema-name`; mutually exclusive with `schema-branch`. |
| `schema-branch` | Schema Branch | optional | — | Free-form string | Same constraints as version. |
| `schema-text` | Schema Text | depends | `${avro.schema}` | Avro schema text | Requires strategy `schema-text-property`; EL supported. |
| `schema-reference-reader` | Schema Reference Reader | depends | — | Controller service ref | Requires strategy `schema-reference-reader`. |

### JsonTreeReader-Specific Properties

| Canonical Key | Display Name | Required | Default | Allowable Values (canonical → display) | Notes |
| --- | --- | --- | --- | --- | --- |
| `schema-inference-cache` | Schema Inference Cache | optional | — | Controller service ref (`RecordSchemaCacheService`) | Only appears when strategy `infer` (Infer from Result) is selected. |
| `starting-field-strategy` | Starting Field Strategy | ✔ | `ROOT_NODE` → “Root Node” | `ROOT_NODE`, `NESTED_FIELD` | Controls whether parsing begins at root or nested field. |
| `starting-field-name` | Starting Field Name | depends | — | Free-form string | Required when strategy is `NESTED_FIELD`. |
| `schema-application-strategy` | Schema Application Strategy | ✔ | `SELECTED_PART` → “Selected Part” | `SELECTED_PART`, `WHOLE_JSON` | Only meaningful when schema references nested fields. |
| `flowfile-attribute-cache` (via schema cache builder) | Schema Cache | optional | — | Controller service ref | Added to allow caching inferred schemas. |
| `max-string-length` | Max String Length | ✔ | `20 MB` | Any data size | Controls streaming constraints. |
| `allow-comments` | Allow Comments | ✔ | `false` | `true`, `false` | Exposed via `AbstractJsonRowRecordReader`. |
| `date-format` | Date Format | optional | — | Java `DateTimeFormatter` pattern | Provided by `DateTimeUtils`. |
| `time-format` | Time Format | optional | — | Java pattern | — |
| `timestamp-format` | Timestamp Format | optional | — | Java pattern | — |

### Canonical Value Mapping Example

* UI “Infer Schema” → canonical value `infer` (see `SchemaAccessUtils.INFER_SCHEMA`).
* UI “Do Not Write Schema” → canonical value `no-schema`.

The manifest **must** use canonical values (`infer`, not “Infer Schema”).

---

## Canonical Property Reference – JsonRecordSetWriter

`JsonRecordSetWriter` extends `SchemaRegistryRecordSetWriter` → `SchemaRegistryService`, and adds writer-specific properties.

### Schema Write Strategy Properties (from `SchemaRegistryRecordSetWriter`)

| Canonical Key | Display Name | Required | Default | Allowable Values (canonical → display) | Dependencies & Notes |
| --- | --- | --- | --- | --- | --- |
| `Schema Write Strategy` | Schema Write Strategy | ✔ | `no-schema` → “Do Not Write Schema” | `no-schema`, `schema-name`, `full-schema-attribute`, `schema-reference-writer` | Descriptor is built with `.name("Schema Write Strategy")`, so the canonical key contains spaces. NiFi expects the canonical **values** listed here. |
| `Schema Cache` | Schema Cache | optional | — | Controller service ref (`RecordSchemaCacheService`) | Optional caching layer; no effect unless configured. |
| `Schema Reference Writer` | Schema Reference Writer | depends | — | Controller service ref (`SchemaReferenceWriter`) | Required when `Schema Write Strategy = schema-reference-writer`. |

The schema access properties inherited from `SchemaRegistryService` still apply, but `SchemaRegistryRecordSetWriter` narrows the allowable strategies to: `inherit-record-schema`, `schema-name`, `schema-text-property` and changes the default to `inherit-record-schema`.

### Date/Time Inheritance (from `DateTimeTextRecordSetWriter`)

| Canonical Key | Display Name | Required | Default | Notes |
| --- | --- | --- | --- | --- |
| `Date Format` | Date Format | optional | — | Optional `DateTimeFormatter` pattern. |
| `Time Format` | Time Format | optional | — | Optional `DateTimeFormatter` pattern. |
| `Timestamp Format` | Timestamp Format | optional | — | Optional `DateTimeFormatter` pattern. |

### JsonRecordSetWriter-Specific Properties

| Canonical Key | Display Name | Required | Default | Allowable Values (canonical → display) | Notes |
| --- | --- | --- | --- | --- | --- |
| `Pretty Print JSON` | Pretty Print JSON | ✔ | `false` | `true`, `false` | When set `true`, `output-grouping` must remain `output-array` (`JsonRecordSetWriter.java` custom validation). |
| `suppress-nulls` | Suppress Null Values | ✔ | `never-suppress` → “Never Suppress” | `never-suppress`, `always-suppress`, `suppress-missing` | Controls whether null or missing fields are written. |
| `Allow Scientific Notation` | Allow Scientific Notation | ✔ | `false` (migrated to `true` for legacy services) | `true`, `false` | Determines numeric formatting. |
| `output-grouping` | Output Grouping | ✔ | `output-array` → “Array” | `output-array`, `output-oneline` | “Pretty Print JSON” must be `false` when this is `output-oneline`. |
| `compression-format` | Compression Format | ✔ | `none` | `none`, `gzip`, `bzip2`, `xz-lzma2`, `snappy`, `snappy framed`, `zstd` | Case-insensitive canonical values; only `gzip` supports the `compression-level` property. |
| `compression-level` | Compression Level | ✔ (when `compression-format = gzip`) | `1` | Integers `0`-`9` | Defaults to NiFi’s small-buffer gzip writer; ignored for other formats. |

The writer also inherits all schema access descriptors; the same canonical value rules apply (`schema-access-strategy = inherit-record-schema`, etc.).

### Canonical Value Mapping Recap

* “Use 'Schema Name' Property” → `schema-name`
* “Infer from Result” → `infer`
* “Do Not Write Schema” → `no-schema`
* “Set 'schema.name' Attribute” → `schema-name`
* “Set 'avro.schema' Attribute” → `full-schema-attribute`
* “Schema Reference Writer” → `schema-reference-writer`

When a property’s canonical key contains spaces (e.g., `Schema Write Strategy`, `Schema Cache`, `Pretty Print JSON`), NiFi expects that exact string in the JSON payload. The manifest helper must therefore map hyphenated or snake_case keys to those canonical names before issuing REST calls.

> **Required vs. default values:** NiFi’s descriptors often mark properties as `required(true)` *and* supply a `defaultValue`. This means the component ships with a safe baseline (e.g., `ZendeskRecordSink.CACHE_SIZE` defaults to `"1000"`) but will still refuse to enable if the field is cleared. The controller-service report mirrors this reality: a property can appear in `requiredProperties` even though a default is present.

---

## Controller Service Update Contract (REST)

1. **Disable before mutate.** NiFi throws `400 Bad Request` if we attempt to modify properties while the service is `ENABLING` or `ENABLED`. We must:
   1. `PUT /controller-services/{id}` with `{state: "DISABLED"}` using the latest `revision` block.
   2. Poll `GET /controller-services/{id}` until `component.state == "DISABLED"`.
2. **Write canonical properties.** Send only canonical keys/values (see tables above). If we previously wrote display-name keys, send an empty string for those keys to clear them (`"Schema Access Strategy": ""`).
3. **Re-enable and poll.** After updating, call `PUT … {state: "ENABLED"}` and wait until `component.state == "ENABLED"`.
4. **Time-outs:** NiFi can legitimately spend several seconds in ENABLING while validating, so allow ≥30 seconds before aborting.

The updated helper in `automation/src/nifi_automation/controller_registry.py` now:

* Fetches descriptors and uses `_canonicalize_properties` to translate manifest keys/values.
* Clears stale display-name keys when necessary.
* Forces services to disable before applying mutations, then polls for the expected state.

---

## Next Steps for Automation & Docs

1. **Manifest hygiene:** ensure every manifest entry uses canonical keys (e.g., `schema-access-strategy`, `schema-write-strategy` with the canonical values above). The existing manifest is now updated accordingly.
2. **Flow specs:** `automation/flows/simple.yaml` references `json-reader` and `json-writer`. With the canonical manifest and controller-service contract in place, the integration tests should pass once the remaining transition bug (service stuck ENABLING) is resolved.
3. **Doc linkage:** Surface this document in `automation/README.md` so future contributors know where to find the canonical property list.
4. **Test enhancement:** add an assertion in the integration suite that dumps controller-service states when validation fails so we capture these errors immediately.

Once the controller services enable cleanly with the canonical payloads, rerun:

```bash
RUN_NIFI_INTEGRATION=1 .venv/bin/python -m pytest
```

to verify both `trivial` and `simple` flows deploy successfully.


Need final doc large but manageable. We'll edit doc to include tables - but we already started doc with sections. Need to add tables for writer etc. Also mention code changes we plan (manifest canonicalization). Provide to-do steps? maybe update final section "Next Steps / TODO" with automation tasks etc.

We should revise doc to include tables for writer. Let's update doc using apply_patch to append sections. Need to add more detail after we left placeholder for writer. Currently doc ended at canonical mapping example? there is more? Need to continue, include writer section, dependencies, state mgmt, recommended tooling etc. At end, maybe include to-do check list: update manifest file (done), extend canonicalization (done). Should mention actual modifications in code (function `_canonicalize_properties`). Provide guidelines; mention restful disable requirement referencing `controller_registry.py`.

Let's append content.

We'll use apply_patch to insert new sections after "### Canonical Value Mapping Example" and before next sections maybe, as doc currently stops there? doc continues with ---? yes but restful not added. Need to edit to add sections: "## Canonical Property Reference – JsonRecordSetWriter", "## Controller Service Update Contract", "## Data We Still Need" or "## Next Steps for Automation" etc. Provide bullet list tasks done/remaining.

Let's patch doc accordingly.
