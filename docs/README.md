# FuqingZh/skills Documentation

Code, tests, CI, and the skill sources under [`skills/`](../skills) are the
authority for active behavior. This index maps only the durable documentation
that code cannot convey on its own.

## Active Guides And Policies

| Need | Source |
| --- | --- |
| Project overview and quick start | [README](../README.md) · [简体中文](../README.zh-CN.md) |
| Installer contract and client discovery | [Installation](installation.md) |
| Release versioning and pinning | [Releases](releases.md) · [Changelog](../CHANGELOG.md) |
| Upgrade and migration guides | [Upgrade to v2](migrations/v2.md) · [Legacy skills CLI migration](migrations/skills-cli.md) |
| External design attribution and licenses | [External sources](sources.md) |
| Repository validation and contribution rules | [AGENTS.md](../AGENTS.md) |

## Active Decisions (`docs/adr/`)

- [Skills CLI distribution and global instructions](adr/2026-11-08-skills-cli-distribution.md)
- [Proportional validation and PDM check routing](adr/2026-10-11-validation-and-check-routing.md)
- [Concise explanation-first framing for plainspoken and dissect](adr/2026-11-17-expression-and-analysis-framing.md)
- [Code-first minimal documentation model](adr/2026-11-24-code-first-documentation-model.md)

## First-Party Skill Entrypoints

| Skill | Entrypoint |
| --- | --- |
| Engineering judgment and reference routing | [calibration](../skills/calibration/SKILL.md) |
| Public API and maintainer docstrings | [writing-code-docs](../skills/writing-code-docs/SKILL.md) |
| Plain, direct natural-language expression | [plainspoken](../skills/plainspoken/SKILL.md) |
| Evidence-led analysis and forecasting | [dissect](../skills/dissect/SKILL.md) |
| Explicit conversation closeout | [closeout](../skills/closeout/SKILL.md) |
| Explicit evidence-driven retrospective | [retrospect](../skills/retrospect/SKILL.md) |

Superseded decisions, completed plans, and historical snapshots live in Git
history (see tags `v1.0.0`, `v2.0.0`, `v2.1.0`). Raw evaluation artifacts
remain under `evaluations/`.
