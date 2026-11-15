# Repository Delivery Feedback

Use when coordinating delegated work, handling pull-request feedback, or
establishing durable continuation across local, CI, and cloud environments.

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
