# Complete talk-normal comparison

Status: complete; [results](results.md) and [author audit](audit.md) recorded.
Inputs were frozen at `d06b84a`. This is a separate user-requested follow-up to
the [original comparison](../README.md). It does not change that study's prompts,
scores, selection decision, or runtime instructions.

## What is tested

The treatment is the entire upstream `prompt.md`, version 0.6.2, from
[hexiecs/talk-normal at d89cf329](https://github.com/hexiecs/talk-normal/tree/d89cf329e775e640181427fae071652198264c7e).
Its bytes are preserved in [prompts/talk-normal.txt](prompts/talk-normal.txt),
including examples, the contrast ban, and the 3–5-sentence conceptual-explanation
rule. It is the sole system prompt, as the upstream API usage recommends. We
neither trim its rules nor stack our communication paragraph on top of it.

The [MIT license](upstream-LICENSE.txt), copyright 2026 hexie, accompanies this
copy. Git blob identities were checked against the pinned GitHub contents API:

| Upstream file | Git blob SHA-1 |
| --- | --- |
| `prompt.md` | `a805b42f959e24f3a404d39e20f1213647fc532f` |
| `LICENSE` | `db40ec036aef0a3c7fd1ad19821d149f0db4fef1` |

This is a system-prompt evaluation, not an installation or compatibility test
of upstream OpenClaw, Hermes, or ChatGPT integration. Design-source context is
in the [source register](../../../docs/sources.md#s01-talk-normal).

## Comparison

- All [12 existing cases](../cases.json), unchanged: six long and six short.
- Two arms: the original paragraph and complete talk-normal.
- Two fresh requests per case per arm: 48 responses total, randomly interleaved
  with three workers. The baseline is regenerated in this run, not borrowed from
  the previous experiment.
- Same generator (`openai/gpt-6-astra`, high), judge (`openai/gpt-6-sol`, high),
  task text, required content, and [judge prompt](judge.txt) as the prior study.
- Existing response-only isolation: no sessions, ambient context files, skills,
  extensions, MCP, or tools. No hidden thinking is saved or inspected.
- One separate judge request per task; shuffled anonymous answer IDs without
  source-prompt or arm labels. Judgments remain same-family model predictions.

The former development and holdout cases are combined only in memory under the
execution label `benchmark`. Their source file and original labels remain
unchanged. Once run here, the formerly held-out cases are observed for future
studies. This is a fixed benchmark comparison with no candidate selection or
post-result prompt tuning, and makes no claim to be the original holdout trial.

The question is whether complete upstream behavior meets these user tasks. The
rubric does not reward obeying upstream brevity constraints at the cost of
required reasoning, correction, a requested analogy, or uncertainty reporting.
Length and timing remain secondary descriptive metrics.

## Reproduction and evidence

[protocol.json](protocol.json) and [execution-manifest.json](execution-manifest.json)
freeze the upstream material, baseline, cases, judge, adapter, and shared engine.
[benchmark.py](benchmark.py) reuses the parent generator, evidence validator, and
summary calculations. Only its root and case-split view change in the isolated
adapter process. The parent engine validates its own manifest before use.

The following generation and judging commands incur model charges. Existing
output directories are protected against overwrite; use a separate workspace
for a replication of this fixed-layout follow-up.

```sh
pdm run python evaluations/communication-style/talk-normal/benchmark.py generate
pdm run python evaluations/communication-style/talk-normal/benchmark.py judge
pdm run python evaluations/communication-style/talk-normal/benchmark.py summarize
```

Offline adapter tests use a fake invocation function, verify 48 attempts receive
exactly the expected prompts, check byte identity and manifests, and reject
output reuse. No model calls are made by ordinary repository validation:

```sh
pdm run pytest tests/test_talk_normal_eval.py tests/test_communication_style_eval.py -q
```
