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

## Quick start

### Install skills

Install [skills CLI](https://github.com/vercel-labs/skills) through your tool
manager, then run the command below. Select only the clients you use; this
example selects Codex, Pi, and Grok Build.

```bash
skills add FuqingZh/skills -g -a codex pi grok -y
```

For an existing installation, review the [changelog](CHANGELOG.md) (and the
[v2 migration guide](docs/migrations/v2.md) if upgrading from v1) and any local
skill edits before replacing them.

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
use `./install.sh --agent agy`; it manages `~/.gemini/AGENTS.md`.
For selected clients, custom directories, and backup behavior, see the
[installation reference](docs/installation.md).

If you already use mise, review this checkout's [`mise.toml`](mise.toml) before
trusting it. From the repository root, run:

```sh
mise trust ./mise.toml
mise run install agy --dry-run
```

Trust enables the task. With mise shell completion enabled, Tab completes
clients and options. If you prefer not to trust the mise config, use
`./install.sh` directly.

## Further reading

- [Installation](docs/installation.md): client discovery, installer options, and safety boundaries.
- [Versions and releases](docs/releases.md) · [Changelog](CHANGELOG.md).
- [v1→v2 migration](docs/migrations/v2.md) · [Legacy skills CLI migration](docs/migrations/skills-cli.md).
- [Development and validation](AGENTS.md#validation).
- [Documentation index](docs/README.md): active contracts and architecture decisions.
- [Issues](https://github.com/FuqingZh/skills/issues): include client versions, commands, and sanitized output.
