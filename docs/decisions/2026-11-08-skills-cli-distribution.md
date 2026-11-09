# Skills CLI distribution and global instructions

Status: accepted; implementation pending release.

## Ownership

Upstream skills CLI owns skill add/update/remove and its lock format. FuqingZh/skills
owns four first-party skills and global instructions. `install.sh` manages only
global blocks; `scripts/cleanup-legacy-links.sh` only removes confirmed checkout-owned legacy links.
Setup owns personal source selection and tool declarations. Its independent
`skills` bootstrap profile prepares tools and attaches the native global lock;
restoration and updates use explicit upstream `skills update -g` commands.
Neither the fish nor Pi profile attaches skill state. No second manifest or
custom add/remove/restore wrapper is maintained.

Codex, Pi, and Grok use the same global block delimiters. An unmarked Codex file
requires explicit force and a verified backup before replacement. Foreign links,
ordinary skill directories, private learning data, and malformed global files
are preserved. The [README](../../README.md) owns commands and migration details.

The active distribution is `calibration`, `writing-code-docs`, `closeout`, and
`retrospect`. Patched `teach` and `grilling` are archived unchanged. Matt grilling
is selected directly from upstream, accepting its invocation policy, batched
questions, and subagent assumptions. Existing behavioral cases and historical
evaluations remain unchanged.

The executable Bash installer exposes `--agent`, `--dry-run`, `--force`, and
`--help`. Existing changed files always receive verified backups. Custom homes
use `CODEX_HOME`, `CALIBRATION_GROK_HOME` (script-only), or `PI_CODING_AGENT_DIR`.
Legacy cleanup has only agent selection, dry-run, and help; it is documented as
a migration tool. No packaged CLI or compatibility wrapper is introduced.
Setup keeps bootstrap for environment and native-state attachment. Its skills
profile does not run updates, repair discovery links, or remove untracked
content. Development checks run their test files directly.

## Repository identity and marker compatibility

The collection is named `FuqingZh/skills`; `calibration` remains a skill and a
private configuration namespace. Global blocks use `FuqingZh/skills:begin/end`.
The installer recognizes valid legacy `calibration:begin/end` pairs, backs them
up, and migrates them without force. Mixed namespaces, duplicate blocks, and
mismatched pairs fail before any selected target is changed. Historical source
names remain intact. See the [migration guide](../migrations/skills-cli.md).

## Versions and evidence

One repository version covers the distribution, templates, and installer. See
[release policy](../releases.md). Setup keeps rolling tool declarations and Matt's
default branch. `skills update` follows a recorded ref rather than selecting the
next semantic release. CLI 1.7.6 was tested with `owner/repo#ref` syntax.

An isolated preliminary probe exercised source discovery, commit installation,
tag pinning, explicit upgrade/rollback, update, removal, invalid refs, and native
Codex/Pi/Grok discovery without model calls. Global instruction fixtures remained
unchanged. Repeated add overwrites and same-name removal deletes shared content;
these normal semantics require explicit usage rather than a custom package manager.

Those probes do not establish model-driven grilling behavior, subagent compatibility,
or complete new-machine recovery. New installer safety tests cover filesystem
contracts; static checks do not establish behavioral improvements. This decision
supersedes installation mechanics in the earlier multi-client decision, whose
historical evidence remains available.
