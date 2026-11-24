# Changelog

## 2.1.0 — 2026-11-17

Adopt the concise explanation-first guidance. Skill names, discovery metadata,
reference paths, installer interfaces, and the global router are unchanged.
This changes analytical defaults; consumers expecting proactive objections
should review the new wording before upgrading.

### Changed

- Replace proactive objection and correction guidance in `plainspoken` and
  `dissect` with an explicit prohibition on model-added rebuttals, acceptance
  warnings, and proof demands. Preserve source attribution, source-internal
  disagreements, and accurate failure and permission reporting.
- Remove the actor-profile counterexample instruction and update static
  contract checks to the adopted behavior.

### Evaluation

- Record a [15-generation explanation-framing pilot](https://github.com/FuqingZh/skills/blob/v2.1.0/docs/testing/20261117-explanation-framing-pilot.md)
  across GPT, Qwen, Grok, and DeepSeek. Results vary by model and context;
  adoption follows user preference, not demonstrated general quality gains.
  Private inputs and outputs are not published.
  Eight fresh follow-up generations compare the longer prohibition with its
  concise replacement; outcomes remain mixed.
- Record a [repeated cross-task pilot](https://github.com/FuqingZh/skills/blob/v2.1.0/docs/testing/20261117-explanation-transfer-pilot.md):
  48 attempts, including incomplete answers and provider/harness failures;
  no demonstrated stable improvement or general regression.

## 2.0.0 — 2026-11-17

Six first-party skills, a minimal global router, and consolidated engineering
references. This is a major release because published reference paths, global
instruction behavior, and historical execution entrypoints have changed.
See the [v2 migration guide](docs/migrations/v2.md) before upgrading.

### Added

- `plainspoken` for substantive natural-language expression and `dissect` for
  in-depth analysis, with English instructions and task-specific references.
- A [release evidence summary](https://github.com/FuqingZh/skills/blob/v2.0.0/docs/testing/20261117-v2.0-release-evidence-summary.md)
  linking measured repository reductions, original human feedback, comparisons,
  failed attempts, and untested boundaries.
- A dedicated [installation reference](docs/installation.md), reached from the
  simplified English and Chinese READMEs.

### Changed

- Move the shared template from `codex/AGENTS.md.template` to
  `templates/AGENTS.md.template`. It now contains only three skill routes:
  `plainspoken`, `dissect`, and `calibration`. Install skills before refreshing it.
- Make calibration routing conditional on the task. Consolidate substantive
  ownership across naming, design, verification, debugging, workspace ownership,
  document types, and project layout; defer to repository and consumer contracts.
- Simplify document guidance without compulsory planning stages or document
  bundles. Use the stable `references/docs/project-layout.md` entrypoint.
- Keep Ruff defaults with linter guidance and diagnostic exceptions with
  verification. Retain narrow authorization, review, and runtime-release boundaries.
- Separate formal project documents, task working material, and requested
  retrospectives. Scope retrospective depth to evidence-comparison needs and
  dissect's future-path analysis to forecasting questions.
- Clarify code-documentation conventions and distinct caller-facing examples;
  retain disclosure of material behavior and contract gaps.
- Remove duplicate OpenAI display metadata and default prompts. Only closeout
  and retrospect retain `agents/openai.yaml`, enforcing explicit invocation;
  validators check supplied metadata and effective cross-client invocation policy.

### Breaking changes and retirement

- Stop discovering or rendering private host-profile paths in the installer.
  Existing private files and text outside managed blocks remain untouched.
- Remove superseded guidance, compatibility pointers, and forwarding anchors.
  External consumers must update links using the migration guide; no compatibility
  stubs remain. Historical snapshots and frozen evidence retain their original bytes.
- Retire `scripts/run_writable_agent_eval.py` and
  `scripts/run_progressive_validation_selection_eval.py` with their dedicated
  runtime tests. Preserve all 20 original source files as byte-identical text in
  the [runtime archive](evaluations/archive/writable-agent-runtime/README.md),
  with independent evidence and provenance checks. Runtime compatibility failures
  were retired, not repaired.

### Validation and evidence

- Preserve installer home selection, verified backups, marker migration,
  foreign-file protections, idempotency, and isolated preview behavior.
- Isolate OpenEvals test scratch directories from local development environments.
  Keep required coverage thresholds and CI protections unchanged.
- The evidence snapshot reports 591 passing tests and 100% line coverage of
  maintained Python tools. Final-package answer-quality, native routing, cost,
  and latency improvements have not been established. Early writing feedback is
  scoped to its frozen candidates; static checks are not model-quality evidence.

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

See [migration instructions](docs/migrations/skills-cli.md) and
[release policy](docs/releases.md). These lifecycle changes do not establish
improved model behavior or compatibility for upstream grilling's subagents.
