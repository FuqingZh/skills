# Implementing-assistant audit

This review was unblinded and performed after scoring. It does not replace the
blinded model ratings, provide independent human preference evidence, or modify
any score. The [raw summary](summary.json) remains mechanically reproducible.

## Coverage

Read in full: both repetitions of both arms for `d2`, `d5`, `h2`, `h5`, and `h6`
(**20 of 48 answers**). This covers every answer with an omission or mixed clarity
rating, plus the specified correction, analogy, and uncertain-outcome boundaries.
The remaining 28 answers received model and mechanical review only. All 12
judgment records were inspected for omissions, style, critical, and clarity flags.

## Observations

- **d2 — derived-state recovery:** all four explain facts plus rules, paired
  state/progress, migration, deletion, and recovery after deletion. The missing
  external-effects distinction is real relative to the rubric; its relevance is
  weakly established by this particular user turn. This repeats the prior study's
  [rubric concern](../audit.md) and affects both arms equally. No rescoring or
  post-result criterion change was made.
- **d5 — TLB correction:** `d5-baseline-2` states “前面那张表应称为 TLB 表项示意表”
  and later acknowledges that its fields cannot establish the implementation.
  The mixed-clarity finding is meaningful; whether to classify that inconsistency
  as clarity or correctness remains a judgment. Both upstream answers preserve
  uncertainty, for example “具体归属仍需结合上下文确认” and “待确认”. Both also
  correct the earlier statement and distinguish CPU-internal TLB from RAM page
  tables. Zero critical findings should not be read as certified correctness.
- **h2 — OT/CRDT correction:** all four explain both families' context costs,
  concurrent insertion/deletion, and history-reclamation conditions. Upstream
  retains the correction rather than simply deleting the disputed claim. Its
  examples work under the explicitly chosen insertion-preserving semantics;
  anchor-based CRDT sketches are identified as examples, not universal layouts.
- **h5 — requested analogy:** all four use nearby spices versus a cupboard and
  explain that real caching usually copies data while the source remains.
  Upstream repetition 2 omits the optional stale-copy discussion present in the
  baseline, while satisfying the requested analogy and boundary. This illustrates
  why equal rubric coverage is narrower than equal explanatory detail.
- **h6 — uncertain write outcome:** all four keep the outcome unknown, check the
  authoritative result and processing evidence, and discuss retries with a valid
  idempotency mechanism. Upstream retains useful negative statements such as
  “目前无法确定这两次请求都没有写入成功”; these are necessary uncertainty reporting,
  not invented rhetorical contrasts under the scoring rubric.

The audited long upstream answers have multiple sections and many sentences.
Their preserved coverage does not test strict compliance with the upstream
3–5-sentence rule. The experiment measures behavior elicited by the complete
prompt, not the safety of enforcing every instruction literally.

## Interpretation limits

No additional target-style or critical issue was identified in this limited
read-through. This does not estimate the judge's false-negative rate. The six
post-hoc positive controls from the original experiment showed responsiveness to
obvious defects only; they were not repeated or treated as new comparative data.
No user preference ranking, second model family, learning-outcome measurement,
or unfamiliar-task test was conducted. The shorter answers are useful comparison
material, with no automatic installation or template substitution.
