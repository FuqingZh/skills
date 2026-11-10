# Evaluation tooling: Promptfoo replay probe

Decision for this iteration: use **Promptfoo 0.125.1 as a local replay and
comparison layer**. Keep the frozen Pi transport for v4. Inspect AI remains a
credible alternative for a future Python-native evaluation pipeline; it was
researched, not installed or exercised.

## Fit for this study

| Need | Promptfoo | Inspect AI |
| --- | --- | --- |
| Custom Python integration | Python providers and assertions | Custom model providers and scorers |
| Batch organization and inspection | Configured cases, provider columns, local history, JSON/HTML export and viewer | Tasks/datasets, evaluation logs and log viewer |
| Re-evaluate saved outputs | Our read-only provider replays source records; Python assertions run without model calls | Documented `inspect score` can score saved logs without rerunning solvers; scorer may still call a model |
| Original failure history | Keep immutable source JSON; avoid in-place retry commands | Keep original log and use a new scored log; avoid overwrite options |
| Evidence here | One 48-cell offline replay, 48 exclusive receipts, JSON/HTML exports | Documentation review only |

The immediate benefit is a standard comparison table and failure display without
writing a custom viewer. No developer-time benchmark was conducted, and no
end-to-end speedup or semantic scoring improvement is claimed. The local adapter
is limited to loading saved artifacts, keeping error status and generating config.
Admission, human-label provenance and pair-level denominators remain study-owned.

## Probe and retained failure

- Registry version: Promptfoo `0.125.1`; required Node `>=22.22.0`; tested with
  Node `26.13.0`.
- First installation used a dedicated `/tmp/skills-promptfoo-probe.RQfhU4/`
  directory. It failed with `TAR_ENTRY_ERROR ENOSPC: no space left on device`.
  In this process environment `/tmp` is a 2 GiB tmpfs; the attempt used about
  1.1 GiB. Only this attempt's `_npx` and `_cacache` directories were removed;
  `install.log` and npm's `_logs/` were retained.
- Second installation used the repository-local, ignored
  `.venv/promptfoo-probe.GhvasL/` directory on the larger workspace filesystem.
  It succeeded. No global install, project dependency edit, runtime prompt change
  or live instruction update occurred. This temporary tool installation is
  separate from the locked PDM validation dependencies.
- `promptfoo_replay.py` prepared the same 24 jobs for each of two saved versions.
  The CLI completed in a reported 10 seconds at concurrency three: **29 valid
  artifacts, 19 retained errors**, with **48 exclusive provider receipts**.
- Exit code `100` reflects the expected error cells. It is not an installation or
  transport failure. There were no model calls. The 24 v3 artifacts and five v4
  artifacts pass the replay assertion; all 19 v4 errors remain errors.
- JSON export retains `response.output` alongside `response.error` for failed
  records. JSON and HTML were generated. Browser rendering and live transport
  timeout/crash behavior were not tested.

The UI's **60.42% pass rate is artifact validity across two historical batches**.
It is not preference agreement and must not replace either version's summary.
Replay is explicitly labeled as replay. Framework cache was disabled; that does
not turn saved answers into fresh model samples.

Probe files are under `.venv/promptfoo-probe.GhvasL/`: `install.log`, `replay.log`,
`replay/results.json`, `replay/results.html`, `replay/source-summaries.json` and
`replay/receipts/`. These are disposable local views; the committed source records,
adapter and summaries are the durable evidence. The optional temporary package
is pinned at its top-level version; it is not a new repository dependency lock.

## Reproduce the local view

Use a sufficiently large local directory rather than a small tmpfs. The following
installs an optional, pinned tool into an isolated npm cache, prepares a new replay
folder and writes only local results. Every new replay needs a new destination;
receipts intentionally reject repeated jobs within one destination.

```bash
TOOL_ROOT="$(mktemp -d "$PWD/.venv/promptfoo-replay.XXXXXX")"
export PROMPTFOO_DISABLE_TELEMETRY=1
export PROMPTFOO_DISABLE_UPDATE=1
export PROMPTFOO_CONFIG_DIR="$TOOL_ROOT/state"
export PROMPTFOO_LOG_DIR="$TOOL_ROOT/logs"
export PROMPTFOO_PYTHON="$(pdm info --python)"

pdm run python evaluations/communication-style/preference-calibration/promptfoo_replay.py "$TOOL_ROOT/replay"
npm exec --prefix "$TOOL_ROOT" --cache "$TOOL_ROOT/npm-cache" --yes --package=promptfoo@0.125.1 -- \
  promptfoo eval -c "$TOOL_ROOT/replay/promptfooconfig.json" \
  --no-cache --no-share --max-concurrency 3 \
  -o "$TOOL_ROOT/replay/results.json" "$TOOL_ROOT/replay/results.html"
```

Expect exit `100` while these retained invalid records are included. Do not use
`promptfoo retry` or `--retry-errors`: the documented retry path updates evaluation
history in place after successful retries. Do not enable sharing or cloud sync.
Open the exported HTML locally; full original context remains in the referenced
source JSON. A model-based replacement assertion would create new paid judgment
calls and requires its own frozen protocol.

## Boundaries before any live migration

The probe demonstrates saved-output display and error preservation for these
records. It does not validate one-attempt behavior for live provider crashes,
timeouts, SDK retries or worker restarts. A live custom provider would need to
retain the existing Pi isolation and process cleanup contract, place the outer
worker timeout beyond the inner timeout, and preserve attempt records before
returning to the framework. Such migration is deferred.

Built-in rubric or winner-selection assertions do not automatically implement
our ties, unknown labels, mixed-case admission or pair-level swap rules. The v4
failure also shows why output-contract conformance needs a small independent
preflight before another large batch. Tool adoption cannot establish that a judge
understands this user's preferences.

## Official sources reviewed

- [Promptfoo Python providers](https://www.promptfoo.dev/docs/providers/python/):
  `call_api`, result/error shape, worker concurrency, timeout and restart behavior.
- [Python assertions](https://www.promptfoo.dev/docs/configuration/expected-outputs/python/):
  deterministic `get_assert` and grading-result shape.
- [CLI reference](https://www.promptfoo.dev/docs/usage/command-line/): local data
  directories, exports, cache/sharing controls and in-place retry semantics.
- [Telemetry](https://www.promptfoo.dev/docs/configuration/telemetry/): telemetry
  is on by default; explicit telemetry and update-check opt-outs used above.
- [Inspect scoring workflow](https://inspect.aisi.org.uk/scoring-workflow.html):
  separate scoring, new scored logs, append/overwrite and model-call boundaries.
- [Inspect model providers](https://inspect.aisi.org.uk/providers.html): custom
  provider integration. No Inspect runtime compatibility claim is made here.

The initially requested Promptfoo `/docs/configuration/retries/` URL returned
HTTP 404. Retry behavior above is sourced from the current CLI reference instead.
