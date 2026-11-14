# Changelog

## Unreleased

- Add `plainspoken` for substantive natural-language expression and `dissect`
  for in-depth analysis, with English instructions and implicit invocation metadata.
- Move the shared global template to `templates/AGENTS.md.template` and reduce
  it to three routes: `plainspoken`, `dissect`, and `calibration`. Install the
  skills before refreshing global instructions.
- Remove private host-profile discovery and path rendering from the installer;
  retain client-home selection, backups, marker migration, and idempotent updates.
- Consolidate calibration's completion route and engineering-discipline entry,
  remove unsolicited retrospective suggestions and duplicate expression guidance,
  and keep environment and workspace boundaries in their relevant references.
  These rules now depend on task-based skill selection.
- Make verification routing conditional on implementation, delivery, or contract
  evidence needs. Keep material evidence and risk reporting while removing fixed
  opening statements, generic checklists, and duplicate permission rules. Align
  the discipline index with this verification scope.
- Focus refactoring guidance on preserved contracts, scoped transition cleanup,
  intentional compatibility entrypoints, and regression evidence. Preserve
  historical records and frozen evidence during reference cleanup.
- Keep debugging environment checks relevant to the observed failure and apply
  completion verification when claiming a fix or verified runtime outcome.
- Remove the general agent/workflow evaluation reference and its dedicated
  calibration trigger and routes. Keep experiment-specific protocols and frozen
  evidence; pin the historical ablation plan's reference to its registered baseline.
- Focus harness guidance on evidenced capability gaps, repository ownership,
  bounded delivery, and authorization. Remove the shared Ruff recipe, terminal
  deployment recipe, and fixed orchestration adoption gate; retire their dedicated
  prompt cases and the stale evaluation case without altering frozen studies.
- Remove the single-target design index and route directly to codebase design
  guidance. Consolidate design judgments, retain wrappers with clear roles and
  long-lived parallel interfaces, and scope verification to implemented changes.
- Retire the mandatory principles bundle. Keep core decision framing in the skill
  and place design, process, documentation, and verification guidance with their
  topic owners; remove universal seed and trace-directory defaults from the bundle.
- Add synthetic behavioral prompts and static packaging checks. These checks
  do not establish English-version answer quality or reliable model routing.

## 1.0.0 — 2026-11-09

First repository-level versioned distribution.

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
- Provide English and Simplified Chinese README entrypoints, with both covered
  by Markdown lint and link validation.

See [migration instructions](README.md#legacy-migration) and
[release policy](docs/releases.md). These lifecycle changes do not establish
improved model behavior or compatibility for upstream grilling's subagents.
