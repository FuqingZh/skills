# Implementation Plan

Turn a settled requirement or accepted direction into executable work with
clear dependencies and acceptance criteria.

- Follow the repository's planning location. If none is defined, use
  `docs/design/`.
- Persist or commit the plan only when explicitly requested or required by
  repository workflow.
- Ground the plan in the requirement or design, repository instructions,
  current implementation, and affected contracts.
- State goals, non-goals, assumptions, affected components, and their
  responsibilities. Preserve established boundaries unless the settled design
  explicitly changes them.
- Organize work into slices with clear outcomes, dependencies, relevant
  interfaces and invariants, acceptance checks, and evidence locations.
  Keep cross-slice paths, names, types, schemas, and compatibility assumptions
  consistent.
- Resolve material product, architecture, interface, and compatibility choices
  before starting implementation that depends on them. For testable technical
  assumptions, define bounded investigations with questions, expected evidence,
  decision criteria, and conditions for starting dependent work.
- For correctness-critical or design-determining behavior, specify
  representative inputs or states and observable acceptance results. Reuse
  existing checks where suitable, and validate assumptions before dependent work.
- Include risks, compatibility concerns, rollback or cleanup needs, and final
  verification. Describe review splits when needed for delivery.
- Make ready slices executable without requiring the implementer to infer
  requirements or reconstruct design intent. Keep unresolved details explicit
  instead of inventing them to make the plan appear complete.
