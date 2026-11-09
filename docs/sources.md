# External design sources

This register records external ideas used in this repository's design and
experiments. It is provenance, not an instruction to load these sources during
ordinary tasks. Existing archive manifests remain authoritative for vendored
historical material; this register does not replace licenses or source records.

## Communication style

Reviewed on 2026-11-09 for the
[communication-style comparison](../evaluations/communication-style/README.md).
The original candidate prompts and cases are independently authored. A separate
[user-requested follow-up](../evaluations/communication-style/talk-normal/README.md)
vendors the full pinned talk-normal prompt for direct comparison, with its MIT
notice retained. Neither study installs an upstream skill or global instruction.

### S01: talk-normal

- Source: [hexiecs/talk-normal](https://github.com/hexiecs/talk-normal/tree/d89cf329e775e640181427fae071652198264c7e).
- License: [MIT](https://github.com/hexiecs/talk-normal/blob/d89cf329e775e640181427fae071652198264c7e/LICENSE).
- Relevant artifacts: [prompt](https://github.com/hexiecs/talk-normal/blob/d89cf329e775e640181427fae071652198264c7e/prompt.md),
  [contrast regression](https://github.com/hexiecs/talk-normal/blob/d89cf329e775e640181427fae071652198264c7e/regressions/rule-17-negation-frame.md),
  and [response comparisons](https://github.com/hexiecs/talk-normal/blob/d89cf329e775e640181427fae071652198264c7e/TEST_RESULTS.md).
- Borrowed idea: describe an unwanted rhetorical operation, provide a concrete
  rewrite direction, and compare observed failures across frozen prompt variants.
- Not adopted: blanket prohibitions on negative comparisons, fixed sentence
  limits, or character reduction as proof that useful information is preserved.
- Evidence boundary: the contrast regression uses one task and model. Examples,
  scope, and rule placement changed together. Its clean repetitions do not
  isolate a causal mechanism or establish cross-task generalization.
- Local use: the `direct` and `example` arms differ only by an independently
  written, task-bounded example; necessary corrections remain permitted.
- Direct upstream test: the follow-up uses the complete, unchanged `prompt.md`
  as its system prompt, with a contemporaneous baseline and all 12 local cases.
  Its [license copy](../evaluations/communication-style/talk-normal/upstream-LICENSE.txt)
  and source identities accompany the fixture; integration installers are not run.

### S02: STFU.md

- Source: [GoZippy/STFU.md](https://github.com/GoZippy/STFU.md/tree/c27b992912ad43a17f8322849c2d9a95a7c347d1).
- License: [MIT](https://github.com/GoZippy/STFU.md/blob/c27b992912ad43a17f8322849c2d9a95a7c347d1/LICENSE).
- Relevant artifacts: [prompt](https://github.com/GoZippy/STFU.md/blob/c27b992912ad43a17f8322849c2d9a95a7c347d1/STFU.md)
  and [benchmarks](https://github.com/GoZippy/STFU.md/blob/c27b992912ad43a17f8322849c2d9a95a7c347d1/data/benchmarks.md).
- Borrowed idea: measure task behavior alongside prose volume and make failed
  evaluations and prompt-version differences visible.
- Not adopted: hard word caps, telegraphic fragments, or a default preference
  for terse output over complete explanations.
- Evidence boundary: benchmark versions, metrics, and harness coverage differ;
  missing cells and model-judge limitations prevent a universal compression claim.

### S03: Laconic_tests

- Source: [highsierralabs/Laconic_tests](https://github.com/highsierralabs/Laconic_tests/tree/512f108d6e6bcc2cc6d8f93a3f70b0be187d6aff).
- Relevant artifacts: [methodology](https://github.com/highsierralabs/Laconic_tests/blob/512f108d6e6bcc2cc6d8f93a3f70b0be187d6aff/docs/methodology.md)
  and [scoring](https://github.com/highsierralabs/Laconic_tests/blob/512f108d6e6bcc2cc6d8f93a3f70b0be187d6aff/docs/scoring.md).
- Borrowed idea: define required content before generation, check conclusions and
  omissions separately, repeat in fresh contexts, and audit instruction leakage.
- Not adopted: its domain-specific directive, tasks, transcripts, or scoring keys.
- Evidence boundary: small safety-oriented corpus with model-assisted scoring;
  the public notes contain historical and revised scoring descriptions. It
  motivates omission checks, not a transferable quality ranking.
- Licensing boundary: the pinned [LICENSE](https://github.com/highsierralabs/Laconic_tests/blob/512f108d6e6bcc2cc6d8f93a3f70b0be187d6aff/LICENSE)
  is CC BY 4.0; its README distinguishes documentation/data from MIT-licensed
  code. This study references methodology without copying those materials.

### S04: Anthropic prompting guidance

- Source: [prompting best practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices),
  accessed 2026-11-09, especially response-format control.
- Borrowed idea: specify the desired output behavior and keep the instruction's
  own style consistent with that goal.
- Evidence boundary: mutable vendor guidance, not an independent comparison of
  our wording or proof of effectiveness on another model family.

### S05: Anatoly concision experiment

- Source: [Concision discipline](https://anatoly.cloud/research/concision-discipline-prompt-strategy),
  accessed 2026-11-09; author: Remi Viau.
- Borrowed idea: measure correctness and output separately when removing
  preambles and uninformative wording from technical responses.
- Evidence boundary: the catalog-scored comparison reports one run per condition
  on one fixture. Its reported token and F1 improvements do not establish the
  isolated contribution of any instruction or predict our result.

## Technical checks for the communication cases

These references cross-check selected technical contracts in the frozen rubric;
they are not gold answers or evidence that every generated answer is correct.
Retrieved 2026-11-09; living documentation may change.

- `d2`: [Flink fault tolerance](https://nightlies.apache.org/flink/flink-docs-stable/docs/learn-flink/fault_tolerance/)
  defines a snapshot as source positions plus operator state, and a checkpoint
  as an automatically taken recovery snapshot. It supplies a concrete
  counterexample to treating every checkpoint as only a progress marker.
- `d3`: [Python condition objects](https://docs.python.org/3/library/threading.html#condition-objects)
  documents lock reacquisition, predicate rechecking, and notification without
  releasing the lock. Fetching OSTEP's condition-variable PDF failed locally;
  this independently available API documentation supplies the cross-check.
- `h2`: [ShareDB Doc](https://share.github.io/sharedb/api/doc) documents versions,
  operations, acknowledgments, and snapshots;
  [Y.Doc](https://docs.yjs.dev/api/y.doc) documents client identity and configurable
  garbage collection. These are concrete implementations, not universal storage
  or reclamation rules for OT and CRDT.
- `h4`: [RabbitMQ publish/subscribe](https://www.rabbitmq.com/tutorials/tutorial-three-python)
  describes a fanout exchange broadcasting to its bound queues, illustrating
  both concepts with an explicit receiver scope.
- `h6`: [AWS timeouts and retries](https://aws.amazon.com/builders-library/timeouts-retries-and-backoff-with-jitter/)
  explains that a timeout does not establish the absence of side effects and
  that retries need an appropriate idempotency contract.

## Attribution policy

Record ideas and their limits here; keep experimental observations with their
own protocol and results. If future work copies or adapts substantive upstream
text, examples, code, or data, check the pinned license and retain the required
notices. Rephrasing copied material is not a substitute for attribution.
