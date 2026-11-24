# Concise explanation-first framing for plainspoken and dissect

Date: 2026-11-17
Status: Accepted

## Context

`plainspoken` and `dissect` govern natural-language explanation and in-depth
analysis. Earlier wording encouraged models to add their own objections and
counterexamples, which produced unsolicited proof demands, acceptance warnings,
and corrective detours during pure explanation tasks. Multiple pilots tested
shorter wording, request-scoped evaluation branches, and automated LLM
preference judges (archived in Git history at `v2.1.0` and commit `179747a`).

## Decision

- Keep the concise prohibition against assistant-added objections, corrections,
  acceptance warnings, and proof demands in
  [`skills/plainspoken/SKILL.md`](../../skills/plainspoken/SKILL.md) and
  [`skills/dissect/SKILL.md`](../../skills/dissect/SKILL.md), while retaining
  source attribution, source-internal disagreements, and accurate failure and
  permission reporting.
- Scope `dissect`'s author-reconstruction prohibition to the author-reading
  paragraph without adding explicit "when asked to evaluate or correct" escape
  clauses (refined in commit `2a552d4`).
- Treat this wording as an explicit user preference decision, not a claimed
  cross-model quality gain.

## Rejected Alternatives

- **Proactive constructive-objection guidance**: Consistently triggered
  unsolicited cautions and proof-gap disclaimers across GPT, Qwen, Grok, and
  DeepSeek samples (`v2.1.0` framing pilot, 23 generations).
- **Paired request-scoping clauses ("evaluate/correct directly when asked")**:
  Tested in 64 fresh generations (`179747a`). It made GPT more direct on one
  explicit evaluation prompt (coverage 0.77–0.88 to 0.99), but did not fix
  repeated known-limit reminders in completion reports (still 2/3 usable
  reports plus 1 pseudo-tool output failure) and did not reliably reduce
  unsolicited commentary.
- **Automated LLM preference judges as adoption gates**: Earlier v3/v4 judge
  runs exhibited order conflicts and high contract-invalidity rates (19/24
  invalid in v4), and the request-scoping aside judge missed subtle completion
  reminders (0.02–0.04 on known-limit repetitions). Automated judges cannot
  replace human review for subtle style preferences.

## Consequences

- High-frequency explanation and reporting tasks avoid defensive disclaimers,
  at the small cost that explicit textual critique prompts may occasionally
  need direct user framing.
- Future wording changes must be evaluated one skill at a time on fresh
  representative tasks rather than relying on static checks or automated judges.

## Reopen When

- Repeated real-session use shows `plainspoken` or `dissect` suppressing
  explicitly requested criticism, teaching corrections, or code reviews.
