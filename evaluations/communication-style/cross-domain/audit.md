# Full-answer author audit

The implementing assistant read all **32 complete answers**, both repetitions
of both arms for `p1`, `p2`, `s1`, `s2`, `o1`, `o2`, `c1`, and `c2`. This audit is
unblinded to arms. The model's zero style findings remain unchanged in the raw
artifacts and [summary](summary.json). Observations below concern information
function and task fit; no independent human preference ranking was obtained.

## Coverage and substantive boundaries

| Case | What all four answers retain | Additional observation |
| --- | --- | --- |
| `p1` | Causal influences, reasons-responsive capacities, responsibility practices, a coherent example and philosophical disagreement | Revised answers add some extended objections and distinctions; baseline answers also cover the controversy. |
| `p2` | Direct answer to whether a title suggestion implies philosophical error, both titles' focus and fit to the article | Explicitly requested clarification is appropriate here, including the opening negation. Both arms sometimes restate the opening judgment at the end. |
| `s1` | Association/causation, reverse causality, confounding, randomized design and practical measurement/analysis issues | All separate assignment effects from adherence and limit generalization. Revised answers spend more space on the study sequence and frequency threshold. |
| `s2` | Correct conditional interpretation of p-values and additional evidence needed | Both revised answers retain a forceful opening correction. Their greater length does not establish a necessary-content gain. |
| `o1` | Interacting resources, institutions, peers and effort; hypothetical students; observable evidence and identification limits | Hypothetical family circumstances are marked as such. Peer selection is distinguished from influence, and mediators from ordinary adjustment variables. |
| `o2` | Three usable headings, in order, without a defensive afterword | `o2-baseline-2` has the judge's single wording ambiguity. Revised repetitions are identical. |
| `c1` | Both parties' possible needs, conditional motives, concrete impact, a message and follow-up | Possible past patterns are conditional, not asserted facts. Both arms sometimes introduce concerns the user has not voiced. |
| `c2` | Direct rewrite without renewed self-defense | All four answers are identical: “这次的问题出在安排上。” The explicit correction request strongly elicits this response. |

The philosophical answers distinguish influence from determinism, and practical
repair or protection from basic-desert punishment. They do not claim to settle
the free-will dispute scientifically. The science answers distinguish a
hypothetical study plan from observed data. No critical error beyond the model's
zero count was identified in this reading; this is a bounded review of the
visible answers, not independent domain-expert verification.

## Contextual editing examples

These examples expose distinctions hidden by the aggregate score. Each links to
the complete answer so the surrounding information remains inspectable.

### 1. Preserve an opening correction that answers the question

In [s2-revised-2](results/benchmark/s2-revised-2.json), the user asks whether
p=0.03 means a 3% probability that the null is true and 97% correctness:

> 不对。**p=0.03 既不表示“原假设只有 3% 的概率是真的”，也不表示“实验结论有 97% 的概率正确”。**

This directly corrects the supplied misconception. The answer then supplies the
conditional definition, explains the reversed conditioning, and discusses
study design and uncertainty. Removing the negation would weaken the answer.

### 2. Preserve requested interpretation of the assistant's suggestion

In [p2-revised-1](results/benchmark/p2-revised-1.json), the user explicitly asks
whether the suggested title means the old title is philosophically wrong:

> 不是。建议改成“自由需要哪些条件”，并不意味着我认为“自由不是随心所欲”在哲学上是错的。

The opening responds to the question. It is not the unsolicited defense observed
in the earlier conversation. At the end, however, the answer returns to:

> **这是对标题与论述重心是否匹配的判断，不是对原标题作哲学上的判错。**

The preceding conditional recommendations already explain which title fits
which article. Ending after those recommendations would retain the answer's
reasons and applicability. The baseline also has a comparable return to the
opening in [p2-baseline-1](results/benchmark/p2-baseline-1.json):

> 改题建议首先是对文章重心和表达效果的判断，不能据此推断原标题在哲学上错误。

The judge permits useful recaps. User preference for these particular closing
restatements remains unmeasured; their shared presence limits any claim that the
new paragraph reliably moves on from established points.

### 3. Remove a conflict frame that the user has not raised

[c1-revised-2](results/benchmark/c1-revised-2.json) identifies the user's fatigue
and the friend's disrupted plans, then adds:

> 这两件事可以同时成立，不必先争出谁更委屈。

The user says the friend is angry and asks how to talk; no contest over who is
more aggrieved is stated. “这两件事可以同时成立。” preserves the point and leads
straight into both parties' possible needs. It loses no proposed repair or
communication boundary.

The baseline has an adjacent framing choice in
[c1-baseline-1](results/benchmark/c1-baseline-1.json):

> 道歉不需要否定自己的辛苦，疲惫也需要被清楚地表达出来。

A direct alternative is “可以承认取消对朋友造成的影响，也说明自己需要休息。”
It preserves both emotional recognition and the communication boundary without
introducing denial of one's hardship.

### 4. State the relationship without inventing an opposing interpretation

Near the end of [p1-revised-2](results/benchmark/p1-revised-2.json):

> 因果解释、行动能力和责任实践不是互相排斥的三种答案，而是三个相接的问题：

The user already asks how those three layers connect, and the body explains
each. A direct transition is “因果解释、行动能力和责任实践连接起三个问题：”.
The following questions then preserve the substantive synthesis:

> **是什么使他这样行动？这些因素是否削弱了他的理解与控制？在此基础上，向他提出什么要求才公平？**

The connective summary is useful. The opposing interpretation “互相排斥” is not
needed to express it. The model reported no invented-contrast finding here.

## What the controls and full read establish

All three control calls match their frozen expected categories. The deliberately
self-defensive afterword and repeated causal warnings are detected; the clean
answers and explicitly requested clarification are unflagged. The control set
is too small and obvious to establish sensitivity to natural borderline prose.

The full read finds preserved depth, corrections, uncertainty and requested
clarification. It also finds opportunities for more direct wording in both
arms, despite zero model findings. No spontaneous self-defense of the originally
observed kind recurred in these tasks. The strongest reconstruction, `c2`, tests
repair after explicit feedback, so its success cannot establish prevention in
ordinary ongoing conversation.

The comparison therefore supports neither adoption nor an equivalence claim.
It supplies negative selection evidence under the frozen gate, plus concrete
material for calibrating what a future evaluator should distinguish.
