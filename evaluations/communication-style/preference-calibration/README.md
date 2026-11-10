# Human preference calibration

Status: **v3 calibration executed; not selected for holdout**. All 24 calls were
structurally valid. Among seven labeled style pairs, four agreed in both orders,
one disagreed, and two had order conflicts. Runtime prompts remain unchanged.

See the [implementation plan](../../../docs/implementation-plans/communication-style-preference-optimization.md),
[five-check rubric](rubric-v3.md), [admission review](admission-v3.json) and
[results with full author audit](results-v3.md). Holdout remains unopened for
human annotation and model scoring; the author has reviewed source comparability.

See the [first-round review](review-round-1.md),
[human labels](labels.round-1.json), [transcription notes](feedback.round-1.json),
[revised reader instructions](instructions-v2.md) and [rubric draft](rubric-v2.md).
D09 is excluded from style-preference scoring; D01 and D08 have no assigned
winner. D03 retains the user's preference and a mixed-comparison review flag.
The original [packet](calibration.md), instructions, renderer and blank
[label template](labels.template.json) remain reproducible historical inputs.
Do not use that unclassified packet as the next scoring round.

## Purpose and evidence boundary

This stage tests whether a future automatic judge understands the user's
contextual preferences. It does not compare complete system prompts or estimate
sentence weights. The 24 pairs are deliberately authored local contrasts,
including adaptations of previously saved public responses. They are not 48
fresh model responses or a natural prevalence sample.

The packet supplies the context relevant to each local comparison. Some contexts
summarize preceding discussion; this is not full historical replay or a test of
long-session behavior. Longer natural answers and full instruction-stack trials
remain later obligations before claiming general prompt improvement.

There is no author-supplied answer key. Probe names describe hypotheses, not gold
labels. Necessary negation, useful synthesis, uncertainty and explanatory depth
are included alongside possible self-defense and repetition. Natural alternative
phrasings and a formatting pair permit genuine ties or unresolved preferences.

## Split and provenance

[pairs.json](pairs.json) contains 24 pairs grouped into eight existing source-case
families. Each family contributes three related pairs and belongs to one split:

| Split | Source families | Pairs |
| --- | --- | ---: |
| Calibration | Responsibility, statistical correction, friendship, education inequality | 12 |
| Holdout | Requested title framing, observational study, editorial titles, editing feedback | 12 |

Both splits cover philosophy, science, sociology and ordinary conversation.
Variants of the same case, including context changes applied to the same answer
pair, stay together. These source topics appeared in earlier experiments; the
holdout is reserved from this judge-calibration loop, not an unseen independent
benchmark. The author has seen all unlabelled materials. The small number of
families limits statistical claims.

Each pair records its source case. Where a saved response informed the contrast,
it also records an exact excerpt and repository-relative response path. Tests
verify the excerpt against that response. Candidate wording may be edited or
newly authored; it is never presented as an unmodified complete model answer.
No new private transcripts were read or copied.

The reader-facing packet omits sources, probe names and editing direction.
Ordering and A/B assignment are independently randomized using seed 42. This is
presentation-level blinding; the repository sources are inspectable, not secret.
No holdout reader packet or holdout labels have been collected yet. Avoid opening
holdout material while making calibration judgments.

## Annotation and evidence

Preference labels are `A`, `B`, `tie`, or `uncertain`; a blank label is pending.
A tie means no material preference. Uncertain means the reader cannot decide.
Neither implies that both answers are correct. A reason can flag that both are
poor even when one is preferred.

Content labels are separately optional: `A`, `B`, `both`, `none`, or `uncertain`.
A blank content label is unknown, never evidence of no regression. Optional
paragraph IDs such as `A1` and `B2` identify the displayed text. The resolver
copies that exact paragraph, preserving Markdown, rather than asking a judge to
retype a quotation. It rejects unknown or repeated IDs. Valid location does not
prove that the cited paragraph supports the judgment; that remains a semantic
review obligation.

The label file includes a SHA-256 of the complete displayed packet, including
instructions and order. Changed material cannot silently inherit old labels.
The validator reports labeled and content-labeled counts; an empty template
passing structural validation does not mean annotation is complete.

## Next stages after human feedback

First classify comparison purpose and reject unmatched factual verdicts from
style-preference scoring. Independent correctness controls belong in a separate
check, and mixed information-coverage changes need explicit review. Apply this
admission review to reserved pairs before enabling the next judge run.

1. Preserve the human choices and reasons. Do not fill absent answers, infer
   content approval, or replace disagreement with the author's expected label.
2. Use calibration labels to refine a short pairwise rubric. Keep content checks
   separate from style preference. Study disagreements before expanding calls.
3. Evaluate each pair in both A/B orders using isolated requests. Normalize the
   returned side to answer identity and report order conflicts separately.
   Identity, visible outputs, malformed attempts and costs must be retained;
   hidden reasoning must not be requested or saved.
4. Freeze the revised judge prompt, model/configuration and reporting rules before
   collecting or inspecting holdout labels. Holdout examples and labels must not
   appear in the judge's tuning examples. Once used to change the judge, that
   holdout is development data and needs replacement for a new validation claim.
5. Report agreement counts, confusion across preference labels, uncertain/invalid
   coverage, swap consistency and concrete disagreements. Separate obvious
   content checks from subtle prose comparisons. Defect-specific false-positive
   or miss rates require corresponding human-confirmed defect labels; preferences
   alone and author probe names do not supply those denominators.

Twelve held-out pairs across four families are diagnostic, not certification.
Do not treat related variants as independent observations or manufacture precise
weights from them. There is no automatic promotion threshold in this stage.
After meaningful judge alignment, a separately specified baseline/candidate
prompt trial can measure natural win/tie/loss outcomes, content regressions and
target failures. Human review and representative full-context cases remain
necessary; length-adjusted analysis is auxiliary to information preservation.

## Offline reproduction

[packet.py](packet.py) renders a deterministic packet and blank form to stdout,
validates a supplied form without writing it, and exposes swap/evidence helpers.
It has no model transport, network calls or package-installation step.

```bash
pdm run python evaluations/communication-style/preference-calibration/packet.py render calibration
pdm run python evaluations/communication-style/preference-calibration/packet.py validate calibration evaluations/communication-style/preference-calibration/labels.template.json
pdm run pytest tests/test_preference_calibration.py -q
```

The committed packet and blank form are reproduced exactly in the tests. Raw
source families and excerpts, no provenance in the comparison payload, A/B swap
symmetry, paragraph identity, pending labels, stale hashes, missing/duplicate rows
and read-only validation are checked offline. These checks establish artifact
integrity, not human agreement or behavioral improvement.

## Method sources

- [CheckList](https://aclanthology.org/2020.acl-main.442/): behavioral tests,
  directional changes and invariance probes.
- [WildBench](https://arxiv.org/abs/2406.04770): realistic task context and
  task-specific evaluation requirements. This packet is still an authored pilot.
- [AlpacaEval](https://github.com/tatsu-lab/alpaca_eval): anonymous pairwise
  comparison; no public benchmark questions or labels were imported.
- [Position-bias study](https://arxiv.org/abs/2406.07791): test answer-order
  consistency rather than assuming one randomized order removes bias.
- [Evaluation best practices](https://platform.openai.com/docs/guides/evaluation-best-practices):
  calibrate model judgments against human annotations before scaling.
- [Length-Controlled AlpacaEval](https://arxiv.org/abs/2404.04475): inspect verbosity
  bias; do not equate fewer words with better information delivery.

These are methodological references. Their published agreement or ranking
correlations are not measurements of this Chinese preference-calibration set.
