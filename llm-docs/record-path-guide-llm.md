# NiFi RecordPath Guide — LLM Notes

*Source*: `nifi-docs/src/main/asciidoc/record-path-guide.adoc` (reviewed 2025-10-13)

## Purpose
- RecordPath is NiFi’s DSL for selecting, filtering, and transforming fields inside record-oriented data (JSON, Avro, CSV, etc.).
- Used by record-aware processors (e.g., `QueryRecord`, `UpdateRecord`, `ConvertRecord`) to address fields irrespective of serialization format.

## Core Syntax
- **Root & Child**: `/field/subField` walks explicit hierarchy from the root record.
- **Descendant**: `//zip` matches all descendants named `zip` regardless of depth; may return multiple matches.
- **Current & Parent**: `.` references current node; `..` moves up one level when used in filters/functions.
- **Wildcards**: `/*/name` selects a `name` child under any immediate parent.
- **Filters**: `[ ... ]` appended to a path restricts the selected records/array items using expressions (e.g., `/people[./age > 18]`).
- **Indexing**: Arrays use zero-based indices `addresses[0]`; slices `addresses[0..2]`; negative indices count from end `addresses[-1]`.
- **Map Access**: `attributes['filename']` or `attributes[/key()]` for dynamic lookups.

## Function Basics
- Functions can appear as standalone expressions or inside filters.
- Arguments may be literals (`'NY'`), numbers (`10`), relative paths (`./price`), or other functions.
- Nested function calls enable complex transforms, e.g., `toUpperCase(substringAfter(./email, '@'))`.

## Function Families (Highlights)
- **String & Text**: `substring`, `substringBefore/After`, `replace`, `replaceRegex`, `concat`, `trim`, `toUpperCase`, `toLowerCase`, `base64Encode/Decode`, `escapeJson`, `unescapeJson`.
- **Type Conversion**: `toDate`, `toString`, `toBytes`, `hash`, `uuid5`, ` anchored` (forces exact match semantics).
- **Aggregation & Creation**: `count`, `mapOf`, `recordOf`, `arrayOf`.
- **Formatting**: `format` (date/numeric formatting).
- **Padding**: `padLeft`, `padRight`.
- **Standalone Predicates**: `isEmpty`, `isBlank`, etc., usable in filters.
- **Filter Functions**: `contains`, `matchesRegex`, `startsWith`, `endsWith`, `not`, `isEmpty`, `isBlank`.

## Working with Collections
- **Arrays**: `[index]`, `[start..end]`, `[first()]`, `[last()]`, `[max_by(/price)]`, etc. Functions like `contains`, `isEmpty` help inside filters.
- **Maps**: Treat map entries as records with `key()` and `value()`; filter keys with `/attributes[ key() = 'filename' ]/value()`.
- **Choice Types**: Use filters to select the matching type (`/value[instanceOf('string')]`).

## Filters & Predicates
- Filters evaluate to Boolean; if `true`, the element is kept.
- Examples:
  - `/people[ ./state = 'CA' ]`
  - `/orders[ ./items[count() > 0] ]`
  - `/records[ matchesRegex( ./id, '^[A-Z]{3}\\d+$' ) ]`
- Combine predicates with functions or logical operators `and`, `or`, `not`.

## Practical Tips
- Prefer explicit child paths (`/a/b/c`) when performance matters; descendant search (`//c`) scans entire subtree.
- Combine RecordPath with Schema fields to avoid typos; mismatched field names resolve to `null`.
- Use `coalesce( ./preferred, ./fallback, 'unknown')` to provide fallbacks.
- When creating new structures, ensure result types align with downstream writer schemas (e.g., map vs record).
- RecordPath results feed into processor properties that expect single value, collection, or Boolean depending on context.

## LLM Answer Patterns
- When users ask “How do I select X?”, specify the exact path syntax and clarify array/map indexing.
- For transformations, mention chaining: `replace( toLowerCase(./name), ' ', '_' )`.
- Troubleshoot “path not found” by checking schema case-sensitivity and whether data is nested arrays vs objects.
- Suggest `isEmpty`/`isBlank` in filters for null-safe comparisons.
- Remind about choice/union types (need `instanceOf()` checks) when data has optional structure.

## Quick FAQs
1. **Filter objects by attribute value** → `/records[ ./status = 'ACTIVE' ]`.
2. **Pick first array element** → `/addresses[0]`; last element: `/addresses[-1]`.
3. **Get all map values where key starts with `http`** → `/headers[ startsWith( key(), 'http' ) ]/value()`.
4. **Build a record literal** → `recordOf('name', ./firstName, 'email', ./email)`.
5. **Hash a field** → `hash('./ssn', 'SHA-256')` or `hash(/person/ssn, 'SHA-256')`.
