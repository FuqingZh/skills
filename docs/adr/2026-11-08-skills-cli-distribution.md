# Skills CLI distribution and global instructions

Date: 2026-11-08
Status: Accepted

## Context

This repository distributes first-party skills and shared global routing
instructions across Codex, Grok Build, Pi, and Antigravity CLI (`agy`). Earlier
releases mixed custom skill symlink installation, private host-profile
discovery, and orchestrator integration inside `install.sh` (see `v1.0.0` and
`v2.0.0` in Git history).

## Decision

- Delegate skill installation, updates, and removal to upstream `skills` CLI;
  maintain no second manifest or custom skill package manager.
- Scope `install.sh` strictly to managing the `FuqingZh/skills:begin/end` block
  in each selected client's `AGENTS.md`, with mandatory verified backups on
  changed files and explicit `--force` for unmarked Codex regular files.
- Keep [`templates/AGENTS.md.template`](../../templates/AGENTS.md.template) as
  a minimal three-skill router (`plainspoken`, `dissect`, `calibration`),
  identical across all supported clients.
- Do not discover or render private host configuration or external orchestrator
  integrations from the public package.

## Rejected Alternatives

- **Repository-owned skill installer and link manager**: Duplicated upstream
  `skills` CLI lifecycle and created fragile cross-client link cleanup
  (retired at `v1.0.0`; legacy link cleanup remains a one-off migration script).
- **Automatic private host-profile discovery and AO integration**: Coupled the
  public package to host-local paths and an abandoned orchestrator stack
  (retired at `v2.0.0`).
- **Always-loaded long global instruction block**: Consumed ambient context on
  every turn regardless of task scope (replaced by the three-skill router at
  `v2.0.0`).

## Consequences

- Users install skills via `skills add` and refresh global routing separately
  via `./install.sh`.
- Client-specific discovery and installer safety contracts remain owned by
  [`docs/installation.md`](../installation.md) and `tests/test_install.py`.

## Reopen When

- Upstream `skills` CLI stops supporting a target client or breaks lockfile
  compatibility.
- A supported client changes its global instruction file contract.
