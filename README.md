# FuqingZh/skills

English | [简体中文](README.zh-CN.md)

Skills for engineering judgment, code documentation, clear expression, and
in-depth analysis. Install shared agent instructions for Codex, Grok Build, Pi,
and Antigravity CLI.

## Included skills

| Skill | Purpose | Invocation |
| --- | --- | --- |
| [calibration](skills/calibration/SKILL.md) | Engineering judgment and reference routing | When relevant |
| [writing-code-docs](skills/writing-code-docs/SKILL.md) | Public API and maintainer documentation | When relevant |
| [plainspoken](skills/plainspoken/SKILL.md) | Plain, direct expression with useful detail | Substantive natural-language responses |
| [dissect](skills/dissect/SKILL.md) | Evidence-led explanations, mechanisms, and forecasts | In-depth analysis |
| [closeout](skills/closeout/SKILL.md) | Conversation review and unresolved work | Explicit only |
| [retrospect](skills/retrospect/SKILL.md) | Evidence-backed reusable lessons | Explicit only |

## Quick start

### Install skills

Install [skills CLI](https://github.com/vercel-labs/skills) through your tool
manager, then run the command below. Select only the clients you use; this
example selects Codex, Pi, and Grok Build.

```bash
skills add FuqingZh/skills -g -a codex pi grok -y
```

For an existing installation, review the [migration guide](docs/migrations/v2.md)
and any local skill edits before replacing them.

### Global instructions

After installing the skills, install the shared routing instructions separately
from a trusted checkout. This installer requires Bash and GNU utilities on
Linux/WSL; macOS and native Windows installation have not been validated.

```bash
git clone https://github.com/FuqingZh/skills.git
cd skills
./install.sh --agent all --dry-run
./install.sh --agent all
```

Review the preview before applying it. `install.sh` only manages the shared
instruction block; it does not install skills. To update only Antigravity CLI,
use `./install.sh --agent agy`; it manages `~/.gemini/GEMINI.md`.
For selected clients, custom directories, and backup behavior, see the
[installation reference](docs/installation.md).

## Further reading

- [Installation](docs/installation.md): client discovery, installer options, and safety boundaries.
- [Upgrade to v2](docs/migrations/v2.md) · [Legacy migration](docs/migrations/skills-cli.md).
- [Versions and releases](docs/releases.md) · [Changelog](CHANGELOG.md).
- [Development and validation](AGENTS.md#validation).
- [Evaluation results](docs/testing/20261117-v2.0-release-evidence-summary.md): measured reductions, writing feedback, and limits.
- [Documentation index](docs/README.md): current guidance and historical records.
- [Issues](https://github.com/FuqingZh/skills/issues): include client versions, commands, and sanitized output.
