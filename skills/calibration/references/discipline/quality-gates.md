# Quality Gates

Use when selecting repository checker rules or deciding whether to introduce,
retain, or remove a diagnostic suppression or exclusion.

## Ruff Defaults

When Ruff is appropriate for the repository, follow its existing rule selection.
If no repository-local selection exists, start with `E`, `F`, `I`, `UP`, `B`,
`SIM`, and `RUF`. Additional rule families, `ALL`, and preview rules are
repository-specific choices, not defaults.

## Diagnostic suppression baseline

Classify a diagnostic by the owner of the invalid or incomplete contract, not
only by the source line where a checker reports it. A warning at a first-party
call site may still originate from incomplete external typing, generated code,
vendored code, or a demonstrated checker limitation.

For first-party code and interfaces, repair the contract or implementation. Do
not use an ignore comment, warning annotation, lint disable, type escape, or
weaker checker configuration merely to make the required check pass.

Contain an external, generated, vendored, or checker gap at its narrowest
repository-owned boundary. Prefer, as the language and repository allow, a
typed adapter, stub, wrapper, declaration, or targeted configuration exclusion
that makes the assumed contract explicit and testable. Do not edit an external
or generated source merely to satisfy a local checker.

Use a source-level suppression only when no such boundary can express a
demonstrably valid contract. Name the exact diagnostic and retain reviewable
evidence for the exception. Do not hide a first-party failure on the same line.
Do not broaden suppressions to hide first-party failures. Keep accepted
exceptions mechanically discoverable, reject unused exceptions when the
checker supports it, and prevent unexplained growth through the
repository-owned validation path.
