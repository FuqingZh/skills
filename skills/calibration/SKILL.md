---
name: calibration
description: Use for substantive cross-project engineering judgment, non-local architecture or refactoring, public or compatibility-sensitive contracts, unclear validation, or repository harnesses. Ordinary local implementation and repository prose with clear repository rules and executable feedback do not require this skill; cross-boundary contract documentation does.
---

# Calibration

Resolve material engineering decisions against the most specific applicable
source of truth. Correct false constraints, abstractions, or requirements when
they materially change the solution. Identify the decision, constraints, and
acceptance evidence. Within authorized, reversible local work, choose a
proportionate approach and revise it as feedback changes the evidence.

## Route

Load only the routers required by the decisions at hand:

- naming: `references/naming/README.md`
- engineering discipline and repository capabilities:
  `references/discipline/README.md`
- architecture, module boundaries, interfaces, and abstraction:
  `references/design/README.md`
- cross-boundary contract documentation or long-form engineering specifications:
  `references/docs_index.md`

## Completion

When the task requires implementation or delivery verification, or evidence
for public or cross-boundary contract claims, use
`references/discipline/verification.md` to select checks for the affected contract.
