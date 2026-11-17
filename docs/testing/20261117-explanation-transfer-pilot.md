# Explanation framing: repeated cross-task pilot

## Question and result

Does shortening the explicit no-objections guidance reproduce the earlier
behavioral changes on other tasks, or improve explanations?

**This pilot does not establish a stable improvement or a general regression.**
Technical explanations mostly retain their core content under both versions.
One concise Qwen statistics answer adds stronger corrective commentary, but
that form does not recur in its other repetition. Historical-task failures
limit comparison for Qwen and Grok. Keep the current skill files unchanged;
retaining shorter wording is not a claim that it improves answer quality.

This follows the [single-task framing pilot](20261117-explanation-framing-pilot.md).

## Design

Three questions were selected from three other existing sessions before
sampling:

- **P — statistics:** explain the meaning and mathematical basis of a p-value.
- **D — databases:** distinguish serializability from actual serial execution.
- **H — history:** explain LBJ's bipartisan legislative mechanisms.

P and H use the exact original standalone user questions. D includes the exact
preceding assistant answer and current question. These are bounded extracts,
not full-session replays; no sentences within selected messages were edited.
No historical target answers or later turns were supplied. An initially
considered historical continuation was replaced by its original standalone
question before generation because its preceding event exceeded the reader's
limit. The final selection tests technical and historical explanation, not
another author's text with an attached primary-source excerpt.

Each task used four models, two skill versions, and two repetitions: 48
attempts. Models were `openai-codex/gpt-6-astra`, `openrouter/qwen/qwen4-max`,
`xai/grok-4.7`, and `openrouter/deepseek/deepseek-v4-pro-0813`.
Both arms were generated afresh. Arm order reversed across repetitions;
two models began with each arm. Task order was P, D, H.

Pi 1.5.2 used the earlier pilot's minimal system preamble and frozen snapshots,
with no tools, extensions, MCP, native discovery, or reference loading.
Requested thinking was medium; recorded settings were medium for GPT/Grok
and high for Qwen/DeepSeek. Input hashes were checked before and after runs;
both expected skill markers appeared in every emitted system addendum.
The shorter snapshots still match the repository files byte-for-byte.

## Completion failures are not style successes

Of 48 attempts, 46 produced normally terminated text, but only 41 contained
substantive answers:

- Grok's four H outputs stopped after promising to consult material.
- Qwen's H concise repetition 1 emitted a tool-call-shaped text string rather
  than answering. No tool ran.
- Qwen's H long repetition 1 ended with the upstream error
  `Output data may contain inappropriate content.`
- Qwen's H concise repetition 2 was interrupted by the two-call shell's
  280-second budget. The preceding long call consumed about 223 seconds.
  This is a harness-budget failure, not evidence that the concise wording
  caused a model failure.

No generation was retried. Original events and partial outputs remain intact.
The tool-free setup does not adequately exercise the reference-loading behavior
that these historical answers attempted. Both versions share that limitation.
The 40 substantive answers with complete long/concise pairs are the matched
comparison set; the remaining substantive Qwen H answer is unpaired.

## Structured judgments

With operator opt-in, TypeSafe `jev-1.14.0` assessed 46 completed texts in six
batches, using random answer IDs without model or version labels. It saw the
final user question and answer, not D's preceding assistant message. Each
answer received two independent judgments:

1. Probability of unnecessary objections, proof demands, acceptance warnings,
   or corrective detours. Requested distinctions, necessary conditions,
   attribution, and relevant factual clarification do not count automatically.
2. Explanatory coverage: **0** no substantive explanation; **1** a key mechanism
   or connection missing; **2** core mechanism explained with an example or
   causal reasoning. This is not a factual-accuracy score.

The following are the evaluator's probabilities of the first behavior, in
repetition 1 / repetition 2 order. They are predictions, not verified rates.
The preregistered thresholds were at least 0.8 for strong predicted presence,
at most 0.2 for predicted absence, and uncertain between them.

| Task | Model | Long | Concise |
| --- | --- | --- | --- |
| P | GPT | 0.08 / 0.12 | 0.12 / 0.11 |
| P | Qwen | 0.21 / 0.22 | 0.18 / 0.39 |
| P | Grok | 0.11 / 0.09 | 0.11 / 0.17 |
| P | DeepSeek | 0.11 / 0.08 | 0.09 / 0.16 |
| D | GPT | 0.06 / 0.06 | 0.06 / 0.08 |
| D | Qwen | 0.10 / 0.18 | 0.13 / 0.17 |
| D | Grok | 0.09 / 0.06 | 0.07 / 0.06 |
| D | DeepSeek | 0.08 / 0.08 | 0.08 / 0.07 |
| H | GPT | 0.06 / 0.07 | 0.18 / 0.20 |
| H | DeepSeek | 0.05 / 0.07 | 0.19 / 0.24 |
| H | Qwen | error / 0.50 | nonanswer / timeout |
| H | Grok | nonanswer / nonanswer | nonanswer / nonanswer |

No substantive answer crossed 0.8; this is not proof that all were free of
unnecessary commentary. In the matched set, mean predicted probabilities were
0.099 long and 0.143 concise. Coverage means were 1.935 and 1.962, both near the
"core mechanism explained" level. These small, near-ceiling differences do not
establish optimization, equivalence, or statistical significance.

Coverage uncertainty matters: DeepSeek's second statistics answers scored
1.56 long and 1.65 concise, with only 0.56 and 0.65 probability respectively on
level 2. Its first long database answer scored 1.55, split between levels 1
(0.44) and 2 (0.56). The five nonanswers had 0.93–1.00 probability on level 0;
they are not included as successful low-objection answers.

## Text review and interpretation

The implementing assistant spot-checked uncertain judgments and paired
examples; this review was not blinded and was not a full correctness audit.

- D retains the requested distinction under both versions. A concise DeepSeek
  answer supplies a concrete concurrency example absent from its first long
  answer. That local elaboration is not a demonstrated general improvement.
- Qwen's second concise P answer explicitly frames the inference as having a
  structural weakness and adds a stronger evidence-strength assessment. The
  first concise repetition instead emphasizes construction and calibration.
  The evaluator's 0.39 judgment on the second answer remains uncertain; it
  must not be reported as a confirmed failure or stable recurrence.
- More content is not necessarily better: both concise Qwen D answers are
  longer than their long-version counterparts. Shorter instructions did not
  reliably shorten answers.
- Coverage scores can miss errors. One concise Qwen P answer verbally reverses
  the stochastic-order direction for discrete p-values while later writing
  the correct super-uniform inequality. High coverage is not correctness.
- GPT and DeepSeek provide substantive historical mechanisms in both versions.
  DeepSeek's second concise H answer adds a qualification about personal
  dependence and replicability; whether this is an unnecessary detour is
  uncertain (evaluator probability 0.24).

The earlier single-task warning does not reproduce as a clear cross-task,
repeatable degradation here. Nor is there evidence of a reliable improvement.
Two repetitions on three convenience-selected tasks cannot establish stable
model tendencies. Task selection, missing historical answers, the tool-free
harness, subjective judgment, and the absence of a full accuracy audit remain
important limits. No native skill-activation, cost, or productivity claim follows.

## Evidence and repository scope

Private evidence is retained under `/tmp/skills-zizek-ab.XdI3LG/transfer/`
(mode 700): source-message extracts, frozen contexts, protocol, runner,
48 event/stderr pairs, 46 extracted texts, completion records, masked judge
requests/results, the answer map, per-answer probabilities, summary, and
input/output SHA-256 manifests. It is local temporary evidence, not a durable
public archive. Preparation failures caused by output suppression and storage
limits are recorded; they did not cause generation retries.

No original conversation, course material, or skill wording was changed.
Private prompts and full answers are not copied into the repository.
Documentation validation is separate from the behavioral observations above.
