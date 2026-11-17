# Unblinded audit of the incomplete sentence ablation

The implementing assistant read 86 complete answers after treatment identities
were available. This is an editorial audit, not an independent blind human
rating. It covers every flagged answer in the seven-case diagnostic subset,
all `p2` and `c2` responses, the largest absolute task effect for each sentence
(first task in case order for ties), three flagged `c1-2` answers and the answer
whose evidence caused both validation failures. The inventory is in
[audit-inventory.json](audit-inventory.json). Model scores remain unchanged.

## Exact-quote failure

Both `c1-1` attempts rated the progression of `c1-drop4-1` below four, citing its
concluding sentence without the Markdown markers. The actual answer contains:

> 重点是：**对这次失约的影响负责，同时诚实表达你的疲惫和现实限制。** 修复靠的是听见影响和后续兑现，不是把自己说得越差越好。

The repeated substance exists. The evidence string does not match the original
bytes because formatting was omitted. The frozen check correctly rejects that
representation under its literal-substring contract. The controls had not tested
this Markdown-spanning evidence case. The first failure and the single failed
retry are both retained; no manual repair is included in numerical results.

## Necessary correction and requested clarification

The p-value answers directly correct the user's mistaken probability reading.
Those opening negations answer the actual question and should remain. The model
ratings do not classify those corrections as invented contrasts.

The title task explicitly asks whether a proposed revision implies the original
title is philosophically wrong. Addressing that interpretation is required.
Several answers subsequently repeat the interpretation disclaimer; that later
repetition can be edited separately from the necessary opening clarification.

All twenty `c2` answers are identical: “这次的问题出在安排上。” The user explicitly
requested that repair. This is evidence of following direct feedback in this
fixture; it does not measure spontaneous avoidance of self-defense.

## Effects depend on small and sometimes debatable findings

### S1 and S2: gains outside their target dimensions

S1's small overall gain comes from the wording “竞争性、可检验的解释” in `o1-drop1-1`.
The judge treats the jointly acting mechanisms as complementary. Mechanisms may
also compete as explanations of observed variation, so this wording penalty is
open to interpretation. Plainness/depth did not differ.

S2's difference comes from framing and repetition rather than a measured change
in focus/coherence. It does not establish the relative importance of coherent
reasoning as a general instruction.

### S3, S4 and S5: corresponding signals, limited evidence

S3's intended dimension improves in two tasks involving unnecessary contrasts.
S4's intended dimension improves in one p-value response with insufficiently
local qualification. These are reused development tasks, with no independent
validation set.

S5's progression gain comes entirely from the two p-value responses. The endings
repeat the central correction after the requested additional evidence. There is
also uneven grading around useful synthesis versus repetition: `s2-full-1` ends
with another rejection of the “结论有 97% 的概率正确” interpretation, without a finding;
`s2-drop5-2` has a comparable closing paragraph with new significance-threshold
information and a repeated correction, and is flagged. The extra repetition is
more extensive in the latter, but the score difference remains a judgment about
prose, not an objective error count.

### One heading affects several overall effects

`o2-full-1` starts with “就业机会与照护责任如何限制脱贫”. The judge reasonably notes
that “就业机会” needs a qualifier such as “不足” when used as an obstacle. Several
deletion arms use “如何影响贫困” instead and avoid this ambiguity. That one
full-arm defect offsets apparent benefits of S3, S4, S5 and S7 elsewhere.

`o2-minimal-1` uses “就业机会与照护负担如何让人陷入贫困”. The judge marks one content
omission and a critical error for stronger causal wording. The heading is
imprecise, but treating it as a critical causal claim is debatable: it names two
factors in an explanatory question and asserts no measured causal estimate.
This classification should not become proof that the full paragraph improves
correctness. The original rating and full/minimal difference remain recorded.

### S6 and S7: no measured advantage in their own target dimensions

S6 has the largest overall point estimate in the available subset. Its gains
come from contrast and repetition ratings; unsolicited self-defense scores do
not differ. Literal removal of S6 leaves the reference in S7 unresolved, so the
condition also includes that syntactic dependency.

S7 has no measured target-dimension advantage on either applicable task. Other
small differences, including one mixed-language phrase and the heading issue,
do not establish its intrinsic weight. The interaction interval is wide around
zero in the selected subset.

## Uneven sensitivity in natural responses

The full arm has no model-rated style findings, yet its answers contain similar
editorial opportunities. For example, `o1-full-1` contrasts useful peer-network
mechanisms with dividing friends into “好” and “坏”; `o1-drop7-2` is penalized for
rejecting “好朋友带好、坏朋友带坏”. Context and phrasing differ, but this comparison
shows why zero full-arm findings cannot be read as editorial perfection.

The excluded valid `c1-2` comparison also contains useful observations: one
answer invents a concern about excessive apology/compensation, another assumes
the original promise was casual, and another overstates certainty that a future
meeting time will be unaffected by work. These observations remain available but
do not enter the seven-task numerical summary.

## Interpretation

The available data support inspecting S3–S5's intended behaviors more closely.
They do not establish stable sentence weights, reliable automatic preferences or
a completed eight-task result. The full paragraph, deletion arms and minimal
anchor all perform near the ceiling of this rubric. Further evaluation would
need better agreement on these contextual distinctions and an evidence format
that the grader can reliably produce. Runtime instructions remain unchanged.
