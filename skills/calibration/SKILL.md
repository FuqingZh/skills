---
name: calibration
description: Use for substantive cross-project engineering judgment, non-local architecture or refactoring, public or compatibility-sensitive contracts, unclear validation, repository harnesses, or agent or workflow evaluation. Ordinary local implementation and repository prose with clear repository rules and executable feedback do not require this skill; cross-boundary contract documentation does.
---

# Calibration

Resolve material engineering decisions against the most specific applicable
source of truth. Identify the decision, constraints, and acceptance evidence;
choose a proportionate approach and revise it as feedback changes the evidence.

## Baseline

Read `references/principles.md`.

## Route

Load only the routers required by the decisions at hand:

- naming: `references/naming/README.md`
- refactoring, debugging, environment diagnosis, verification, repository
  harnesses, and agent or workflow evaluation:
  `references/discipline/README.md`
- repository capability assessment, workspace boundaries and ownership,
  repeated delivery failures, missing CI or review capability, cross-contract
  review feedback, review-convergence exhaustion, and delivery topology:
  `references/discipline/harness.md`
- architecture, module boundaries, interfaces, and abstraction:
  `references/design/README.md`
- cross-boundary contract documentation or long-form engineering specifications:
  `references/docs_index.md`
- task-level retrospectives: suggest `$retrospect` when completed work reveals
  a failed assumption, consequential rework, validation surprise, repeated
  pattern, or delivery risk worth carrying forward.

If a routed reference is unavailable, continue from the baseline, name the
missing source, and do not invent its rules.

## Completion

Apply `references/discipline/verification.md` before claiming completion,
including public or cross-boundary contract claims. Select checks according to
the affected contract and the evidence needed to support the claim.
