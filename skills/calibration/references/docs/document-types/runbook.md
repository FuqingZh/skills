# Runbook

Document controlled operational procedures, especially for production-adjacent
or high-risk work. Enable authorized operators to verify results and respond
to checkpoint or recovery failures.

Use the [AWS runbook guidance](https://docs.aws.amazon.com/wellarchitected/2023-10-03/framework/ops_ready_to_support_use_runbooks.html)
as a method reference. Repository-local commands, permissions, and rollback
rules remain authoritative.

- Follow the repository's runbook location. If none is defined, use
  `docs/runbooks/`.
- State purpose, scope, owner, prerequisites, access requirements, and
  conditions for use.
- Give ordered steps with checkpoints and expected observations.
- Define verification, recovery, rollback, escalation, and stop conditions.
- Identify version, environment, and dependency assumptions that affect safety.
- Keep secrets, private host state, and unreconstructable raw evidence out of
  the public document.
