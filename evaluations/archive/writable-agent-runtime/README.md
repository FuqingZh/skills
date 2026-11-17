# Retired writable-agent evaluation runtime

The Codex writable-agent executor and progressive-validation batch controller
are retired from the supported tool set. Their sandbox, broker, permission-profile,
process-cleanup, and scheduling tests are no longer active repository checks.
The skills, installer, and current validation tools do not depend on this runtime.

## Preserved source

[manifest.json](manifest.json) records 20 byte-for-byte snapshots from commit
`8f14136352780fc5e2471bf05ec322d4953fa0e9`: two runtime scripts, 15 test modules,
and three test-support modules. Each original repository path maps to the same
path under this directory with a `.txt` suffix. The snapshots are historical
text, not executable tools or importable test modules. The old entrypoints have
been removed without compatibility wrappers.

To investigate historical behavior, inspect that source commit and its recorded
runtime prerequisites. Restoring an execution environment or running a model
experiment requires a separately scoped task; these snapshots do not establish
current Codex or sandbox compatibility.

## Evidence retained in place

- [AI-native implementation](../../ai-native-implementation/README.md): cases,
  fixtures, scorers, and recorded W06/W07 observations.
- [Progressive validation selection](../../progressive-validation-selection/README.md):
  frozen protocols, inputs, corrected results, and failure history.

Original experiment records, hashes, provenance, and private evidence locations
remain unchanged. Active checks in
[test_historical_evaluation_evidence.py](../../../tests/test_historical_evaluation_evidence.py)
verify the source snapshots, frozen fixture manifest, case inventory, and W07
result hashes and calculations without importing or executing the retired tools.
The independent third-party provenance and license checks remain active.

The repository retains its existing quality gate and 100% line-coverage
requirement for maintained Python tools. No diagnostic exclusion or coverage
threshold reduction is part of this retirement. Other evaluation tools are
outside this change.
