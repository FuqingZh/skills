# Complete talk-normal: observed results

## Finding

The complete upstream prompt produced shorter answers in this run while matching
the baseline on the frozen content rubric. The comparison did **not** demonstrate
a reduction in the six target style problems: the judge found none in either
arm. No global instruction or installed skill was changed.

All 48 generations and 12 blinded judge calls completed successfully, without
retries, malformed judgments, or discarded attempts. The frozen protocol and
source identities are described in the [study README](README.md). Raw outputs
are in [results/benchmark/](results/benchmark/) and ratings in
[results/benchmark-judgments/](results/benchmark-judgments/).

## Frozen-rubric judgments

| Measure | Baseline | Full talk-normal |
| --- | ---: | ---: |
| Responses | 24 | 24 |
| Required-content omissions | 2 / 88 | 2 / 88 |
| Responses with omissions | 2 | 2 |
| Critical findings | 0 | 0 |
| Target style findings | 0 | 0 |
| Clarity: clear / mixed | 23 / 1 | 24 / 0 |

These are model judgments, not independently established correctness or human
preferences. The 88 requirement observations are nested within 24 responses to
12 tasks; they are not 88 independent tasks. The only content omissions were the
same `d2` criterion in both repetitions of both arms. No long-response style
drift was flagged, so this sample cannot estimate prevention of such drift.

The shared `d2` criterion includes the external-side-effect boundary in addition
to checkpoint state/progress. All four answers explain the computational
recovery relationship, but none explicitly separates replaying computation from
re-executing external effects. The [author audit](audit.md) retains the original
rubric concern: that extra boundary is weakly elicited by the user's task. Scores
remain unchanged and do not establish a comparative regression.

The single mixed-clarity rating concerns `d5-baseline-2`: it first identifies the
ambiguous table as a TLB, then acknowledges that the fields alone cannot settle
its type. Both talk-normal repetitions retain the uncertainty consistently.
This isolated difference is insufficient to establish general superiority.

## Length, usage, and timing

| Measure | Baseline | Full talk-normal |
| --- | ---: | ---: |
| Total visible characters | 43,598 | 34,719 |
| Long-answer total characters | 39,220 | 31,803 |
| Long-answer median characters | 3,214.5 | 2,513 |
| Short-answer total characters | 4,378 | 2,916 |
| Short-answer median characters | 312.5 | 278 |
| Input tokens | 5,064 | 25,224 |
| Reported output tokens | 30,558 | 26,568 |
| Reported total tokens | 35,622 | 51,792 |
| Mean seconds per response | 59.171 | 55.172 |
| Long-answer mean seconds | 102.973 | 93.741 |
| Short-answer mean seconds | 15.369 | 16.604 |
| Estimated generation cost, USD | 1.57854 | 1.58064 |

Visible text decreased **20.4% overall**, 18.9% for long answers and 33.4% for
short answers. Reported output tokens decreased 13.1%. The longer system prompt
increased input tokens approximately fivefold and total reported tokens 45.4%,
leaving estimated generation cost essentially unchanged. Reported output-token
accounting can include reasoning billing; visible characters and token totals
measure different things. No hidden thinking was saved or scored.

Mean response time decreased 6.8% overall; short answers were slightly slower.
These are descriptive observations under concurrent execution, not a general
latency or workflow-speed result. Pi estimates costs rather than reporting actual
bills (`totalFromProvider: false`). Judging added an estimated USD 0.24648;
the follow-up's total estimated model cost was **USD 3.40566**.

[summary.json](summary.json) is mechanically reproduced by:

```sh
pdm run python evaluations/communication-style/talk-normal/benchmark.py summarize
```

## Task-boundary checks and interpretation

The implementing assistant read 20 full answers: all four answers each for
`d2`, `d5`, `h2`, `h5`, and `h6`, including every flagged answer. This was an
unblinded review, separate from the scores; details are in [audit.md](audit.md).

- Necessary correction remained present in `d5` and `h2`.
- Both upstream `h5` answers supplied the requested analogy and its limit.
- Both upstream `h6` answers preserved unknown write outcomes, authoritative
  result checks, and idempotency-aware retry precautions.
- The upstream long answers inspected were still multi-section explanations
  containing thousands of characters, despite its 3–5-sentence conceptual rule.
  This run does not establish that strict sentence-cap enforcement would
  preserve the same coverage.

**Supported conclusion:** full talk-normal is a plausible concision candidate on
these tasks; it produced shorter visible answers without additional omissions
under the frozen rubric. It did not demonstrate fewer target style defects or
lower cost. The rubric checks specified content, not every useful teaching detail
or the user's overall preference, so shorter answers with equal scores do not
prove equal learning value or a better reading experience.

**Decision:** retain the current global paragraph. The experiment supplies a
concrete comparison for discussion, without automatic adoption. A new adoption
claim would need the user's assessment of actual answer pairs or another
explicitly scoped evaluation. This run used one generator and a same-family
judge; its cases and rubric were already known, and no new unseen test set was
introduced. The prior study's former holdout responses are now observed in this
separate follow-up, not retroactively used as a successful selection holdout.
