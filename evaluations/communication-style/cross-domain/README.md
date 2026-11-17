# Cross-domain communication-style comparison

The user requested a test of the new general-purpose paragraph after reviewing
unnecessary self-defense in the assistant's own replies. Inputs were frozen at
`00d793f` before model calls. No installed instructions or skill files change.

Status: complete; no demonstrated target-style improvement. See the
[results](./results.md), [raw summary](summary.json), and [full-answer audit](./audit.md).
Both arms received zero model style findings; revised output grew 14.7%.

A separately frozen [sentence-level ablation](../sentence-ablation/README.md)
tests the revised paragraph's seven sentences and their marginal contributions.

## Treatment and tasks

[baseline](prompts/baseline.txt) is byte-identical to the original paragraph.
[revised](prompts/revised.txt) is the exact last proposed paragraph: plain,
coherent explanation; substantive distinctions and uncertainty; no unsolicited
defense of the answer's wording, intentions, or approach. It imposes no sentence
limit and does not prohibit necessary negation.

[cases.json](cases.json) contains eight Chinese tasks, one long and one short
for each domain:

| Domain | Long task | Short task |
| --- | --- | --- |
| Philosophy | Responsibility under causal influences | User explicitly asks what an editorial suggestion implies |
| Science | Exercise/sleep observational study and causal design | Correct a p-value misconception |
| Sociology | Mechanisms of educational inequality | Rewrite three headings |
| Conversation | Cancelled meeting, feelings, repair and a message | Correct a prior self-defensive editing reply |

Seven cases are synthetic. The last reconstructs the observed failure without
private transcripts, source identifiers, or personal facts. These are development
cases, not an unseen validation set. Different domains do not establish coverage
of their whole subject areas.

Each case receives two independent responses per arm: **32 responses**, with
three interleaved workers. The baseline is regenerated contemporaneously.
Generator: `openai/gpt-6-astra`, high reasoning. Judge: `openai/gpt-6-sol`, high
reasoning. Temperature uses the provider default. Fresh Pi processes use the
same response-only isolation as the [parent study](../README.md): no inherited
conversation, context files, skills, extensions, MCP, tools, or session storage.
Each arm's paragraph is the sole system prompt. The engineering instruction
stack is deliberately absent. Fixed case histories are identical between arms.

## Clarified rubric and controls

[judge.txt](judge.txt) changes the prior rubric before generation:

- Self-defense includes unsolicited protection of one's wording, intentions,
  recommendations, or process, even when it is not an excuse for a prior error.
- Redundancy is contextual: repeat warnings without new content or useful
  synthesis can count. A helpful recap can remain.
- Opening negation that directly answers the question, substantive corrections,
  real uncertainty, and clarification explicitly requested by the user remain
  valid. Negative words are not a metric.

The revised rubric is used for **both** arms. Counts from earlier studies are not
pooled or retrospectively changed. The generators never see it or its criteria.

Before generation, three calls judge five authored answers in
[controls.json](controls.json), with expected labels withheld. They check obvious
self-defense, redundant warnings, clean correction, and explicitly requested
clarification. Every control must match the frozen expected style categories,
retain content, and pass quote/schema validation. A failed control stops the
comparison; all attempts remain on disk. Passing these small controls does not
measure sensitivity to subtle natural examples or establish human agreement.

## Reproduction

[protocol.json](protocol.json) specifies the comparison and interpretation gate.
[execution-manifest.json](execution-manifest.json) hashes inputs and the shared
parent runner/validator and summarizer. [benchmark.py](benchmark.py) is a thin
adapter plus the control gate. It first checks the parent source manifest.

Generation and judging incur model charges. Existing attempts are protected
against overwrite. Use a separate workspace for replication.

```sh
pdm run python evaluations/communication-style/cross-domain/benchmark.py calibrate
pdm run python evaluations/communication-style/cross-domain/benchmark.py generate
pdm run python evaluations/communication-style/cross-domain/benchmark.py judge
pdm run python evaluations/communication-style/cross-domain/benchmark.py summarize
```

Offline validation makes no model calls:

```sh
pdm run pytest tests/test_cross_domain_style_eval.py -q
```

Raw answers contain visible text and usage metadata, never hidden thinking.
Comparative judging shuffles anonymous answers per task. Model judgments and the
implementing assistant's unblinded audit are recorded separately. Shorter output
alone does not establish improvement. A zero/zero target comparison is
inconclusive. The protocol authorizes no automatic template adoption.
