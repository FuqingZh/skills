# Migration to skills CLI

Run migration commands from the original calibration checkout. Preview each
operation before applying it; ordinary installation and setup bootstrap never
run legacy cleanup automatically.

## Legacy skill links

```bash
./scripts/cleanup-legacy-links.sh --agent all --dry-run
./scripts/cleanup-legacy-links.sh --agent all
```

The cleanup tool has three options: `--agent` (Codex by default), `--dry-run`,
and `--help` (`-h`). It only unlinks exact checkout-owned historical targets,
including dangling links. It preserves foreign links, ordinary directories,
shared skills CLI installations and lock files, global instructions, learning
data, and the checkout. A moved checkout cannot establish ownership of links
pointing to its old path.

Custom homes use the same environment variables as [installation](../../README.md#global-instructions):
`CODEX_HOME`, `CALIBRATION_GROK_HOME`, and `PI_CODING_AGENT_DIR`.
There is no `uninstall.sh` compatibility wrapper: the cleanup command never
represented a complete uninstall of global instructions or shared skills.

After inspecting and cleaning old links, install the desired skills through
`skills add`; see the [quick start](../../README.md#quick-start).

## Repository name and managed markers

The repository is now `FuqingZh/skills`. Existing checkouts can update their
origin URL without moving the checkout directory:

```bash
git remote set-url origin git@github.com:FuqingZh/skills.git
./install.sh --agent all --dry-run
./install.sh --agent all
```

Installation backs up a valid `calibration:begin/end` block and migrates it to
`FuqingZh/skills:begin/end`, preserving all text outside the block. No force is
required for this migration. Old and new blocks together, mismatched pairs,
nested blocks, and malformed markers stop the entire selected-target preflight.
Repeated installation of a current block creates no backup.

Skills keep their own names and installation directories. To migrate recorded
sources, explicitly re-add the four skills under the new repository address;
review installed edits first because add can overwrite them:

```bash
skills add FuqingZh/skills --skill calibration writing-code-docs closeout retrospect -g -a codex pi grok
```

This records the new source through the upstream CLI rather than hand-editing its
lock. Private `calibration/AGENTS.md` paths and `CALIBRATION_GROK_HOME` stay unchanged.
Historical URLs and evidence retain their original names. Keep the existing
checkout path until any legacy link cleanup is complete; renaming the GitHub
repository does not establish ownership of links pointing at a moved checkout.

## Unmarked Codex instructions

An existing unmarked Codex regular file stops installation by default:

```bash
./install.sh --agent codex --force --dry-run
./install.sh --agent codex --force
```

Force requires a successful, verified backup before replacement. Recover personal
rules from the backup outside the new block. Malformed blocks, symbolic links,
and directories still stop even with force. All changes to existing regular
files are backed up; unchanged files create no backup.

## Retired interfaces

Before the first versioned release, the interface was reduced to installation
and explicit legacy cleanup. `--codex-home`, `--grok-home`, and `--pi-home` are
replaced by the environment variables above. `--no-backup` is removed; backups
are mandatory. `--skills-only`, `--instructions-only`, and `--profile` remain
retired. These options fail without writing rather than silently changing scope.
