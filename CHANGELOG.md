# Changelog

## 1.0.0 — unreleased

First repository-level versioned distribution; no tag has been published yet.

- Rename the repository to `FuqingZh/skills`; preserve skill names, private
  calibration configuration, and historical provenance.
- Emit `FuqingZh/skills:begin/end` global markers and migrate valid legacy
  `calibration:begin/end` blocks with backups. Reject mixed or mismatched markers.
- Distribute `calibration`, `writing-code-docs`, `closeout`, and `retrospect`
  through upstream skills CLI.
- Limit `install.sh` to global instructions, with managed blocks for Codex,
  Grok Build, and Pi. Preserve block-external text and ordinary refresh backups.
- Require explicit `--force` and a verified backup for replacing an unmarked
  Codex regular file. Reject malformed blocks and nonregular targets.
- Keep `./install.sh` as the executable Bash entrypoint with four options:
  `--agent`, `--dry-run`, `--force`, and `--help`. Existing changed files are
  always backed up; custom homes use environment variables.
- Retire `--skills-only`, `--instructions-only`, `--profile`, `--no-backup`,
  and the three `--*-home` options with explicit errors.
- Add ownership-limited `scripts/cleanup-legacy-links.sh` for legacy links.
  Normal installation performs no skill cleanup; no uninstall wrapper is kept.
- Archive patched `teach` and `grilling` with byte-integrity manifests and
  historical provenance. Upstream Matt grilling is an independent user choice.

See [migration instructions](README.md#legacy-migration) and
[release policy](docs/releases.md). These lifecycle changes do not establish
improved model behavior or compatibility for upstream grilling's subagents.
