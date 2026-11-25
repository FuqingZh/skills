# Workspace Ownership And Execution Scope

Use when establishing execution authority, bounding workspace discovery,
transferring ownership, or verifying runtime release.

## Implementation Task Intake

Follow the user's authorized scope of implementation or delivery. Requests to
analyze, review, or discuss do not by themselves authorize implementation.
When asked to produce a plan or document, deliver the requested artifact
without treating that request as authorization to execute its proposed changes.
Resolve discoverable facts from repository and environment evidence rather
than asking the user to supply them.

Keep discovery and mutations within the assigned repository or task workspace.
Before recursive searches or broad discovery on a remote mount, network
filesystem, large shared filesystem, or parent aggregation root, narrow the root
and apply a traversal-aware bound such as relevant subdirectories or maximum
depth. Bound file types, file size, result count, and concurrency where supported;
prefer indexes and targeted lookups. If a safe boundary cannot be established,
stop the broad search and report the narrower check needed.

Preserve existing ownership: do not write in another owner's active branch or
sibling worktree, and do not repeat rejected filesystem escalation. Do not
claim background work or cleanup is complete before verifying that spawned
child processes have exited. Keep partial cleanup observable and retryable, and
preserve dirty worktrees.
