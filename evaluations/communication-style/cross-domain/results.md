# Cross-domain comparison results

## Outcome

**The revised paragraph did not demonstrate a target-style improvement.** Both
arms received zero style findings under the clarified judge rubric. Content
coverage was complete under the frozen criteria, with no critical findings.
The revised arm generated **14.7% more characters**. No runtime instruction was
changed.

Inputs were frozen at `00d793f`. All three pre-generation control calls passed.
The comparison completed all 32 generations and eight blinded judge calls, with
no transport failures, invalid judgments, retries, or discarded attempts.
[summary.json](summary.json) reproduces the raw model scores. The implementing
assistant read all 32 answers; its separate [audit](audit.md) documents useful
boundaries and editorial issues missed by an all-zero aggregate.

## Model-rated outcomes

Each arm has 16 responses: eight long and eight short, with two repetitions per
case. Counts below describe the judge's decisions, not established correctness.

| Measure | Baseline | Revised |
| --- | ---: | ---: |
| Responses | 16 | 16 |
| Required-content omissions | 0 / 60 | 0 / 60 |
| Critical findings | 0 | 0 |
| Style findings | 0 | 0 |
| Clear / mixed clarity | 15 / 1 | 16 / 0 |
| Total characters | 17,968 | 20,605 |
| Long-answer characters | 15,617 | 17,888 |
| Short-answer characters | 2,351 | 2,717 |
| Median long-answer characters | 2,122.5 | 2,448.5 |
| Median short-answer characters | 250 | 275.5 |
| Mean generation seconds | 40.411 | 42.535 |
| Input tokens | 3,412 | 3,268 |
| Output tokens | 13,599 | 15,338 |
| Total tokens | 17,011 | 18,606 |
| Estimated generation USD | 0.71407 | 0.79958 |

Long answers grew 14.5%; short answers grew 15.6%. Generation cost grew 12.0%.
Pi reports usage/cost estimates (`totalFromProvider: false`); billed output can
include reasoning tokens, while the stored answers contain only visible text.
Generation cost for both arms was USD 1.51365, comparative judging USD 0.149946,
and controls USD 0.013346: **USD 1.676942** estimated total.

The single mixed-clarity result is `o2-baseline-2`: “就业机会与照护责任如何限制脱贫”.
The judge observed that readers may need “就业机会不足” to understand why employment
opportunities would restrict escape from poverty. The revised headings avoid
that ambiguity. This isolated wording difference does not establish a general
clarity advantage.

## Reading the comparison

- **Necessary correction survived.** All four p-value answers directly reject the
  reversed probability interpretation and explain the conditional direction.
- **Requested clarification survived.** All four `p2` answers directly explain
  whether a title suggestion entails a philosophical judgment. Their opening
  negation addresses the user's explicit question.
- **Explicit repair worked in both arms.** All four `c2` answers are exactly
  “这次的问题出在安排上。” No renewed defense follows. Because the user explicitly
  identifies and requests removal of the failure, this tests correction after
  feedback, not spontaneous prevention.
- **Depth survived.** The long answers develop mechanisms, examples, competing
  interpretations, and evidential limits. No length cap was imposed.
- **Natural prose still contains unnecessary framing candidates.** For example,
  `c1-revised-2` adds “不必先争出谁更委屈”, although the user never asks who is more
  aggrieved. `p1-revised-2` introduces a contrast with “互相排斥的三种答案” while
  summarizing three layers the user already asks to connect. The audit gives
  context-preserving direct alternatives. These remain separate from raw scores.

The obvious controls successfully distinguished deliberate self-defense and
repetition from clean answers. They did not establish agreement with the user's
preferences on subtler natural prose. The zero/zero comparison leaves no observed
target reduction to attribute to the revised prompt.

The revised text replaces the whole paragraph. The increased length cannot be
assigned to a particular phrase such as “develop the reasoning coherently” from
this design. More characters also do not establish that the added information is
unnecessary: some revised explanations develop additional qualifications.

## Scope and decision

This small constructed development set uses one generator and a same-family
judge. It does not reproduce a long evolving conversation or the full installed
instruction stack. The audit is by the implementing assistant, unblinded to arms;
no independent human preference ranking or cross-family replication was run.
Earlier study counts use a different rubric and remain separate.

**Keep the runtime baseline.** The frozen gate requires reduced target findings
without increased omissions, critical errors, or lost necessary clarification.
The target-reduction condition is unmet. The next informative measurement would
need naturally recurring failures and user-calibrated judgments of their
information function; increasing repetitions of these already-clean tasks would
not address that measurement gap.
