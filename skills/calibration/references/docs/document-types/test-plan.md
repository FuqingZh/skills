# Test Plan

Document validation strategies or acceptance contracts that need reuse across
changes, releases, or environments. Give contributors enough information to
run the checks and judge whether the acceptance criteria are met.

- Follow the repository's testing-documentation location. If none is defined,
  use `docs/contributing/`.
- Use configured test and verification entrypoints. Link executable tests and
  CI definitions, keeping implementation details with their owning code.
- State scope, risks, affected contracts, and relevant test levels.
- Identify fixtures, data boundaries, environment assumptions, and required
  setup.
- Give commands or CI checks, expected evidence, and failure interpretation.
- Define acceptance criteria and any required manual artifact or runtime
  inspection.
- Record compatibility, cleanup, and rollback implications when applicable.
