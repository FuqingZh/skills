# Sentence ablation: incomplete study, seven-case diagnostics

## Execution outcome

All **160 isolated generations** completed, with no generation failures or
retries. Three judge-control calls passed. Of sixteen original blinded
comparison calls, fifteen validated. The `c1-1` record failed the frozen literal
quality-evidence check. Its single declared identical-input retry failed too.
There are **17 comparison attempts**, all retained, and no complete eight-task
score. [summary.json](summary.json) records this incomplete status.

Both invalid attempts quoted the conclusion of `c1-drop4-1` without its Markdown
bold markers. The words were present in the answer, but the quoted string was
not a literal substring. The original runner, rubric and records were preserved;
no quote repair, normalization, replacement score selection or further retry was
performed. The post-freeze [recovery protocol](recovery-protocol.json) was committed
at `c89e4e9` before the additional call. This execution amendment is separate from
the original design frozen at `0a6fc47`.

## Available diagnostic scope

A post-hoc complete-case analysis includes `p1`, `p2`, `s1`, `s2`, `o1`, `o2`, and
`c2`: **140 answers, fourteen comparisons, seven equally weighted tasks**. Both
`c1` replicates are excluded from this analysis, including its valid second
comparison, so every included task has two repetitions. No evidence was deleted.
The ordinary-conversation long task is therefore absent; the short task only
tests repair after explicit feedback.

[partial.py](partial.py) applies the frozen scoring algorithm to this declared
subset. [partial-summary.json](partial-summary.json) retains per-task differences,
quality scores, unadjusted bootstrap intervals and selection metadata. These are
descriptive diagnostics on the available tasks, not the planned full-study
estimate or a replacement validation set.

## Sentence effects within the seven-case subset

Scores use the declared 0–100 index. Each effect is `full − drop_i`; a positive
value favors keeping that sentence in the presence of the other six. The target
column compares only its designated dimension, also rescaled to 0–100.

| Sentence | Intended function | Overall effect | Unadjusted 95% interval | Target effect | Target tasks |
| --- | --- | ---: | --- | ---: | ---: |
| S1 | Plainness and appropriate depth | +0.30 | [0.00, 0.89] | 0.00 | 7 |
| S2 | Focus and coherent reasoning | +0.60 | [0.00, 1.19] | 0.00 | 7 |
| S3 | Substantive corrections and contrasts | +0.51 | [−1.28, 2.13] | +5.00 | 5 |
| S4 | Place limits beside their claims | +0.30 | [−1.49, 2.08] | +2.50 | 5 |
| S5 | Build on established points | 0.00 | [−1.79, 1.79] | +5.00 | 5 |
| S6 | Omit unsolicited self-defense | +0.85 | [0.26, 1.62] | 0.00 | 7 |
| S7 | Answer requested clarification | +0.30 | [−1.49, 2.08] | 0.00 | 2 |

The intervals use 20,000 task-cluster bootstrap samples, seed 71. They describe
variation within this selected subset. They do not account for the missing task,
judge disagreement, prompt-selection history, model-family dependence or multiple
comparisons. Zero-width target intervals where all observations equal zero do
not establish that a sentence has no effect.

The full paragraph scores **99.40**, versus **98.00** for the minimal role anchor:
net **+1.40** points, interval **[0.30, 2.72]**. The S6/S7 interaction is **+0.04**,
interval **[−1.74, 1.83]**. Near-ceiling scores and seven selected task clusters
provide little resolution for stable importance estimates.

### Where the apparent effects arise

- **S1:** its overall gain comes entirely from one wording finding in `o1`; its
  plainness/depth dimension does not change.
- **S2:** its gain comes from unnecessary framing or repetition in `p1` and `o1`;
  the focus/coherence dimension does not change.
- **S3:** the target gain comes from unnecessary contrasts in `p1` and `p2`.
  Its overall gain is partly offset by the full arm's ambiguous `o2` heading.
- **S4:** the target gain comes from one p-value answer's insufficiently local
  qualification. That is one task, not broad evidence of a persistent effect.
- **S5:** the target gain comes entirely from repeated endings in the p-value
  task. Its overall gain is canceled by the full arm's `o2` heading defect.
- **S6:** its largest overall point estimate comes from contrast/repetition
  findings in `p2`, `s2` and `o1`. The self-defense dimension shows no difference.
  Removing S6 also leaves S7's reference unresolved, as declared in the design.
- **S7:** its target dimension shows no difference in either applicable task.
  `c2` explicitly requests a repair, so success there does not measure spontaneous
  prevention of defensive commentary.

S3, S4 and S5 have signals in their intended dimensions worth investigating.
The observations do not support assigning any sentence a fixed percentage weight.
Deleting a sentence changes a whole prompt, the marginal effects overlap, and
these effects do not sum to the paragraph's net effect. Normalizing the seven
point estimates to 100% would manufacture a distribution of importance.

## Content, style and audit boundary

Within this subset, full and all deletion arms have zero model-rated required
content omissions and zero critical findings. The minimal arm has one omission
and one critical finding, both attached to the first `o2` heading. Its causal
wording is questionable; the implementing assistant considers the critical-error
classification debatable. The raw rating remains unchanged.

The full arm has zero model-rated style findings. Deletion arms have 0–4 each;
minimal has one. This revised grader detects some natural contrasts and repeated
endings that the prior rubric missed. The separate [audit](./audit.md) also finds
uneven treatment of similar passages. Passing the authored controls does not
establish broad sensitivity, consistency or agreement with the user's preferences.

The unblinded audit read **86 complete answers**, covering all 28 flagged answers
in the diagnostic subset, all forty `p2`/`c2` answers, each sentence's largest
absolute task difference and three flagged answers from the excluded valid
`c1-2` comparison. It also inspected the offending original answer. No audit
judgment was substituted into the model scores.

## Cost and disposition

Estimated total execution cost is **USD 9.28494**, including all 160 generations,
three controls and seventeen comparison attempts. Provider-reported billing
totals were unavailable. The subset arm costs and judge cost in the partial
summary cover only included evidence; `total_execution_cost` includes excluded
and failed attempts as well.

The planned full-study sentence scores remain unavailable. The baseline runtime
paragraph, installer, installed skills, setup and release tag are unchanged.
No automatic adoption or further model calls follow from this diagnostic report.
