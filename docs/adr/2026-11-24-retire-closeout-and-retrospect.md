# Retire closeout and retrospect skills

Date: 2026-11-24
Status: Accepted

## Context

`closeout` and `retrospect` were explicit-only skills (`disable-model-invocation: true`,
the only two first-party skills requiring `agents/openai.yaml`). `closeout`
originated before native `/compact` and prompt caching made same-session
continuation practical, and accumulated Codex-specific archival gating.
`retrospect` maintained a `.retrospect/` diary layout whose practical leverage
on subsequent agent behavior remained unclear (preserved in Git history at
`v2.1.0` and commit `430240a`).

## Decision

- Retire `skills/closeout/` and `skills/retrospect/`, narrowing the first-party
  collection to four implicitly invocable core skills: `calibration`,
  `writing-code-docs`, `plainspoken`, and `dissect`.
- Rely on native `/compact` and `/clear` for routine session management,
  upstream `handoff` (`mattpocock/skills`) when moving hot context across
  harnesses or directories, `calibration`'s ADR rules for durable decisions,
  and `calibration`'s `harness.md` placement ladder for fixing repeated agent
  failures at the lowest durable layer.

## Rejected Alternatives

- **Slimming `closeout` to a lightweight session-handoff macro**: Overlapped
  with `/compact` and upstream `handoff` (which writes cleanly to `$TMPDIR`
  without dirtying Git status), while persisting an ADR takes a single natural
  request.
- **Keeping `retrospect` with `.retrospect/` records**: Creating retrospective
  diaries duplicated the stale-documentation problem without changing
  executable repository feedback.

## Consequences

- First-party skills no longer require any `agents/openai.yaml` metadata files.
- Removing `closeout` and `retrospect` is a breaking skill-catalog change for
  the next major release under [`docs/releases.md`](../releases.md).

## Reopen When

- Repeated multi-session work shows a durable gap not covered by native
  compaction, upstream `handoff`, and `calibration`.
