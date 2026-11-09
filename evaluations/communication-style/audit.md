# Communication-style audit

## Coverage and independence

The blinded `gpt-6-sol` judge scored all 36 development answers. Mechanical
checks verify complete answer/criterion coverage and literal evidence quotes.
The implementing assistant additionally read 30 complete answers:

- Both repetitions, every arm: `d2`, `d4`, `d5`, `d6` (24 answers).
- First repetition, every arm: `d1`, `d3` (six answers).

This second audit knew arm identities. It is neither a second blinded evaluator
nor independent human review. The remaining six answers received model judging
and mechanical validation only. No raw score was changed by this audit.

## Findings

### Required content

All six `d2` responses describe matching state and processing position but omit
the distinction between replaying internal computation and guaranteeing effects
in an external system. The frozen rubric combines these in requirement index 2,
so every arm loses two of 42 criterion observations.

This is a shared secondary omission, not a relative loss caused by a candidate.
The task asks for recovery, migration, and deletion; an external-side-effect
boundary is less explicit in the task than in the rubric. This may make that
criterion too demanding. It remains unchanged in the recorded results.

### Checkpoint generalization

`results/development/d2-direct-1.json` opens with:

> checkpoint 只记录处理进度，并不保存重建结果所需的全部信息。

This unqualified definition is inaccurate: checkpoints can contain operator
state paired with input positions. The
[Flink reference](../../docs/sources.md#technical-checks-for-the-communication-cases)
provides a concrete counterexample. The answer later explains a correct paired
state/progress snapshot, which reduces the practical extent of the error but
does not explicitly correct the opening statement. The raw critical finding is
retained. One occurrence cannot establish that the short rule caused it.

### Style and useful distinctions

The inspected answers preserve relevant distinctions: fixed resources versus
instance count, notification versus lock ownership, and TLB versus main-memory
page tables. Their summaries generally connect the requested explanation rather
than introduce unrelated alternatives. No additional clear target-style finding
was added in this audit.

Some short configuration answers supply three repair options, and some learning
answers include brief navigation or recap sentences. The rubric allows useful
comparisons and informative recaps. A reader may still prefer a shorter answer;
this study does not convert that preference into a quality finding after seeing
which arm produced it.

The TLB question supplies an incomplete prior explanation, so the answer must
separate a correction from certainty about the original intent. Some responses
begin by adopting an interpretation, then acknowledge that the fields alone do
not identify the original structure. This is a residual context-quality concern,
not evidence of a consistent arm-level difference under the frozen rubric.

## Post-hoc judge sanity check

After seeing zero natural style findings, the assistant authored
[seven controls](positive-controls.json): one clean factual progress update and
six versions with one deliberately conspicuous target behavior each. Only the
task, rubric, and anonymous answers were sent to the same judge; expected labels
and the purpose of the check were withheld.

The [recorded judgment](results/positive-control-judgment.json) identified all six
intended primary categories and left the clean answer unflagged. All controls
preserved the requested facts according to the judge. This checks for a grossly
nonresponsive evaluator. It does not estimate sensitivity, specificity, subtle
style preferences, long-answer discrimination, or effectiveness of the prompts.

## Privacy and evidence boundaries

The public cases contain generic technical scenarios and synthetic identifiers.
No private source documents, personal learning history, source paths, or verbatim
conversation extracts are included. The fixed teaching histories are authored
summaries rather than a claim to reproduce original messages.

Visible model answers, usage metadata, and explicit judge explanations are
retained. Hidden thinking is discarded by the runner. No tool-capable workflow,
live instruction installation, or second model family was evaluated. The
retained baseline is a conservative no-adoption decision, not proof that it is
optimal or that the user's real complaints have been resolved.
