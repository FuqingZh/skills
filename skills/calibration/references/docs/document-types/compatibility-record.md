# Compatibility Record

Document verified behavior, constraints, failure signatures, and adaptations
at an external or third-party boundary so others can reuse the findings
within their demonstrated scope.

- Follow the repository's compatibility-reference location. If none is defined,
  use `docs/reference/`.
- Identify the boundary, versions, environment, and applicable conditions.
  Distinguish the provider's stated contract from locally observed behavior.
- Separate observations, inferences, recommendations, and unresolved questions.
- Describe reproducible checks and link their evidence. Record failure
  signatures, affected callers or artifacts, and whether adaptations were tested.
- Limit conclusions to the scope supported by the evidence. Use repeated checks
  when needed to establish stability or characterize variable behavior.
- State limitations and conditions that require revalidation; identify an owner
  when follow-up work remains.
- Keep raw trial-and-error with the owning investigation's task records. When
  retaining exploration notes, follow the
  [working-material placement rules](../workflow/project_docs_architecture/20260805-v1.1-project-docs-architecture.md#working-material).
- Give readers enough information to reproduce the relevant observation,
  apply the adaptation within its validated scope, and recognize when the
  record no longer applies.

[Kubernetes version-skew policies](https://kubernetes.io/releases/version-skew-policy/)
and [MDN compatibility tables](https://developer.mozilla.org/en-US/docs/MDN/Writing_guidelines/Page_structures/Compatibility_tables)
are optional examples of presenting versions, scope, and supported combinations.
