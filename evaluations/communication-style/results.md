# Communication-style results

## Decision

**Retain the current runtime paragraph.** Neither candidate demonstrated the
required reduction in unwanted style on the frozen development set. No candidate
was nominated, and the planned 24 holdout answers were not generated.

This is an inconclusive prompt comparison with a style-floor result: the judge
reported zero target-style findings for every arm. It does not establish that
all three prompts are equivalent or that natural conversations are problem-free.

## Execution

- Inputs and runner frozen in commit `5838e50` before generation; SHA-256 values
  are in [manifest.json](manifest.json).
- Six development tasks, three arms, two fresh runs each: 36/36 completed.
- Three naturally long tasks and three short tasks; 18 answers in each group.
- Six separate, anonymously ordered judge packets completed; no generation or
  judging retries, failed attempts, or malformed outputs.
- Separate process/context per answer; explicit system text; no ambient global
  instructions, sessions, skills, MCP, extensions, or tools.
- `openai/gpt-6-astra`, high thinking; `openai/gpt-6-sol`, high thinking, for judging.
- [Post-hoc controls](audit.md#post-hoc-judge-sanity-check): six planted style
  categories identified, clean control unflagged. No candidate outputs changed.

## Raw model judgments

Each row has six responses. Missing content counts rubric items, not whole
answers. These are model judgments, not independently verified ground truth.

| Arm | Task length | Style-flagged answers | Missing / required items | Critical findings | Median visible characters |
| --- | --- | --- | --- | --- | --- |
| Baseline | Long | 0/6 | 2/28 | 0 | 2,989.5 |
| Direct | Long | 0/6 | 2/28 | 1 | 2,814.5 |
| Example | Long | 0/6 | 2/28 | 0 | 2,830.5 |
| Baseline | Short | 0/6 | 0/14 | 0 | 284 |
| Direct | Short | 0/6 | 0/14 | 0 | 277 |
| Example | Short | 0/6 | 0/14 | 0 | 306 |

The judge rated all 36 answers clear. Counts for every style category and
opening/middle/ending region are zero, as are length-normalized style frequencies.
This provides no estimate of how well the candidate prevents late-answer drift.

All missing items concern the same secondary external-side-effect boundary in
`d2`. The one critical finding is an unqualified claim that a checkpoint only
records progress. See [audit.md](audit.md) for context, source cross-checking,
review coverage, and uncertainty about severity and causal attribution.

## Output and resource observations

| Arm | Visible characters, total | Input tokens | Output tokens reported by Pi | Mean seconds per answer | Estimated generation USD |
| --- | --- | --- | --- | --- | --- |
| Baseline | 21,167 | 2,614 | 14,941 | 63.735 | 0.77319 |
| Direct | 19,533 | 2,470 | 13,355 | 56.020 | 0.69245 |
| Example | 21,545 | 2,974 | 14,717 | 64.261 | 0.76559 |

Characters include Markdown and code; token usage follows the provider/Pi fields.
These output-token counts are distinct from visible-character counts and may
include reasoning billing according to the provider's accounting. Reasoning
usage counts are retained as metadata; its content is never saved or scored.
Costs are Pi estimates (`totalFromProvider: false`), not billing confirmations.
Development generation estimates total USD 2.23123 and judging USD 0.18727.
The separate control and smoke calls are excluded from this table.

The shorter direct output and lower observed duration do not demonstrate better
answers or a workflow-speed improvement. Two repetitions, concurrent requests,
backend variability, and repeated tasks do not support a causal timing claim.

## Limits and next evidence needed

- No eligible development candidate means no held-out comparative evidence.
- Cases are independently written reconstructions or synthetic tasks, not replay
  of the conversations that originally motivated the user's preferences.
- The author saw the specifications and developed the rubric; no independent
  human preference assessment has occurred. The judge shares the generator's
  provider/model family. Its narrow forced-colloquialism definition may miss
  stylistic annoyances that preserve literal meaning.
- The obvious controls show that the evaluator can flag planted defects, without
  showing that it detects subtle awkwardness in natural long answers.
- No no-rule arm was tested; this experiment cannot establish the necessity of
  the existing paragraph. It also says nothing about the other global paragraphs.
- Fixed summaries cover bounded follow-up answers, not evolving tool-heavy
  sessions or long-context instruction drift.

A future comparison needs reviewed examples that reproduce the unwanted behavior
and a rubric calibrated to the user's judgments. Preserve these results and
freeze any changed protocol separately; do not tune on this run and relabel it
as held-out evidence. No such follow-up is started by this delivery.

## Reproducible evidence

[development-summary.json](development-summary.json) is generated by
[summarize.py](summarize.py) from the 36 response files and six judgment files in
`results/`. [selection.json](selection.json) records the no-adoption decision.
The offline repository tests reproduce the summary and check coverage, quotes,
input integrity, rejected output reuse, and holdout refusal without a candidate.
