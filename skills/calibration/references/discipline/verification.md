# Verification Discipline

Use when verifying implemented behavior, delivered outputs, external operations,
or public or cross-boundary contract claims. Discussion of a proposed approach
alone does not require delivery checks.

- Run the smallest relevant checks at a repository-owned validation entrypoint
  that can detect failures in the affected contract.
  Broaden only when repository-local policy explicitly requires it or evidence
  leaves an obligation uncovered. Prefer configured repository tools over a
  universal language checklist.
- Use current evidence for the final contract. Inspect generated outputs at
  their expected path and check relevant content; generator exit status alone
  does not establish the result.
- Read back external writes when practical. For deployments and services,
  verify the live endpoint, process, rollout, or service state the user relies on.
- For APIs, CLIs, and schemas, check the interface contracts, compatibility,
  and documentation consistency affected by the change, using the repository's
  validation mechanisms.
- For performance claims, use reproducible benchmarks with explicit inputs,
  environment, and scale; validate outputs as well as runtime. Make the random
  seed explicit when it materially affects reproducibility or public behavior,
  following the project's contract.
- Report what changed, what was verified, and the command, artifact, endpoint,
  or readback supporting the claim. Identify unverified items that materially
  affect the completion judgment, why they remain unverified, and the remaining
  risk. Give follow-up commands or evidence locations when needed.
- Match evidence to each material claim. Keep original evidence accessible
  through a reconstructable reference or an approved evidence location. When
  before evidence is unavailable, state the gap; do not invent a prior failure
  or imply an old version was executed. Domain-specific criteria live in
  [debugging](debugging.md), [refactoring](refactor.md), and
  [design](../design/codebase.md).
- Describe risk through the affected consumers or operations and any effects
  that would remain after reverting the code.
