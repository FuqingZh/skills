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
