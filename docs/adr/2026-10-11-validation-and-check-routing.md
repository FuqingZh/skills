# Proportional validation and PDM check routing

Date: 2026-10-11
Status: Accepted

## Context

`pyproject.toml` defines discrete Python, Markdown, link, shell, skill, and
pytest checks composed into `pdm run check`, locked by `pdm.lock`. Earlier
guidance required running the entire code gate for every edit regardless of
affected surface, and an assessment considered adding Nx for affected-target
selection and caching (see commit `2a552d4` for the prior full records).

## Decision

- Select local validation proportionally to the affected behavior and contracts;
  run the full `pdm run check` gate when runtime behavior, skills, routing,
  installer contracts, or repository policy require it.
- Classify documentation changes by behavioral impact rather than file
  extension (skill/prompt/routing edits are behavior changes, not prose-only).
- Keep PDM tasks as the single local and CI validation entrypoint; do not adopt
  Nx or a custom path-based check skipper.

## Rejected Alternatives

- **Unconditional full gate for all edits**: Caused documentation-only edits to
  run unrelated runtime suites mechanically (superseded on 2026-08-07).
- **Nx affected selection and caching**: Required adding a Node toolchain and
  hand-maintaining dependency edges (`pdm.lock`, deleted link targets, skill
  metadata, and runtime isolation checks cannot be inferred safely from
  directory layout alone) with no measured CI timing bottleneck.

## Consequences

- Local checks stay fast and aligned with CI without introducing a second
  toolchain.
- Contributors must choose checks from the affected contract and disclose any
  unverified obligation.

## Reopen When

- Repeated CI timing measurements show substantial avoidable execution time, or
  the repository splits into independently maintained packages needing a shared
  dependency graph.
