# Request-scoped explanation pilot

Status: completed local pilot, 2026-11-17. **Do not adopt the paired candidate
unchanged on this evidence.** It made GPT's requested evaluation more explicit
in both repetitions, but did not reliably remove unsolicited commentary or
completion-report reminders. One candidate completion report failed outright.
Neither installed skill nor either repository skill entrypoint was changed.

## Why this comparison was needed

The [framing pilot](20261117-explanation-framing-pilot.md) recorded a user
preference for explaining an author without unsolicited objections, corrections,
acceptance warnings, or demands for proof. It did not test explicitly requested
criticism. The [transfer pilot](20261117-explanation-transfer-pilot.md) found
neither reliable improvement nor a repeatable cross-task regression from
shortening that guidance. Its content coverage findings were not accuracy
certification.

The [release evidence summary](20261117-v2.0-release-evidence-summary.md) also
records two important constraints: the user's preference was not simply for
shorter answers, and earlier automated judges did not reliably reproduce the
user's preferences. Those conclusions remain separate from this experiment.

The current wording can be read as prohibiting correction even when requested.
That creates a textual tension with teaching feedback and strategy evaluation.
This pilot tests whether making the request boundary explicit improves behavior,
rather than assuming that the textual tension necessarily causes refusals.

## Frozen arms

Baseline: repository `e17e2fd`, matching the installed `plainspoken` and
`dissect` entrypoints byte for byte. Both skills were supplied in both arms.
Only the following passages changed; topic references were not loaded.

### Plainspoken candidate

Replace the two-line instruction beginning “Develop the explanation without
adding corrective commentary” with:

> Keep the response focused on the requested explanation, judgment, or correction.
> Omit unsolicited evaluative asides and reminders about how the reader should
> receive the answer. When evaluation or correction is requested, state it directly
> and explain its basis.

### Dissect candidate

Replace the paragraph beginning “Reconstruct the argument without adding your
own objections” with:

> When asked to explain an author or argument, reconstruct it in its own terms
> without adding an unsolicited critique. When asked to evaluate, compare, forecast,
> or correct, develop a supported judgment responsive to that request. If both
> explanation and evaluation are requested, make clear which claims belong to the
> source and which are your assessment. Do not append an evaluation stage by default.
> Explain source-internal disagreements as part of the argument. Attribute claims
> accurately; do not invent support.

The final source-disagreement and attribution requirements were preserved, not
removed. Because both passages changed together, this study cannot attribute an
effect to either skill individually.

## Design and execution

Eight tasks × two models × two arms × two repetitions: **64 fresh generations**,
forming 32 within-model, within-task pairs. Previous outputs were not reused as
controls.

| ID | Task | Origin |
| --- | --- | --- |
| P | Explain p-values and their statistical basis | Exact earlier transfer context |
| D | Explain whether serializability requires actual serial execution | Exact earlier transfer context |
| H | Explain LBJ's cross-party legislative methods | Exact earlier transfer context |
| Z | Continue a source-grounded lesson on concrete universality | Exact earlier framing context |
| E | Reconstruct a supplied library-acquisition argument | New synthetic explanation request |
| V | Evaluate the same argument, its strengths, weaknesses, and decision-changing evidence | New synthetic evaluation request |
| C | Correct a learner's mistaken inference from concurrency to non-serializability, with a counterexample | New synthetic feedback request |
| F | Report completed documentation changes and checks; full-text access limits are already known | New completion-report fixture |

Generation used Pi 1.5.2 with `openai-codex/gpt-6-astra` and
`openrouter/deepseek/deepseek-v4-pro-0813`, requesting medium thinking.
The retained metadata does not independently establish an effective thinking
level. No generation seed or temperature was fixed; seed 42 randomized judge
identifiers, not model sampling.

The earlier CLI isolation was retained: a minimal base system prompt, two
repeatable `--append-system-prompt` arguments, an attached context, and no tools,
extensions, MCP, skill discovery, prompt templates, themes, context files, or
persistent session. Offline mode disabled incidental discovery, not model API
calls. Each generation used a new process. Version order reversed across
repetitions and models. Two model queues ran concurrently, with a 180-second
per-call timeout and retries disabled.

All 64 calls exited normally with a final stop, the requested provider/model,
and zero recorded retry or tool-execution events. There were no transport
failures or timeouts. **Transport success did not imply answer success**:
`F-deepseek-candidate-r1` contained only a textual pseudo-tool invocation.
It remains in the denominator as an output failure.

The four historical contexts and baseline files passed byte comparisons against
their originals before execution. Input and runner hashes passed after execution.
Initial preparation copies outside `frozen/` failed a byte check and were not
used; corrected, verified snapshots were frozen before any generation.

## Review method

Jev 1.14.0 through TypeSafe received randomized response IDs, relevant context,
and full visible answers, without model or arm labels. Each response had separate
questions for:

- Probability of an unsolicited evaluative aside, acceptance warning, unnecessary
  capability reminder, or evidence demand.
- Task coverage on three ordered levels: 0 = central task failed or contradicted;
  1 = partial with a central omission/error; 2 = central requirements addressed
  without an identified central error.

Requested criticism/correction, source-internal disputes, necessary definitions
and assumptions, and accurate attribution were explicitly excluded from the
aside category. The pre-review flag thresholds were at least 0.8 for presence,
at most 0.2 for absence, and uncertain between them.

There were 11 main judge calls with 128 questions; Z was split into four
two-answer batches to stay below the request-size limit. One additional call
tested six constructed controls with 12 questions. These controls were added
after the P/D results, not preregistered. They contrasted ordinary explanation,
unrequested criticism, correct/incorrect feedback, and concise/redundant reports.

The author also read all 64 visible answers and recorded an **unblinded agent
review**. This was not new human preference feedback or a complete factual audit.
The observations below do not overwrite the judge's returned probabilities.

## Findings that matter for adoption

### Requested evaluation improved locally, not across every model

On V, both current GPT answers explained strengths, weaknesses, and relevant
evidence, but framed the answer mainly around the author's argument. Both
candidate GPT answers directly stated their own supported judgment. This was a
change in directness, not a transition from total refusal to evaluation.

Jev assigned the highest coverage level probabilities of **0.77 and 0.88** to
current GPT, versus **0.99 and 0.99** to candidate GPT. DeepSeek already gave
explicit judgments under both versions; its corresponding probabilities were
0.99–1.00. This supports a local GPT result, not a general improvement.

### Requested correction was not suppressed by the current version

All eight C answers rejected the mistaken inference and supplied a valid
independent-data counterexample. The candidate did not unlock a missing behavior.
D likewise preserved the main distinction in both arms.

Some technical qualifications remained wrong or incomplete. In C, DeepSeek's
second repetition in both arms generalized the conflict-graph test to
serializability overall, rather than conflict serializability. Some D answers
treated matching final states as sufficient without accounting for reads.
Successful correction of the learner's central mistake is not full technical
accuracy.

### The actual completion-report problem persisted

All four GPT F answers, across both arms and repetitions, repeated that full-text
access had not been verified, although the fixture said the user already knew
this and requested only changes and checks.

DeepSeek current repeated the limit in one of two answers. Candidate omitted it
in its one usable report, but its other answer was only a pseudo-tool invocation.
Thus the eight F outputs comprise:

| Arm | Usable reports | Reports repeating the known limit | Output failures |
| --- | --- | --- | --- |
| Current | 4/4 | 3/4 | 0/4 |
| Candidate | 3/4 | 2/4 | 1/4 |

The candidate's lower reminder count is not a clean gain: one response did not
deliver a report at all. No command was actually executed by that response.

### Explanation-only tasks did not show a reliable reduction in commentary

E retained explanatory reconstruction in both arms without an appended critique
stage. However, some DeepSeek outputs in both arms strengthened “harder to buy”
into effectively “no alternative channel”; absence of criticism is not source
fidelity.

P continued to attract misconception lists and usage cautions in both arms.
Candidate DeepSeek r2 also began by claiming it could not read the attached
context. Candidate r1 stated exact uniformity of null p-values without the
continuous/exact-calibration condition.

On Z, both candidate GPT repetitions included additional proof or applicability
cautions. For example, r1 added “也不能据此直接推出当下应当实施恐怖的行动主张”;
r2 added that the passage had not independently proved a historical necessity.
Those additions go beyond identifying whose argument is being reconstructed.
Current outputs were not uniformly clean either: GPT r1 added a proof caveat,
and DeepSeek r1 warned that the analogy need not be accepted as psychological fact.

Candidate DeepSeek r2 also conflated a metaphor with its referent, stating
“骨头既是排尿器官，也是授精器官”. The supplied source uses a phallic metaphor
to discuss two readings of “Spirit is a bone”; it does not identify a bone as
that organ. It also weakened the source's necessity claim into only conceptual
order. These are observed errors, not proof that the candidate wording caused
them. H showed no repeatable cross-model advantage.

## What the automated scores can and cannot tell us

The aside judge returned **zero high-probability presence flags in both arms**.
Fourteen responses were uncertain: six current and eight candidate. This is not
evidence of zero unwanted commentary.

The constructed controls were easy for the judge: unsolicited criticism and a
redundant warning received probabilities 0.98 and 0.93; their clean counterparts
received 0.02. A plainly wrong correction had probability 0.91 on coverage level
0. But the actual F reports repeating the known limit received aside probabilities
only 0.02–0.04. Coverage predictions also missed specific P/Z errors noted above.

Consequently, this judge passed conspicuous controls but was not sufficiently
sensitive to the user's subtler relevance preference. Its coverage score was not
an accuracy audit. Do not interpret near-ceiling results as verified success.

The complete per-task/model numerical summary follows. Each cell lists r1, r2.
Aside values are model probabilities. Coverage values are model-predicted
positions on the **0–2 ordered scale**, not percentages or human ratings.

| Task | Model | Current aside probability | Candidate aside probability | Current coverage | Candidate coverage |
| --- | --- | --- | --- | --- | --- |
| P | gpt | 0.27, 0.22 | 0.33, 0.26 | 1.98, 1.99 | 1.97, 1.98 |
| P | deepseek | 0.23, 0.30 | 0.23, 0.58 | 1.96, 1.98 | 1.95, 1.95 |
| D | gpt | 0.10, 0.12 | 0.14, 0.14 | 1.98, 1.98 | 1.99, 1.99 |
| D | deepseek | 0.16, 0.08 | 0.10, 0.11 | 1.98, 1.99 | 1.98, 1.99 |
| H | gpt | 0.04, 0.04 | 0.04, 0.03 | 1.93, 1.85 | 1.91, 1.94 |
| H | deepseek | 0.03, 0.04 | 0.04, 0.06 | 1.25, 1.45 | 1.85, 1.34 |
| Z | gpt | 0.39, 0.14 | 0.35, 0.27 | 1.94, 1.97 | 1.96, 1.96 |
| Z | deepseek | 0.55, 0.09 | 0.07, 0.50 | 1.95, 1.95 | 1.93, 1.96 |
| E | gpt | 0.03, 0.02 | 0.04, 0.03 | 1.98, 1.98 | 1.98, 1.96 |
| E | deepseek | 0.03, 0.03 | 0.03, 0.03 | 1.97, 1.98 | 1.99, 1.98 |
| V | gpt | 0.06, 0.07 | 0.07, 0.07 | 1.76, 1.88 | 1.99, 1.99 |
| V | deepseek | 0.07, 0.06 | 0.08, 0.07 | 1.99, 1.99 | 1.99, 1.99 |
| C | gpt | 0.03, 0.04 | 0.03, 0.02 | 1.88, 1.91 | 1.91, 1.87 |
| C | deepseek | 0.03, 0.03 | 0.03, 0.03 | 1.92, 1.89 | 1.92, 1.91 |
| F | gpt | 0.02, 0.03 | 0.02, 0.03 | 1.41, 1.40 | 1.40, 1.41 |
| F | deepseek | 0.03, 0.04 | 0.30, 0.03 | 1.78, 1.39 | 0.07, 1.78 |

No pooled win rate, significance claim, or release-wide quality score is inferred
from these convenience tasks and two repetitions.

## Decision and remaining scope

**Keep the current installed versions; do not promote this paired candidate as a
stable quality improvement.** The request-scoping principle remains reasonable,
and V provides a narrow reason to retain it for further design. However, the
candidate did not fix the user's completion-report problem, did not consistently
remove unsolicited commentary, and had an output failure.

If the wording is refined further, a more diagnostic comparison would change one
skill at a time: keep task interpretation/evaluation scope in dissect, and
expression relevance in plainspoken. That is an untested design direction, not
an adopted replacement or a commitment to another run.

This was explicit skill-content injection, not native activation or the complete
Memex tutor/persona stack. Forecasting, mixed explanation-plus-evaluation requests,
implicit correction requests, and strategy-persona interactions remain untested.
There is no cost, latency, productivity, learning-outcome, or general human
preference claim.

## Local evidence and validation

Private evidence lives at `/tmp/skills-scope-ab.Qkb2no/frozen/`. It includes
snapshots, contexts, the runner, per-call final text and execution metadata,
stderr, blind mapping, judge requests/results, author observations, and aggregate
scores. The parent directory is mode 700. Hidden reasoning was discarded rather
than persisted. Raw sessions, book passages, and complete answers are not copied
into this repository. This temporary directory is not a durable public archive.

| Artifact | SHA-256 |
| --- | --- |
| Current plainspoken | `4d57328457f51596822748e150fe4b1ccd1c56f0fcc3d580ad0aa601c274be9b` |
| Candidate plainspoken | `bc5f817cacfa6b3891396c6d741c5ccdf641c9882b199c3c48a5ae3ac9220168` |
| Current dissect | `c43a51d499f70f285a805426af91b373adf123544ccee18901ff1ca1646d8ba1` |
| Candidate dissect | `e39db659b188f870de6c0b8d6dcf188b4f2e2d01e3084769f34a904ffd70e6d8` |
| Complete evidence manifest | `fb27263fd867bfbada266b385bf952b7fbaee17236712cb4f07a2cbbe94fa54c` |

Runner syntax compilation and input/runner integrity checks passed. Final
installed files still matched the baseline. Targeted Markdown lint, repository
link validation (211 files), and worktree/staged whitespace checks passed. Active
LSP diagnostics found the new report clean and reported two ambiguous-link warnings
on unchanged `archive/README.md` links in `docs/README.md`. These checks validate
the report and its links, not the quality of generated answers.
