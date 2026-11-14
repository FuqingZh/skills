# Debugging Discipline

Use for bugs, runtime failures, failing tests, unclear behavior, and root-cause
analysis.

- Establish the original failing surface before editing. Reproduce it when
  reasonably available; otherwise inspect concrete logs, requests, artifacts,
  or runtime state and name the evidence gap. An existing failure record can
  supply this evidence without manufacturing a fresh failing test.
- Distinguish symptoms, hypotheses, and causes supported by evidence. When
  environment drift is plausible, inspect the actual versions, configuration,
  and runtime state implicated by the failure.
- Keep conclusions within the environment actually observed. Absence or a
  mismatch inside a sandbox or worker does not establish the state of an
  external host or service. Verify the relevant state from an authoritative
  context before changing persistent configuration. When that context is
  unavailable, report the boundary and the exact check still needed.
- Fix the supported cause with the smallest effective change. Do not hide the
  failure through broader exception handling or silent fallback.
- Rerun the original failing check or an equivalent that would detect the
  original symptom under the same triggering conditions. Exercising the same
  path or obtaining exit status zero is insufficient by itself.
- When claiming a fix or a verified runtime outcome, apply
  [verification discipline](verification.md) for completion evidence and reporting.
