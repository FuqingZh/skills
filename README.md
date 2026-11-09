# FuqingZh/skills

Portable engineering skills and global agent instructions for Codex, Grok Build,
and Pi. Repository-owned contracts and upstream standards guide local work;
calibration supplies reusable judgment and safety boundaries.
The repository was formerly named `FuqingZh/calibration`; the `calibration` skill
name and its private configuration namespace remain unchanged.

## Quick start

Install [skills CLI](https://github.com/vercel-labs/skills) through your tool
manager (for example, mise's `"npm:skills" = "latest"`). Then install the four
first-party skills:

```bash
skills add FuqingZh/skills -g -a codex pi grok -y
```

The global installer requires Bash and GNU utilities on Linux/WSL. macOS and
native Windows installation have not been validated.

Global instructions are a separate, explicit installation from a trusted checkout:

```bash
git clone https://github.com/FuqingZh/skills.git
cd skills
./install.sh --agent all --dry-run
./install.sh --agent all
```

Review existing installations before migration; see [legacy migration](#legacy-migration).
Select only the agents you use. `-a codex pi` uses space-separated names.
Codex and Pi discover `~/.agents/skills` directly; Grok receives discovery links.
Shared storage can be visible to other clients scanning it. Agent selection is
not an isolation boundary.

## Included skills

| Skill | Purpose | Invocation |
| --- | --- | --- |
| [calibration](skills/calibration/SKILL.md) | Engineering judgment and reference routing | When relevant |
| [writing-code-docs](skills/writing-code-docs/SKILL.md) | Public API and maintainer documentation | When relevant |
| [closeout](skills/closeout/SKILL.md) | Conversation review and unresolved work | Explicit only |
| [retrospect](skills/retrospect/SKILL.md) | Evidence-backed reusable lessons | Explicit only |

The patched `teach` and `grilling` copies are [archived](thirdparty/archive/README.md)
with provenance, licenses, and historical evaluations. Personal learning data is
outside this migration. To choose unmodified upstream grilling separately:

```bash
skills add mattpocock/skills --skill grilling -g -a codex pi grok -y
```

This follows Matt's default branch and its upstream interaction and invocation
policy, including batched dependency-frontier questions and subagent assumptions.
It does not carry calibration's former patches.

## Skill lifecycle and versions

Use `skills list -g`, `skills update`, and `skills remove` for the upstream-managed
lifecycle. Read the command's current help before destructive operations. Repeated
`skills add` can overwrite installed edits; removal can delete matching shared
content. These are normal CLI semantics. Setup attaches the native global lock;
restoration and updates remain explicit. This repository maintains no second lock.

With tested skills CLI 1.7.6, pin a source with `FuqingZh/skills#<tag-or-full-sha>`.
`skills update` follows the recorded ref; advancing a release pin or rolling back
requires explicit `skills add` with the desired ref. CLI version and source version
are independent. Global instructions change only when `install.sh` is rerun from
the selected checkout. See [release policy](docs/releases.md) and
[release notes](CHANGELOG.md); the proposed `v1.0.0` tag has not been published.

## Global instructions

The executable Bash entrypoint is `./install.sh`; `bash install.sh` also works.
It supports four options: `--agent`, `--dry-run`, `--force`, and `--help`
(`-h`). The default agent is Codex. No package or global CLI wrapper is required.

Advanced layouts and isolated tests use environment variables with absolute paths:

| Client | Home variable | Default when unset or empty |
| --- | --- | --- |
| Codex | `CODEX_HOME` | `~/.codex` |
| Grok Build | `CALIBRATION_GROK_HOME` | `~/.grok` |
| Pi | `PI_CODING_AGENT_DIR` | `~/.pi/agent` |

`CALIBRATION_GROK_HOME` configures these scripts only; it does not configure Grok
or skills CLI. For example, `CODEX_HOME=/absolute/test-home ./install.sh --dry-run`.

`install.sh` manages a `<!-- FuqingZh/skills:begin -->` / `<!-- FuqingZh/skills:end -->`
block in each selected `AGENTS.md`. It preserves text outside valid blocks,
preflights all destinations, always backs up changed existing files, and is idempotent.
Dry-run performs no writes. A missing file receives a new block; Pi and Grok
append a block to an unmarked regular file. Symlink targets, directories, malformed
or repeated markers, unsafe homes, and overlapping selected homes are rejected.
An existing valid `calibration:begin/end` block is backed up and migrated to the
new namespace without `--force`. Mixed namespaces and mismatched pairs fail
without writes, even with force; dry-run identifies a planned migration.

The template renders the private host-authority pointer using absolute
`$XDG_CONFIG_HOME/calibration/AGENTS.md` or `$HOME/.config/calibration/AGENTS.md`.
It does not create that private file. `$calibration` invocation spelling is rendered
as `calibration` for Pi and Grok. Client discovery does not prove model compliance.

## Legacy migration

Follow the [migration guide](docs/migrations/skills-cli.md) for old skill links
and unmarked Codex files. Cleanup is a separate migration operation; normal
installation never removes skills. Removed options fail explicitly.

## Development

Use Python 3.12+ and PDM to install the locked validation environment:

```bash
pdm sync --clean
pdm lock --check
pdm run check
```

The full gate runs Ruff, Pyright, rumdl, Markdown link checks, ShellCheck,
pytest with 100% line coverage for repository-owned Python tools, and skill
validation. Ruff uses the explicit stable baseline `E`, `F`,
`I`, `UP`, `B`, `SIM`, and `RUF`; preview rules are not enabled.
For a focused installer change:

```bash
pdm run lint-shell
pdm run test tests/test_install.py
pdm run validate-skills
```

Installer tests use isolated configuration homes. Select checks proportionally
to the changed behavior; [AGENTS.md](AGENTS.md) describes contribution and
validation requirements.

## Documentation and support

- [Documentation index](docs/README.md): current decisions, evaluation results,
  migration history, and implementation plans.
- [Engineering references](skills/calibration/references/principles.md): principles
  and the [skill router](skills/calibration/SKILL.md) for focused guidance.
- [Multi-client installation](docs/decisions/2026-09-24-multi-client-skill-installation.md):
  compatibility decisions, native discovery checks, and evidence limits.
- [Issues](https://github.com/FuqingZh/skills/issues): bug reports and
  improvement proposals. Include the client version, command, and relevant
  sanitized output when reporting installation problems.

Behavioral prompts and evaluations support bounded conclusions under their
recorded conditions. Skill discovery and passing static checks do not establish
equal behavior across clients or a general improvement in model performance.
