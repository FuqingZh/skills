# Sentence-level style ablation

This study tests the seven sentences of the revised
[cross-domain paragraph](../cross-domain/prompts/revised.txt). Sources were
frozen at `0a6fc47` before any model calls. Existing evaluations and runtime
instructions remain unchanged.

**Status: incomplete.** All 160 generations finished. Fifteen of sixteen original
comparison records validated; the sole declared retry of the remaining record
also failed literal-quote validation. The full-study score is unavailable.
[Results](./results.md) report clearly labeled post-hoc diagnostics on seven
fully scored cases, with an [unblinded audit](./audit.md).

## Treatments

| ID | Sentence | Primary dimension |
| --- | --- | --- |
| S1 | Write plainly and directly, with the depth and structure the question needs. | Plain wording and appropriate depth |
| S2 | Focus on the subject and develop the reasoning coherently. | Focus and coherence |
| S3 | Use corrections, contrasts, and qualifications to add substantive information. | Useful distinctions |
| S4 | Place uncertainty and limits alongside the claims they qualify. | Local qualification |
| S5 | Build on established points to move the discussion forward. | Progression |
| S6 | Omit unsolicited commentary defending your wording, intentions, or approach, or explaining what your answer should not be taken to mean. | No unsolicited self-defense |
| S7 | Address those matters when the user raises them. | Respond to requested clarification |

Ten conditions are defined in [sentences.json](sentences.json):

- `full`: all seven sentences;
- `drop1` through `drop7`: remove exactly the named sentence;
- `minimal`: no style paragraph;
- `drop67`: remove both last sentences to examine their dependency.

All conditions share the sole role anchor “You are an AI assistant.” Remaining
sentences retain their words, order and paragraph grouping. Line wrapping is
normalized; the full paragraph's words match the prior candidate exactly. The
minimal condition still receives the same user task and the model's pretraining.
It measures the incremental paragraph effect relative to this anchor, not an
uninstructed or untrained model.

S7's “those matters” refers to S6. Literal deletion of S6 leaves an unresolved
reference; no repair is introduced into the other sentence. The joint deletion
helps distinguish their interaction. The S6 marginal effect still includes any
cost of that residual reference.

## Cases, isolation and calls

The eight [cases](cases.json) retain the previous cross-domain tasks and content
criteria byte-for-value, adding only a declared list of applicable quality
dimensions. Four domains each have one long and one short task. These previously
observed development cases are not held-out data.

Each condition receives two fresh responses per task: **160 generations**.
`openai/gpt-6-astra`, high reasoning, provider-default temperature, three workers,
300-second call limit, frozen ordering seed 71. Each request runs in an isolated
Pi process with no session, tools, skills, context files, extensions or MCP. No
engineering instructions or inherited conversation are loaded. The same fixed
case histories are supplied across all conditions.

The `openai/gpt-6-sol` judge receives ten independently shuffled anonymous
answers for one task and replicate at a time: **16 comparison calls**. It sees
the task and rubric, never the treatment prompts, arm identities or expected
scores. Repetition labels pair blocks for analysis, not common model random
seeds. Visible outputs and usage are stored; hidden thinking is neither saved
nor scored. No quality-based retries or discarded attempts are permitted.

## Measurement calibration

The previous rubric produced no natural style findings. This study freezes a
more sensitive [judge](judge.txt) before generation. It distinguishes useful
synthesis from an unnecessary opposing clause inside that synthesis, and allows
one local defect to lower one quality dimension without rejecting the whole
answer.

Three [control calls](controls.json), completed before generation, test:

1. A naturally observed unnecessary contrast versus a direct transition, plus
   an unsolicited defensive afterword.
2. Necessary p-value correction versus an objectively wrong probability claim.
3. Explicitly requested title clarification versus evading that question.

Expected labels are withheld. Low scores require literal answer-specific
evidence. Controls must detect the contrast/defense, preserve necessary negation
and clarification, and detect the factual error. Failure stops the study.
Passing establishes these limited distinctions, not broad grader reliability or
agreement with a human on natural answers.

## Scores and sentence effects

Seven quality dimensions use anchored integer scores from 0 to 4: failed,
mostly absent, substantially impaired, one minor defect, and no evidenced defect.
Only task-applicable dimensions are scored. Required content, critical errors
and style findings are reported independently; a style advantage does not erase
a correctness regression.

An answer's overall score is 25 times its mean applicable dimension score.
Average the two repetitions within each task, then weight the eight tasks equally.
This declared equal-weight index is a measurement convention, not an estimated
human utility function. The ordinal scale does not establish equal subjective
distance between adjacent levels.

For sentence *i*:

```text
marginal effect_i = score(full) - score(drop_i)
paragraph net effect = score(full) - score(minimal)
interaction_67 = score(full) - score(drop6) - score(drop7) + score(drop67)
```

Positive marginal points favor keeping the sentence; negative points favor its
deletion under this experiment. Report the overall effect, corresponding primary
dimension effect, per-task differences and correctness regressions. Effects are
conditional on the other sentences being present. They need not sum to the
paragraph's net effect and cannot be converted into fixed weights totaling 100%.
This is not a Shapley-value/all-subset experiment.

Use 20,000 task-cluster bootstrap samples with seed 71 for unadjusted percentile
95% intervals. Only eight task clusters exist, and S7's target dimension has two.
Reused full responses correlate the comparisons. Multiple comparisons, ordinal
scores, case selection and same-family judging limit interpretation: these are
exploratory uncertainty summaries, not confirmed statistical significance.

## Evidence and reproduction

The following describes the original full-study execution. Its summary command
still fails on the retained invalid record. [summary.json](summary.json) is an
explicit incomplete-status marker, not a complete numerical summary.

After the first failure, [recovery-protocol.json](recovery-protocol.json),
[recovery.py](recovery.py), [recovery-manifest.json](recovery-manifest.json) and
the failed original were committed at `c89e4e9` before one identical-input retry.
It failed too; neither attempt was overwritten, repaired or normalized.

[partial.py](partial.py) is a disclosed post-hoc analysis adapter. It selects
only the seven tasks with both original comparison records valid and reuses the
original scoring algorithm. Both `c1` replicates remain in the evidence, excluded
from these diagnostics only. [partial-summary.json](partial-summary.json) includes
the selection, 140 analyzed responses, all 160 generated responses and all costs.
Its intervals describe this selected subset and do not fill the missing task.

[protocol.json](protocol.json) fixes the design and
[execution-manifest.json](execution-manifest.json) hashes the execution source,
inputs and shared parent runner. [benchmark.py](benchmark.py) reuses its isolated
transport and content/evidence validator. Frozen sources must match before calls;
existing artifacts cannot be overwritten. Incomplete results prevent summary.

Paid execution, once per fresh study workspace:

```sh
pdm run python evaluations/communication-style/sentence-ablation/benchmark.py calibrate
pdm run python evaluations/communication-style/sentence-ablation/benchmark.py generate
pdm run python evaluations/communication-style/sentence-ablation/benchmark.py judge
pdm run python evaluations/communication-style/sentence-ablation/benchmark.py summarize
```

Offline checks:

```sh
pdm run python evaluations/communication-style/sentence-ablation/partial.py
pdm run pytest tests/test_sentence_ablation_eval.py -q
```

The implementing assistant audits every flagged answer, all `p2` and `c2`
responses, and the largest absolute task effect per deleted sentence. This audit
is unblinded and separate from raw model scores. No automatic prompt adoption,
installation, release change or upstream dependency change is authorized by this
experiment.
