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

Load only the references required by the decisions at hand:

- naming: `references/naming/README.md`
- engineering discipline and repository capabilities:
  `references/discipline/README.md`
- architecture, module boundaries, interfaces, and abstraction:
  `references/design/codebase.md`
- document type and minimum content for cross-boundary contracts or long-form
  engineering specifications: `references/docs/document-types/README.md`
- project documentation layout, naming, navigation, and lifecycle, or placement
  of investigation working material:
  `references/docs/workflow/project_docs_architecture/20260805-v1.1-project-docs-architecture.md`

Follow repository-owned documentation and collaboration contracts; use shared
guidance to fill gaps in those contracts. Do not use the document-type route
for routine PR body generation unless the user asks how summaries relate to
durable project docs.

## Completion

When the task requires implementation or delivery verification, or evidence
for public or cross-boundary contract claims, use
`references/discipline/verification.md` to select checks for the affected contract.
