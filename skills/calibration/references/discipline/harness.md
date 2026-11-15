# Repository Agent Harness

Use this reference when an agent repeatedly stalls, rediscovers the same
operation, lacks feedback, or cannot reliably navigate and complete work in a
repository.

The goal is to identify the missing repository capability and place it at the
lowest durable layer that can provide it. Do not default to adding prompt text.

## Missing Capability Diagnosis

| Observed gap | Prefer |
| --- | --- |
| Facts or authority are hard to find | repository map, current docs, or generated reference |
| A repeated operation is hard to execute | repository script, tool, or stable command |
| Correctness cannot be decided | test, grader, acceptance fixture, or explicit contract |
| Runtime state cannot be observed | logs, metrics, traces, screenshots, or inspectable artifacts |
| A boundary is repeatedly violated | lint, structural test, schema, or typed interface |
| A task cannot survive interruption or handoff | durable task state, isolated workspace, or orchestration |

Confirm the gap from actual failures, review feedback, or repeated task
evidence.

When a session repeatedly searches for the same fact, identify the entrypoint
the agent actually read and the authoritative source it needed. Prefer a
navigation pointer between them. If the source was already reachable, check
for misleading names, stale content, or conflicting authority before adding
another link or document.

Inspect existing checks and CI wiring before proposing a coding rule. Fix the
implementation when a check correctly catches a defect; repair the feedback
path when an existing check is unwired or broken. Add deterministic checks for
uncovered mechanical constraints. Keep context-dependent judgment guidance
with its existing owner and available where needed.

## Placement Ladder

Place each learned capability with the owner able to keep it current and, when
possible, enforce it:

| Knowledge or capability | Owner |
| --- | --- |
| Temporary observation | project task records |
| Stable project fact or boundary | project documentation |
| Repeated project operation | repository script or tool |
| Mechanically decidable invariant | test, lint, schema check, or CI |
| Cross-project engineering judgment | calibration |

For verifiable engineering facts, use current repository, environment, and
external-system evidence. Memory and conversation can provide leads; current
intent and authorization remain governed by applicable instructions.

## Repository Capability Adoption

When asked to assess or improve a repository for agent-led engineering, begin
with its delivery goal, local authority, current feedback loop, and a
representative task. Do not begin from a universal maturity model or a fixed
set of artifacts.

Treat named tools and artifacts as possible means unless the user or an
accepted contract requires that exact artifact. Assess the capability they
serve before creating them.

Leave adequate capabilities unchanged. Add the smallest durable increment
that addresses an observed gap, with its repository or external control-plane
owner. Verify its effect on the failure mode and stop when the loop is adequate.
Do not promote repository-local implementation details into calibration.

Add plans, specifications, or approval stages only when coordination, risk,
interruption, or repeated failure warrants them. A code change alone does not
require these stages or renewed approval for already-authorized work.

### Ruff Defaults

For Ruff rule selection, use [quality-gate defaults](quality-gates.md#ruff-defaults).

### Diagnostic suppression baseline

When deciding on a suppression or exclusion, use the
[quality-gate boundary rules](quality-gates.md#diagnostic-suppression-baseline).

## `AGENTS.md` Contract

Treat `AGENTS.md` as an operational map for an agent entering a repository or
subtree. Include only repository-specific information needed to find authority
and execute work, such as:

- a compact repository or subtree map;
- links to current architecture, testing, planning, and deployment authority;
- environment entrypoints and canonical verification commands;
- repository-specific review guidance when external agents cannot inherit a
  developer's global instructions;
- external resources, dangerous operations, and permission boundaries;
- repository-local exceptions to broader defaults.

Keep root and nested scopes explicit. Point to `docs/README.md` when the
repository has one. Do not copy architecture prose, test matrices, temporary
task state, generic engineering guidance, or source articles into
`AGENTS.md`. A repository with no useful local increment may omit it.

## Implementation Task Intake

For execution authority, workspace search boundaries, ownership transfer, or
runtime release, use [workspace ownership](workspace-ownership.md).

## Repository Delivery Feedback Loop

For delegated work, pull-request review, or durable continuation, use
[delivery feedback](delivery-feedback.md).

## Human Escalation

Resolve discoverable facts through safe evidence gathering. Escalate decisions
that exceed current authorization or still require a human choice about:

- product intent and priority;
- scope, interface, or compatibility tradeoffs;
- risk acceptance;
- irreversible or high-impact external operations;
- judgment that remains materially underdetermined after safe evidence
  gathering.

When escalation remains after safe evidence gathering, present the checked
evidence, the unresolved decision, and a recommendation.

## Completion

Complete a harness change only when the observed gap, selected owner, smallest
capability, and verification path are explicit. Evaluate representative
behavior separately when claiming the system became more effective.

## Further reading

- [DORA: Working in small batches](https://dora.dev/capabilities/working-in-small-batches/)
- [Google Engineering Practices: Small CLs](https://google.github.io/eng-practices/review/developer/small-cls.html)
