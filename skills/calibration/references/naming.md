# Naming Sources

Use existing contracts and mature ecosystem guidance for naming decisions.
Consult only the section relevant to the current language, framework, or
interface.

## Authority

- Preserve published compatibility and names required by protocols, overrides,
  serialization, or framework integration. A style preference does not authorize
  renaming an existing interface.
- Follow repository conventions and the API being extended. For new surfaces
  without an established convention, use the relevant guidance below.
- Let configured formatters and linters check mechanical conventions. For linter
  selection or rule defaults, use [Ruff defaults](linters/ruff.md). Keep
  additional domain vocabulary or naming policy in the owning repository.

## Languages And Frameworks

- Python: [PEP 8 naming conventions](https://peps.python.org/pep-0008/#naming-conventions).
- Rust: [Rust API Guidelines: Naming](https://rust-lang.github.io/api-guidelines/naming.html).
- R projects adopting tidyverse conventions:
  [Tidyverse style guide](https://style.tidyverse.org/syntax.html#object-names).
  Follow existing base R or other ecosystem conventions where they apply.
- For other languages or framework-specific interfaces, consult their official
  guidance when needed. If no applicable source is available, follow the nearest
  existing repository convention.

## CLI Options

- For GNU-style interfaces, use the
  [GNU CLI conventions](https://www.gnu.org/prep/standards/html_node/Command_002dLine-Interfaces.html)
  and [long-option table](https://www.gnu.org/prep/standards/html_node/Option-Table.html)
  for argument syntax and standard option names.
- Consult [CLI Guidelines](https://clig.dev/) when the decision involves
  usability or interaction.
- For new long options without an established convention, default to
  lowercase kebab-case.

## Schemas, Headers, And Identifiers

Follow the target protocol and consumer schema, including native serialization
mappings:

- Protobuf: [AIP-140](https://google.aip.dev/140) for field names and
  [ProtoJSON](https://protobuf.dev/programming-guides/json/#field-names-as-json-keys)
  for JSON mappings.
- New JSON interfaces without an adopted naming style: use the
  [Google JSON property-name conventions](https://google.github.io/styleguide/jsoncguide.html#property-name-format)
  as the naming default.
- SQL: follow the database or ORM rules; the
  [SQL Style Guide](https://www.sqlstyle.guide/#naming-conventions) can inform
  descriptive names and word separation. The database governs identifier limits,
  quoting, and reserved words.
- Tabular exports: consult
  [Table Schema](https://datapackage.org/standard/table-schema/) for field
  names, human-readable titles, and column correspondence. Preserve source or
  consumer names.

These references do not require adopting new formats or frameworks. For
identifiers, establish identity, uniqueness, stability, and cross-system
mapping requirements under the owning protocol or database contract. Assess
published field changes for compatibility, preserve necessary mappings at the
owning serialization boundary, and use
[verification discipline](discipline/verification.md) to verify consumer
compatibility.

## Versions And Releases

Identify the versioned unit and the repository's declared versioning and release
policy rather than inferring compatibility from a version string or imposing
one scheme across ecosystems:

- [Semantic Versioning](https://semver.org/) for projects adopting SemVer.
- [PyPA versioning](https://packaging.python.org/en/latest/discussions/versioning/)
  for Python version syntax, scheme choices, and ecosystem behavior.
- [PyPA single-source guidance](https://packaging.python.org/en/latest/discussions/single-source-version/)
  for Python version-source integration; use native build and release tools for
  other ecosystems.

Keep repository-specific version sources, tag mappings, release automation, and
migration commitments in the owning repository. Version selection does not
authorize publication or prove deployment; follow
[verification discipline](discipline/verification.md) for release completion.
