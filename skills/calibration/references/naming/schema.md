# Schema And Header Contracts

Follow the [naming entrypoint's authority rules](README.md#authority) and the
target protocol and consumer schema, including native serialization mappings.
Consult only the source relevant to the current surface:

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
- Tabular exports: consult [Table Schema](https://datapackage.org/standard/table-schema/)
  for field names, human-readable titles, and column correspondence. Preserve
  source or consumer names.

These references do not require adopting new formats or frameworks.

For identifiers, establish the system's identity, uniqueness, stability, and
cross-system mapping requirements. Follow its database, protocol, or domain
standard; reversibility and encoding are choices of the owning contract.

Assess published field changes for compatibility. Preserve necessary mappings
at the owning serialization or integration boundary and use
[verification discipline](../discipline/verification.md) to verify consumer compatibility.
