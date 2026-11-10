# Preference judge v4: incomplete calibration

Status: **not selected; no computable primary pair agreement**. The frozen batch
ran all 24 calls once. Five outputs passed validation and 19 failed. Each of the
seven labeled style pairs lacks at least one valid order. No output was repaired,
retried, discarded or partially admitted into preference statistics. Holdout and
runtime prompts remain unchanged.

Freeze: `eeb87d3`. Inputs and execution rules are in [manifest-v4.json](manifest-v4.json)
and [protocol-v4.json](protocol-v4.json). All attempts are in
[results-v4/](results-v4/); [summary-v4.json](summary-v4.json) is reproducible with:

```bash
pdm run python evaluations/communication-style/preference-calibration/judge_v4.py summarize
```

## Execution and comparison

| Measure | v3 | v4 |
| --- | ---: | ---: |
| Calls attempted | 24 | 24 |
| Structurally valid | 24 | 5 |
| Invalid | 0 | 19 |
| Labeled style pairs | 7 | 7 |
| Stable matches | 4 | unavailable |
| Stable mismatches | 1 | unavailable |
| Order conflicts | 2 | unavailable |
| Unavailable primary pairs | 0 | 7 |
| Estimated USD | 0.27382 | 0.515898 |
| Usage tokens | 46,566 | 81,353 |

The zero agreement counters in the machine summary are accompanied by seven
unavailable pairs. They are **not a measured 0% preference agreement**. Costs are
usage estimates, not invoices. This is repeated development data, not a fresh
independent sample. D04 remains in its predeclared denominator despite the known
content confound; mixed and unlabeled pairs remain separate.

The five valid outputs are D02-original, D03-swapped, D04-swapped, D08-swapped and
I01-swapped. No pair has two valid orders, including the identity control.

## Output-contract failure

- Eighteen records fail `Empty judgment text`. In their visible JSON, an absent
  self-defense finding uses empty `target`, `increment` or `deletion` strings.
  The reused v3 validator requires those strings to be nonempty even when absent.
- D03-original fails `Unknown check status`: its per-dimension `self_defense`
  check uses `present`, which belongs to the separate self-defense field. The
  per-dimension vocabulary is `issue/clear/uncertain/not_applicable`.
- These are valid JSON responses, not transport failures. Source records retain
  the entire visible response and usage; validation failure does not erase them.

The implementing assistant introduced a contract gap: the new prompt listed the
fields and status vocabularies but did not explicitly preserve v3's nonempty
requirement for inapplicable explanation fields. The preflight tests used authored
valid fixtures and rejection cases; they did not exercise whether the new prompt
would actually satisfy that contract. A full paid batch was launched before this
mismatch was found. More detailed output increased both cost and the opportunity
for structural failure, without establishing better judgment.

The frozen prompt, validator and records are preserved. Relaxing validation now,
filling blanks with “不适用”, or extracting just the winner would change the
predeclared analysis. Any future contract should express absent/inapplicable
states consistently, minimize duplicated fields and receive a separately frozen,
small output-conformance check before a larger batch. That is a future design
requirement, not a repair or retry of this batch.

## Unblinded author audit of all visible outputs

All 24 visible judgments were reviewed, including the raw JSON inside invalid
records. The following is the implementing assistant's diagnostic reading against
the preserved human comments. Invalid records supply failure diagnosis only;
they contribute no recovered preference scores or defect-detection rates.

| Pair | Diagnostic finding across the two orders |
| --- | --- |
| D01 | Both catch A's unjustified certainty. Both still accept B's possibilities as sufficiently grounded, rather than identifying the missing reasons the user wanted. |
| D02 | Both criticize the extra closing correction. Neither identifies the shared unsolicited “97%” correction as the user did. One instead introduces a shared terminology complaint about “检验假设”; the other calls the same wording clear. |
| D03 | Both notice the shared punishment disclaimer, and both distinguish the requested example from its absence in the other answer. They still praise the example's explanatory value, where the user found it unhelpful. The comparison remains mixed. |
| D04 | Both call both messages natural, including the phrase the user found artificial. The swapped record again emphasizes the explicit overtime explanation. Naturalness alignment is unestablished, and the content confound remains. |
| D05 | Both catch the explicit defensive paragraph. Both still call the shared “个人行动仍会改变结果” contribution useful, missing the user's objection to that supplement. |
| D06 | Both identify the added “谁更委屈” framing as removable. Both miss the shared introduction and metaphor and call the prose direct. They disagree about whether the extra framing is self-defense or only repetition. |
| D07 | Both mark both answers clear and natural. Neither captures the user's objection to the “有人、有人” construction or the remaining difficulty in A. |
| D08 | Both praise directly addressing the two probability claims. Neither identifies the user's objection to turning a chain of inference into parallel negations. They also accept B's indirect answer as sufficiently responsive, while the user requested a clear initial answer. No human preference exists for this pair. |
| D10 | Both identify the unprompted mutual-exclusivity denial as removable. This repeats an already observed v3 strength; it is not new independent evidence. |
| D11 | Both still reward explicitly denying exclusivity, despite recognizing that the positive account already shows the connection. This remains contrary to the user's feedback. |
| D12 | Both now state that the earlier unverified-mechanism boundary continues to apply to B. One still praises repeating that boundary in A and says deletion risks overstatement; the other calls the repetition removable. The protective function remains uncertain/absent rather than clearly aligned with the user's diagnosis. One also adds a shared missing-link complaint that the other does not make. |
| I01 | Both raw responses say tie. One treats the time as a possible proposal, while the other marks grounding uncertain. Only the swapped response is structurally valid, so the identity pair is unavailable under the protocol. |

Explicit per-answer checklists made the judgments easier to inspect. They did
not make the model reliably notice shared defects or contextual redundancy.
There is no supported claim that v4 improves preference agreement, nor that a
specific defect's sensitivity or specificity has improved.

## Tooling and disposition

The [Promptfoo replay probe](evaluation-tools.md) displayed the saved v3/v4
outputs side by side, including all 19 v4 errors. It made no model calls. Its
artifact-validity pass rate is not a user-preference score.

This closes the predeclared v4 batch. No automatic v5, holdout run, new human
labels or runtime adoption follows. Further optimization should use the user's
judgments as the primary decision source while tools organize comparisons and
retain diagnostics. The automated judge is not ready to replace that judgment.

## Verification

- 75 related offline tests passed; the full repository gate passed with **642
  passed and 20 existing environmental skips**.
- Ruff, format checks and explicit Pyright checks cover both new evaluation
  modules; repository checks cover their tests. Markdown and links passed for
  179 files. The test suite preserves the 19 invalid records as invalid.
- Lock check, isolated `CODEX_HOME` installer preview and worktree/index/branch
  whitespace checks passed. Runtime instructions, installer and dependencies were
  not changed. The optional Promptfoo probe lives under ignored `.venv/`.
- Active LSP probes remained inconclusive; the independent Pyright run passed.
  The reported 100% coverage scope is `scripts/`, not all evaluation modules.
- No browser-rendering test, live framework transport migration, independent
  human defect labeling or holdout evaluation was completed.
