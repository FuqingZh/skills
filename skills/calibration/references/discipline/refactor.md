# Refactor Discipline

Use this when changing structure while intending to preserve behavior: refactor,
migration, extraction, file split, wrapper removal, import cleanup, compatibility
cleanup, or staged convergence work.

## Judgment Checks

- Identify the public behavior and compatibility contracts to preserve. Changes
  to public APIs, CLIs, schemas, file layouts, and generated outputs must be
  intentional and documented separately from structural changes.
- Introduce a layer only for a concrete boundary, policy, lifecycle, reuse point,
  or readability benefit. Review main-path readability and justify any necessary
  increase in complexity.
- When practical, clean transition debt created or exposed by this move in the
  same batch: unnecessary broad imports, unused exports, duplicate helpers,
  obsolete compatibility aliases, suppression comments, temporary names, and
  dead routes. Keep the cleanup within the affected scope.
- Apply the [diagnostic suppression baseline](quality-gates.md#diagnostic-suppression-baseline)
  when deciding whether to introduce, retain, or remove a diagnostic suppression
  or exclusion.
- Check relevant old paths, names, call sites, docs, tests, fixtures, and generated
  references before claiming convergence. Update stale active references,
  distinguish intentional compatibility entrypoints, and preserve historical
  records and frozen evidence.
- Verify preserved behavior with checks that would detect regressions. Add tests
  where existing coverage is insufficient; verify intentional behavior and
  contract changes separately.

## Completion Criteria

A refactor is complete only when:

- old and new boundaries are not both active without a documented reason
- temporary compatibility code is either removed or tracked with an explicit
  retirement condition
- preserved behavior is supported by checks that would detect a regression

Apply [verification discipline](verification.md) for acceptance evidence,
compatibility review, and reporting.
