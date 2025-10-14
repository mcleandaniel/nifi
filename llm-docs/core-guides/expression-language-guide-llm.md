# NiFi Expression Language Guide — LLM Notes

*Source*: `nifi-docs/src/main/asciidoc/expression-language-guide.adoc` (reviewed 2025-10-13)

## Purpose
- Teaches how to reference FlowFile attributes, system properties, and environment variables inside NiFi component properties.
- Documents syntax, evaluation order, editor features, and every built-in function grouped by category.

## Core Concepts
- **Expression Form**: `${subject:func(args):func2(...)};` start delimiter `${`, end `}`; functions chained left→right.
- **Subjects**: Usually FlowFile attributes; escape special characters or leading digits with quotes (`${"my attr"}`).
- **Hierarchy**: Lookup order is FlowFile attribute → JVM system property → OS environment variable; missing keys yield `null`.
- **Embedded Expressions**: Nest `${}` inside arguments for comparisons or computed arguments.
- **Subjectless Functions**: Call directly (`${hostname()}`) when no subject is required; result becomes subject for subsequent functions.
- **Escaping Literals**: Use `literal()` or double dollar signs (`$$`) when property supports EL but you need raw text (e.g., `literal("Hello ${User}")`).
- **Expression Language Editor**: Modal helper in UI showing attribute values, autocomplete, function reference, preview.
- **Framework System Properties**: The EL exposes NiFi-defined system keys such as `nifi.framework.version` for embedding runtime metadata.
- **Data Types**: Strings are default; numeric functions expect parseable values; type coercion helpers convert as needed.

## Function Categories & Highlights
- **Boolean Logic**: `isNull`, `notNull`, `isEmpty`, `equals`, `equalsIgnoreCase`, `matches`, `ifElse`, `and`, `or`, `not`.
- **String Manipulation**: `toUpper`, `toLower`, `trim`, `substring`, `substringBefore`, `substringAfter`, `replace`, `replaceAll`, `append`, `prepend`.
- **Search & Pattern**: `contains`, `find`, `findRegex`, `indexOf`, `lastIndexOf`, `startsWith`, `endsWith`.
- **Encoding/Decoding**: `base64Encode`, `base64Decode`, `urlEncode`, `urlDecode`, `escapeXml`, `unescapeJson`, `hash` (selectable algorithms).
- **Mathematical & Numeric**: `toNumber`, `plus`, `minus`, `mod`, `multiply`, `divide`, `ceil`, `floor`, `round`, `min`, `max`, `abs`, `format`, `math`.
- **Date & Time**: `toDate`, `format`, `formatInstant`, `formatDate`, `plusHours`, `minusDays`, `toNumber` (epoch conversions).
- **Type Coercion**: `toNumber`, `toDecimal`, `toString`, `toRadix` convert between numeric/text forms.
- **Subjectless Context**: `hostname()`, `ip()`, `UUID()`, `now()`, `literal()`.
- **JSON Helpers**: `isJson`, `jsonPath`, `jsonPathAdd`, `jsonPathSet`, `jsonPathPut`, `jsonPathDelete`; supports modifying and extracting scalar/array values.
- **Delimited Utilities**: `getDelimitedField` extracts tokens by index/delimiter; combine with string functions for CSV-style parsing.
- **Attribute Collection Helpers**: `anyAttribute`, `allAttributes`, `anyMatchingAttribute`, `allMatchingAttributes`, `anyDelineatedValue`, `allDelineatedValues`, plus aggregators like `join` and `count`.

> TIP: Most functions document subject type, return type, and error behavior; if arguments are missing or incompatible, NiFi routes to failure at validation time.

## Safe Usage Patterns
- Validate null-handling using `default` or `ifElse` to avoid `null` outputs when attributes missing.
- Combine boolean functions with `and`/`or` chains rather than complex nested `ifElse` when readability matters.
- For numeric math, convert strings with `toNumber` first; handle locale formatting via `format`/`toNumber` pattern arguments.
- When reading JSON attributes, use `jsonPath` before conversion; `parseJson` returns object enabling dot notation or functions like `get`. Ensure attribute value is valid JSON.
- Use `escapeJson`, `escapeXml` before embedding dynamic values into other languages to avoid injection.

## Editor & Debugging Notes
- Expression Language editor lists available attributes for selected component context (incoming FlowFile vs variable registry).
- Preview panel resolves expressions using a sample FlowFile; missing attributes appear with warning icon.
- Controller Service properties may be EL-enabled or disabled per descriptor; the doc clarifies that support is per-property.

## LLM Answering Tips
- When asked “can I do X in EL?” identify function category above and cite canonical function names; mention chaining if multiple steps needed.
- For timezone-sensitive operations, reference date functions and note that NiFi stores epochs in milliseconds.
- If user needs conditional routing, suggest boolean functions combined with `ifElse`, `matches`, or `equals` and mention null-safety.
- For performance questions (e.g., repeated regex), advise caching results with `cache` functions when available or moving to scripted processors.
- Warn that subjectless functions cannot follow another function without chaining (e.g., `${hostname()}` not `${attr:hostname()}`).

## Cross-Doc Pointers
- **Developer Guide** FlowFile section elaborates on core attributes referenced throughout this guide.
- **User Guide** demonstrates Expression Language usage in property editors and advanced UI search.
- **Administration Guide** references Expression Language within proxy routing (`nifi.remote.route.*`) and property files; same functions apply outside UI.

## Anticipated FAQs
1. *How do I safely handle missing attributes?* → Combine `notNull`, `default`, or `ifElse` to provide fallback values before using the attribute.
2. *How do I extract JSON fields inside EL?* → Use `${attribute:jsonPath('$.field')}` or `${attribute:parseJson():get('field')}` depending on desired type.
3. *Can I perform math with FlowFile sizes?* → Convert to number (`${fileSize:toNumber():div(1024)}`) then apply math functions (`plus`, `minus`, `format`).
4. *How do I compare timestamps?* → Convert to epoch with `toDate('format'):toNumber()` or use `format` to produce comparable strings.
5. *How do I build dynamic filenames?* → Chain string functions: `${path:substringAfterLast('/')}-${now():format('yyyyMMddHHmmss')}.${filename:substringAfterLast('.')}`.
