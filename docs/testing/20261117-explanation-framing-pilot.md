# Explanation framing pilot — 2026-11-17

## Decision and scope

Initially adopt the tested explicit no-objections candidate in
[plainspoken](../../skills/plainspoken/SKILL.md) and
[dissect](../../skills/dissect/SKILL.md), at the user's direction. This replaces
instructions to develop the assistant's own objections with reconstruction of
claims, reasons, and inferential connections. The candidate prohibits added
rebuttals, corrective distinctions, acceptance warnings, and demands for proof.
It retains source attribution, the source's own disagreements, and accurate
reporting of failures and permission or capability limits.

The [actor reference](../../skills/dissect/references/actors-and-interactions.md)
also stops requesting profile counterexamples. It was not loaded in this pilot;
its behavioral effect is unmeasured. Descriptions, routing, other references,
installer behavior, and published releases are unchanged. Adoption is a user
preference decision, not a claim of uniformly better answers. Tasks explicitly
requiring criticism or assessment have not been tested with this prohibition.

## Task and method

The task was a Chinese reading-course continuation about concrete universality
in Žižek's *The Parallax View*, using the existing user's `go-on` request.
Each fresh generation received a bounded reconstruction of course background,
the preceding assistant answer, and the same supplied book excerpt. The original
answer that prompted the experiment was excluded. This was not a replay of the
full original conversation.

Pi 1.5.2 supplied both skill bodies explicitly as system additions to
`You are a helpful assistant.` Tools, extensions, MCP, skill discovery, context
files, prompt templates, and persistent sessions were disabled. This tests
instruction content, not native skill selection, tool use, or cross-client
installation. No model judge was used; observations below are the implementing
assistant's unblinded reading, not independent ratings or human preference votes.

There were **15 successful generations**, one per populated table cell below,
with no generation retries. Every final event reported normal completion.

| Model and provider | Original | Constructive objections | Explicit prohibition | Prohibition + reduced evaluative context |
| --- | --- | --- | --- | --- |
| `openai-codex/gpt-6-astra` | Tested | Tested | Tested | Not tested |
| `openrouter/qwen/qwen4-max` | Tested | Tested | Tested | Tested |
| `xai/grok-4.7` (subscription OAuth) | Tested | Tested | Tested | Tested |
| `openrouter/deepseek/deepseek-v4-pro-0813` | Tested | Tested | Tested | Tested |

All commands requested `medium`. Qwen and DeepSeek final records reported
`high`; GPT and Grok used `medium`. The requested setting must not be interpreted
as an equal reasoning budget across providers.

The first revision asked objections to identify their target, grounds, and
consequences. The adopted candidate instead explicitly forbids model-added
objections and corrections. Both keep argument structure as a reasoning and
prose-organizing method, not required claim/evidence/counterevidence headings.

The final context intervention removed or rephrased 18 lines of evaluative
course guidance and preceding-answer commentary. Book text, final user message,
and prohibition skill snapshots stayed identical. Source-provenance limits,
prior learner questions, and author-internal disputes remained. This was removal
of selected evaluative framing, not all context or every possible qualification
cue. The same edited context was used for DeepSeek, Qwen, and Grok. It is only a
private test input; the original course and conversation were not changed.

## Observed results

| Model | Original and constructive-objection versions | Prohibition, original context | Prohibition, reduced evaluative context |
| --- | --- | --- | --- |
| GPT | Both added a distinction between radical negation and the necessity of historical Terror; the revision expanded reconstruction without removing the corrective turn. | Targeted proof-gap and acceptance warnings did not appear in this sample. | Not tested. |
| Qwen | Both evaluated proof gaps; the revision added more objections, including a reading/history analogy criticism and potential historical counterexamples. | Stronger objections receded, but proof-gap qualifications remained. | Still marked historical claims as unproven and listed unsupported connections; explicitly appealed to retained course source boundaries. |
| Grok | Both added assessment; the original also added a present-day-action disclaimer. | Repeated proof-gap corrections remained. | Targeted model-added corrections did not appear; source-internal disputes and the excerpt's truncation remained. |
| DeepSeek | Original added cautions and insufficient-proof reminders. The constructive version concentrated more on exposition, though preemptive distinctions remained. | Added acceptance warnings, historical-verification reminders, and an end-of-answer assessment requirement. | Targeted model-added cautions and proof-gap assessment did not appear. |

Thus a stronger prohibition was not consistently associated with fewer
corrections. Removing evaluative context coincided with the target behavior's
disappearance in the Grok and DeepSeek samples, but not Qwen's. These observations
support investigating context/model interaction rather than attributing the
behavior solely to immutable training tendencies or a safety policy.

They do **not** establish causation or overall quality. Each condition has one
sample; revisions change multiple clauses, context edits shorten the prompt,
and later comparisons reuse earlier outputs rather than concurrent repeated
baselines. Criticism present in the source is not counted as assistant-added
criticism. A source-truncation notice is not a failure of the target behavior.
Some less-critical outputs state strong historical claims directly or anticipate
missing text. Attribution, factual fidelity, useful depth, and suitability for
other tasks require separate assessment. No win rate, model ranking, latency,
cost saving, or security-scanner improvement follows from this pilot.

## Evidence and reproducibility

The baseline is the skill content at `bdee79aadc523c49115a53f39674ab70e81f76b7`
(the v2.0.0 release). Raw prompts, outputs, events, stderr, protocols, context
diffs, and per-run hash checks remain local and private. They include personal
conversation context and book material and are not part of the public report.
Public readers therefore cannot independently reproduce the exact private task
from this summary alone. No reserved holdout material was opened for this study.

The local evidence directory is `/tmp/skills-zizek-ab.XdI3LG/`; it is mode 700
and temporary, not a durable public archive. Earlier candidates and all generated
answers remain unchanged there. The initially adopted skill files matched the
tested snapshots byte-for-byte; the later condensation below was not generated
in this pilot. SHA-256 identities of the tested snapshots:

| Snapshot | SHA-256 |
| --- | --- |
| Original plainspoken | `5b1f162a9b69c8a25fe89fb2abe5a27834be48005b3cbc5cb63b2071f979b5af` |
| Original dissect | `a9023026941c2f635da7a28bcae1660fdf34652a03c300323115204736279d8a` |
| Constructive plainspoken | `0a5dc94cd5420a3d1d74fad77bcb0ef615298223345b6d9b5604c05b186f690a` |
| Constructive dissect | `7b64a52a2494916f134cc78cb6d955c324484e16e4e3b8d063318fcc4e7c7fae` |
| Adopted plainspoken | `86c7269dbfb31bfa447743b8b73696090e98d8242398413c095f09983fc1af74` |
| Adopted dissect | `aa16c865337f60d93ffdd10bc0a70fa3197d5c5c5b796209e7735cb9b7fad684` |
| Original bounded context | `cfe951b4ceffb5bc9e7eb6dfbb86e90c9482ed893c6fce2bf950ea2f81bf95a1` |
| Reduced-evaluation context | `5b3fc93c9f434fe37972311858f4636eef8b901ad6c26bcef7ea20c82c91c059` |

## Subsequent condensation

At the user's request, shorten the two prohibition paragraphs while retaining
argument reconstruction, no added corrective commentary or adequacy/acceptability
judgments, source-internal disagreements, and accurate attribution without
invented support. The current skill files contain this shorter wording.
At adoption, no new model generations had been run for it. The initial 15 outputs
above belong to the longer frozen candidates, not this condensation. The fresh
comparison below evaluates the shorter wording separately.

For the shorter wording, 92 related static tests, skill validation, Ruff checks,
Markdown/link checks, and whitespace checks passed. These are packaging and
contract checks, not renewed evidence of model behavior.

## Fresh long-versus-concise comparison

A subsequent authorized run generated eight fresh answers: long and concise
prohibitions once each on the same four models, using only the unchanged
reduced-evaluation context. Both arms were generated anew; historical answers
were not used as the comparison baseline. GPT and Grok ran long first; Qwen
and DeepSeek ran concise first. All eight stopped normally, without retries.
Recorded thinking was medium for GPT/Grok and high for Qwen/DeepSeek in both
arms. Input hashes were checked before and after execution, and both skill
markers were verified in each emitted system addendum.

The implementing assistant's unblinded observations were:

| Model | Longer prohibition | Concise prohibition |
| --- | --- | --- |
| GPT | No clear added proof-gap or acceptance warning. | Similar on that target; explanation remains connected. |
| Qwen | Historical/provenance qualifications and a general demand for separate arguments. | More direct claims of missing independent support and an unproved historical-necessity transition. |
| Grok | Warnings about interpreting traditions and accepting historical claims. | Still qualifies the explanation, including an unsolicited modern-action disclaimer. |
| DeepSeek | Adds disclaimers against reading the discussion as praise or religious advocacy. | Those disclaimers disappear; the answer mainly reconstructs the argument. |

Both GPT answers postpone Paul and Laclau although those sections are supplied;
the other models reach them. All use topic headings rather than a mandatory
claim/evidence/counterargument template. Forward chapter references and some
interpretive additions remain unverified. No overall factual-accuracy pass is
claimed. Acknowledging the excerpt's truncated ending and explaining the
source's own disagreements do not by themselves count as added objections.

Results are mixed, not evidence that the concise version is equivalent or
uniformly worse. Qwen's concise answer gives a concrete reason not to assume
that the shorter adequacy wording reliably preserves the explicit prohibition
on proof demands. Fresh longer answers also reintroduce behavior absent from
some earlier context-ablation samples. One sample per cell cannot separate
wording effects from generation variability. Shorter instructions did not
consistently produce shorter answers, and no cost or quality gain is claimed.

The current skill wording is unchanged by this evaluation. This follow-up adds
eight generations to the original 15, for 23 total. It tests one task with the
reduced-evaluation context only, not native activation or general reliability.
A [separate repeated cross-task pilot](20261117-explanation-transfer-pilot.md)
subsequently tests three other session tasks and records completion failures
separately from style judgments.

Concise snapshot SHA-256:

- plainspoken: `4d57328457f51596822748e150fe4b1ccd1c56f0fcc3d580ad0aa601c274be9b`
- dissect: `c43a51d499f70f285a805426af91b373adf123544ccee18901ff1ca1646d8ba1`

Private evidence in the same temporary directory includes
`concise-comparison-protocol.json`, `concise-comparison-sha256.txt`,
`concise-comparison-verification.json`, `CONCISE-COMPARISON-RESULTS.md`, and
eight sets of events, stderr logs, and extracted answers. A failed oversized
final-event parsing attempt is recorded; complete answers were extracted from
text-end events and no model generation was repeated.

## Engineering validation

Before the subsequent condensation, the locked environment was synchronized
without dependency upgrades. `pdm lock --check` and `pdm run check` passed:
592 tests, no skips, 100% line
coverage of the 325 maintained Python-tool statements, six validated skills,
and Python, Markdown/link, and shell checks. Active LSP diagnostics on the
changed Python test were clean. The earlier targeted suite passed 92 tests.
An earlier run exposed obsolete assertions for the replaced scrutiny wording;
those were updated to the authorized contract and a prohibition/accurate-reporting
test was added. No tests were skipped or coverage thresholds weakened.
Static checks do not establish response quality or instruction compliance.

The user selected the concise version for v2.1.0 after the follow-up comparisons.
Publication does not update global installations or alter v2.0.0 and its evidence.
