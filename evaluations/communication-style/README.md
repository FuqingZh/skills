# Communication style comparison

Status: development comparison complete; baseline retained. No candidate met the
style-improvement gate, so the planned holdout calls were not run. See the
[results](results.md), [selection](selection.json), and [audit](audit.md).

This study evaluates the opening communication paragraph only. The runtime
template, other global instructions, skills, installer, and installed homes are
unchanged.

## Question

Can a short instruction reduce self-defense, redundant explanation, invented
contrasts, forced colloquialisms, and decorative metaphors while preserving
clear, complete answers, including long explanations and requested comparisons?

External design sources and their limits are in the
[central source register](../../docs/sources.md). No upstream prompt or test
corpus is copied. The two candidate prompts were frozen before model generation.

## Materials and boundaries

- [Protocol](protocol.json): conditions, selection policy, and evidence limits.
- [Cases](cases.json): 12 independently written Chinese tasks, six per split;
  three long and three short in each split. Eight reconstruct generic learning
  scenarios; four are synthetic. They contain no private names, transcripts,
  paths, learning progress, credentials, or copied book passages.
- [Baseline](prompts/baseline.txt): exact opening paragraph at repository commit
  `fcac560789e1b39a519fad4d39ac98c0370caec0`.
- [Direct](prompts/direct.txt): concrete desired behavior with bounded exclusions.
- [Example](prompts/example.txt): identical direct prompt plus one contrast example.
- [Manifest](manifest.json): frozen source and runner SHA-256 values.
- [Judge](judge.txt): required-content checks and separately evidenced style issues.

The cases are reconstructions, not historical replay. Topic/source-dossier
families do not cross splits. Original conversation IDs are unavailable, so
separation of original sessions cannot be established. The prompt author has
seen the case specifications; holdout means held out from response-guided tuning,
not a secret third-party test set. Required content is reviewed against the
technical task; previous assistant prose is not a gold answer.

Long tasks request complete mechanisms, comparisons, or connected explanations
without imposing minimum or maximum word counts. Fixed summaries exercise
multi-turn response behavior with identical context across arms; they do not
simulate independently evolving long sessions. Cases and required content are
separate: generators receive only the task, never the rubric or old answers.

## Isolation and execution

[The runner](run.py) starts one new Pi process per answer, with an empty working
directory, explicit system prompt, no sessions, tools, extensions, MCP, skills,
prompt templates, or context files. It uses existing provider authentication
without exporting credentials. The parser smoke probe returned `READY` with 36
input tokens, consistent with only its tiny explicit prompt rather than the
installed global instructions.

Pi 1.5.0 runs `openai/gpt-6-astra` with `high` thinking. These are provider-reported
IDs, not a guarantee of immutable backend weights. Temperature remains the
provider default; the CLI has no temperature option. JSON events must report one
completed assistant response and a successful settled event. Retries, tools,
truncation, mismatched identities, and empty outputs fail closed. Only visible
text and usage metadata are stored; thinking content is neither saved nor scored.

A separate `openai/gpt-6-sol` process judges anonymous, shuffled responses for one
case at a time. Arm names, repetitions, source prompts, and provenance are not
sent. Each answer receives its own complete ratings. Both models belong to the
same provider/family; this is model-assisted evaluation, not independent human
review. The implementing assistant audits evidence and regressions; this audit
is not blinded to arms and is not independent human verification.

The planned maximum was 36 development answers, selection, then 24 holdout
answers, plus one judge call per case per split. Actual execution stopped after
36 development answers and six judge calls because no candidate qualified.
A post-hoc [judge sanity check](positive-controls.json) used one additional judge
call on six deliberately flawed answers and one clean control. It was added
after the zero-finding result and is not a preregistered outcome or a holdout test.

Two preliminary transport/parser smoke calls are outside the comparison. Three
concurrent requests bound resource use. No failed attempt was overwritten or
silently omitted, and no response was retried for quality.

## Reproduction

Requires the locked repository environment, Pi 1.5.0, and authorized provider
access. These commands make paid model calls; the ordinary repository gate runs
only the offline tests in `tests/test_communication_style_eval.py`.

```sh
pdm run python evaluations/communication-style/run.py generate \
  --split development \
  --output evaluations/communication-style/results/development
pdm run python evaluations/communication-style/run.py judge \
  --split development \
  --responses evaluations/communication-style/results/development \
  --output evaluations/communication-style/results/development-judgments
```

The recorded selection is `null`, so the runner refuses holdout generation.
A future experiment needs a separately frozen protocol and evidence boundary;
do not rewrite this run's candidates or select from the unobserved holdout.
Use a new output directory for a replication of the development comparison.
Existing attempt files are never replaced, and the source manifest must match.

Recompute the raw descriptive table without model calls:

```sh
pdm run python evaluations/communication-style/summarize.py development
pdm run pytest tests/test_communication_style_eval.py -q
```

The parser/runner and summary script also receive explicit Ruff and Pyright
checks. The current runtime paragraph remains unchanged; this experiment makes
no statistically general or workflow-speed claim.
