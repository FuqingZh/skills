# Installation reference

[Quick start](../README.md#quick-start) covers installing skills and shared
routing instructions. This reference owns client discovery, installer options,
and managed-file behavior. For existing installations, also read the
[migration guide](migrations/v2.md).

## Skill installation and discovery

Install [skills CLI](https://github.com/vercel-labs/skills) through your tool
manager; for example, mise supports `"npm:skills" = "latest"`.
The CLI installs and manages the [six first-party skills](../README.md#included-skills).
Select only the clients you use. In `-a codex pi`, client names are space-separated.

Codex and Pi discover `~/.agents/skills` directly; Grok receives discovery links.
Other clients scanning shared storage can also see those skills. Agent selection
is not an isolation boundary.

Use `skills list -g`, `skills update`, and `skills remove` for the upstream-managed
lifecycle. Read the current CLI help before destructive operations. Repeated
`skills add` can overwrite installed edits; removal can delete matching shared
content. Setup attaches the native global lock; restoration and updates remain
explicit. This repository maintains no second lock.

For source pinning, upgrades, and rollback, see [versions and releases](releases.md).
CLI versions and skill source versions are independent. Updating skills does not
refresh the shared global instructions described below.

## Global instructions

The executable entrypoint is `./install.sh`; `bash install.sh` also works.
It requires Bash and GNU utilities on Linux/WSL. Installation on macOS and native
Windows has not been validated. Run it from a trusted checkout.

Install the skills before refreshing the global block. The installer only
manages shared instructions; it does not install, update, remove, or verify the
presence of skills. Legacy link cleanup is a separate
[migration operation](migrations/skills-cli.md).

The shared [template](../templates/AGENTS.md.template) routes substantive responses
to `plainspoken`, in-depth analysis to `dissect`, and matching engineering work
to `calibration`. Detailed methods live in the skills. Descriptions guide native
model selection, and skills can apply together. Discovery and passing static
checks do not establish model compliance, equal behavior across clients, or a
general improvement in model performance.

Every client receives the same template. The installer does not discover, read,
or render private host configuration; existing private files remain untouched.

### Options

| Option | Behavior |
| --- | --- |
| `--agent AGENTS...` | Select `codex`, `grok`, `pi`, or `all`; defaults to Codex. |
| `--dry-run` | Preview without writing files. |
| `--force` | Back up and replace an existing unmarked Codex regular file. |
| `--help`, `-h` | Show usage. |

For example, refresh only Codex and Pi:

```bash
./install.sh --agent codex pi --dry-run
./install.sh --agent codex pi
```

Review the preview before applying it. Removed options fail explicitly rather
than silently changing scope. No package or global CLI wrapper is required.

### Custom homes

Non-empty home environment variables must contain absolute paths:

| Client | Home variable | Default when unset or empty |
| --- | --- | --- |
| Codex | `CODEX_HOME` | `~/.codex` |
| Grok Build | `CALIBRATION_GROK_HOME` | `~/.grok` |
| Pi | `PI_CODING_AGENT_DIR` | `~/.pi/agent` |

`CALIBRATION_GROK_HOME` configures these scripts only; it does not configure Grok
or skills CLI. For an isolated preview:

```bash
CODEX_HOME=/absolute/test-home ./install.sh --dry-run
```

### Managed-file behavior

The installer manages the block delimited by `<!-- FuqingZh/skills:begin -->`
and `<!-- FuqingZh/skills:end -->` in each selected client's `AGENTS.md`.
It preserves text outside valid blocks and preflights all selected destinations
before the first write. Changed existing files are always backed up and the
backup is verified before replacement. Each file is replaced atomically;
unchanged files are left alone and create no backup.

| Existing target | Behavior |
| --- | --- |
| Missing file | Create a new managed block. |
| Valid current block | Refresh the block, preserving surrounding text. |
| Valid legacy `calibration:begin/end` block | Back up and migrate without `--force`; preview identifies the migration. |
| Unmarked Pi or Grok regular file | Append the managed block. |
| Unmarked Codex regular file | Stop unless `--force` is explicit; personal text remains in the verified backup. |
| Symlink, directory, malformed or repeated block, mixed or mismatched markers | Reject, including with `--force`. |

After a forced Codex replacement, restore personal rules from the backup outside
the new block; see [unmarked Codex instructions](migrations/skills-cli.md#unmarked-codex-instructions).

Unsafe homes and overlapping selected homes are rejected. In particular, a home
must not be `/`, lie inside the checkout, or contain the checkout. Repeated or
nested target directories are also rejected. Dry-run performs no writes.
