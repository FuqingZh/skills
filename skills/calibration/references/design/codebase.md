# Codebase Design

Use this when deciding module boundaries, interface shape, abstraction depth,
adapters, shared helpers, wrapper layers, data flow, configuration, and where
logic belongs.

## Judgment Checks

- Give each boundary a clear caller and responsibility. Callers should not need
  to manage the internal complexity it owns.
- Treat the interface as everything a caller must know to use the module
  correctly: names, inputs, outputs, errors, side effects, configuration, call
  ordering, lifecycle, and any performance guarantees the caller relies on.
- Keep the main path understandable and easy to trace, reducing the need to
  chase scattered helpers. Justify necessary increases in complexity through
  concrete benefits.
- Add an abstraction when it reduces caller complexity, clarifies lifecycle or
  ownership, isolates policy, protects compatibility, or provides real reuse.
- Keep thin wrappers that provide a stable interface or a clear responsibility.
  Remove indirection that adds tracing cost without a responsibility or contract
  benefit.
- As an optional aid, imagine inlining an abstraction into its callers. Consider
  removing it if that reduces indirection without duplicating policy, exposing
  hidden complexity, or losing a contract.
- Keep domain behavior in the layer that owns the domain concept. Keep caller
  taste, product defaults, and presentation policy out of low-level kernels
  unless they are part of the explicit contract.
- Give temporary compatibility paths a retirement condition. For long-lived
  parallel interfaces, document their distinct contracts and reasons to coexist.
- Choose names and boundaries that express domain concepts and the caller's
  understanding of the task.

## Implementation Choices

- Prefer established domain parsers, writers, and bulk or vectorized APIs over
  reimplementing their operations.
- Keep related information together. Split, convert, or materialize data only
  at an algorithm or consumer boundary that requires it.
- For fast-moving libraries, verify the installed version and applicable API
  through source, documentation, or a small executable example.
- Keep technical defaults in explicit configuration structures and make their
  sources inspectable. Follow the project's configuration mechanism without
  scattering defaults through orchestration logic or requiring a separate file.
- Validate extensible configuration by the invariants a consumer requires.
  Preserve tolerated metadata and extension keys unless the owning contract
  requires a rewrite.
- Give non-obvious thresholds meaningful names and an applicability rationale.
  Expose an override only when callers or operations need to adjust the value.

When accepting an implemented design change, apply
[verification discipline](../discipline/verification.md) for compatibility,
tests, documentation impacts, and completion evidence.
