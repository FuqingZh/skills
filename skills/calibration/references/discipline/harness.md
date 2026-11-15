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

When Ruff is appropriate for the repository, follow its existing rule selection.
If no repository-local selection exists, start with `E`, `F`, `I`, `UP`, `B`,
`SIM`, and `RUF`. Additional rule families, `ALL`, and preview rules are
repository-specific choices, not defaults.

### Diagnostic suppression baseline

Classify a diagnostic by the owner of the invalid or incomplete contract, not
only by the source line where a checker reports it. A warning at a first-party
call site may still originate from incomplete external typing, generated code,
vendored code, or a demonstrated checker limitation.

For first-party code and interfaces, repair the contract or implementation. Do
not use an ignore comment, warning annotation, lint disable, type escape, or
weaker checker configuration merely to make the required check pass.

Contain an external, generated, vendored, or checker gap at its narrowest
repository-owned boundary. Prefer, as the language and repository allow, a
typed adapter, stub, wrapper, declaration, or targeted configuration exclusion
that makes the assumed contract explicit and testable. Do not edit an external
or generated source merely to satisfy a local checker.

Use a source-level suppression only when no such boundary can express a
demonstrably valid contract. Name the exact diagnostic and retain reviewable
evidence for the exception. Do not hide a first-party failure on the same line.
Do not broaden suppressions to hide first-party failures. Keep accepted
exceptions mechanically discoverable, reject unused exceptions when the
checker supports it, and prevent unexplained growth through the
repository-owned validation path.

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

Follow the user's authorized scope of implementation or delivery. Requests to
analyze, review, or discuss do not by themselves authorize implementation.
When asked to produce a plan or document, deliver the requested artifact
without treating that request as authorization to execute its proposed changes.
Resolve discoverable facts from repository and environment evidence rather
than asking the user to supply them.

At intake, discover the repository's accepted delivery path. Ordinary local
engineering does not require an issue tracker or an orchestrator session.

Keep discovery and mutations within the assigned repository or task workspace.
Before searching a remote mount, network filesystem, large shared filesystem,
or parent aggregation root, narrow the root and apply a traversal-aware bound
such as relevant subdirectories or maximum depth. Bound file types, file size,
result count, and concurrency where supported; prefer indexes and targeted
lookups. If a safe boundary cannot be established, stop the broad search and
report the narrower check needed.

Preserve existing ownership: do not write in another owner's branch or sibling
worktree or repeat rejected filesystem escalation. Transfer only after verified
write-authority revocation and runtime release. A terminated session is not proof
that its children exited; require an empty OS-owned containment boundary before
claiming full runtime release.
Keep partial cleanup observable and retryable, and preserve dirty worktrees.

## Repository Delivery Feedback Loop

Delegation retains responsibility for the outcome. Use existing task and platform
state to track the goal, acceptance criteria, owner, pending work, and next
observation. Choose available tools for waiting and notification.

Before ending foreground tracking, verify that a durable continuation mechanism
has accepted responsibility for observing the work, resuming its owner, and
notifying a reachable recipient. Saved task state or PR submission alone does
not establish that handoff. Otherwise continue bounded observation and authorized
follow-up, or report the exact blocker while keeping pending work explicit.

For pull-request delivery, use repository-owned checks and platform review on
the current commit. Classify failures before changing the harness: fix product
defects when existing checks correctly detect them; add capability only for an
observed execution or feedback gap. Tool access does not grant write or scope
authority or replace the current owner. Follow
[verification](verification.md) for acceptance evidence and external readback;
report unavailable external access and the action needed to restore it.

Handle same-scope mechanical review feedback within the current authorized
pull request contract through the existing bounded owner loop. If review on
the exact current head exceeds that contract or the configured review-convergence
budget is exhausted, pause remote review and preserve branch, head, worktree,
owner, and feedback state. Reassess the next action within existing authority;
escalate contract expansion when additional authorization is required.
Choose work boundaries from actual dependencies and independent acceptance
criteria, rather than treating budget exhaustion as a reason to split a PR.
Transport, polling, or idempotent-operation retry exhaustion retains its
preserve-and-report path. Do not impose universal LOC, file-count, or
review-round thresholds.

Keep the repository as the source of truth across execution environments.
Maintain shared setup logic in the repository when local, CI, and cloud runs
can use it. Keep server-only dependencies and data behind repository-owned
checks or CI runners; do not assume a hosted environment can reproduce them.

Add recurring monitoring only for demonstrated recurring work. Keep scheduling
in the platform control plane and use the continuation handoff above.

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
