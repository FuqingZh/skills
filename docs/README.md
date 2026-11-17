# FuqingZh/skills Documentation

The skills collection is in stable maintenance mode. This index separates current
authority, recorded open work, and historical evidence.

## Start Here

1. Read the repository README ([English](../README.md) / [简体中文](../README.zh-CN.md))
   for the project overview and quick start; [installation](installation.md)
   owns installer options and managed-file behavior.
2. Use the [calibration router](../skills/calibration/SKILL.md) to select reusable
   references; use the [document-type router](../skills/calibration/references/docs/document-types/README.md)
   for a document's minimum contract and the layout reference for project organization.
   Shared locations are fallbacks for projects without local conventions;
   this repository keeps its existing document paths.
3. Follow [AGENTS.md](../AGENTS.md) for repository validation and contribution rules.

## Public Architecture

Reusable references live inside the owning skills, which provide model
interaction entrypoints. Repository tools own setup and validation. The shared
[global template](../templates/AGENTS.md.template) only routes to skills; the
public package does not discover private host configuration or provide an
orchestrator integration.

Skill instructions and trigger descriptions live in `SKILL.md` and its referenced
files. First-party `agents/openai.yaml` files contain only the Codex explicit-only
policy needed by closeout and retrospect; the other four skills omit the file.
The validator accepts optional metadata and checks supplied fields and effective
invocation policy against repository and cross-client contracts. Codex defaults
to implicit invocation when the policy is absent; see the
[official skill configuration](https://developers.openai.com/codex/skills).

## Current Authority

| Need | Source |
| --- | --- |
| Project overview and quick start | [README](../README.md) |
| Installer contract | [Installation reference](installation.md) |
| Cross-project judgment and routing | [Calibration skill router](../skills/calibration/SKILL.md) |
| Substantive natural-language expression | [Plainspoken skill](../skills/plainspoken/SKILL.md) |
| In-depth explanation and prediction | [Dissect skill](../skills/dissect/SKILL.md) |
| Repository capabilities, instructions, and continuation/review boundaries | [Harness](../skills/calibration/references/discipline/harness.md) |
| Linter selection and rule defaults | [Linters](../skills/calibration/references/linters/README.md) |
| Execution scope, workspace ownership, and runtime release | [Workspace ownership](../skills/calibration/references/discipline/workspace-ownership.md) |
| Completion, external-result evidence, and diagnostic exceptions | [Verification](../skills/calibration/references/discipline/verification.md) |
| Document layout and lifecycle | [Project documentation layout](../skills/calibration/references/docs/project-layout.md) |
| Durable implementation-plan contract | [Implementation plans](../skills/calibration/references/docs/document-types/implementation-plan.md) |
| Explicit conversation closeout | [Closeout skill](../skills/closeout/SKILL.md) |

The installer and skill sources define active behavior. Adoption rationale,
completed comparisons, and superseded protocols are indexed in the
[historical records](archive/README.md), with their original evidence limits.
Completed evaluations do not establish general model or cross-client quality.

The [skills CLI transition](decisions/2026-11-08-skills-cli-distribution.md)
supersedes the installer mechanics in the earlier multi-client decision.
[Release policy](releases.md) owns repository versioning.

[External design sources](sources.md) records borrowed ideas, pinned references,
and evidence limits; experimental results remain with their protocols.

## Recorded Open Work

- [Communication-style preference optimization](implementation-plans/communication-style-preference-optimization.md):
  five-check judge calibration, reserved human evaluation, then paragraph comparison.
- [Project docs convergence](implementation-plans/20260805-v1.0-project-docs-architecture-convergence-implementation-plan.md):
  local slices are complete; the recorded downstream owner migration remains
  pending. This index does not verify another repository's current state.
- [Body compression trial](decisions/2026-09-20-calibration-body-compression-and-routing.md):
  historical adoption evidence is retained; current guidance follows the skill
  router. Metadata candidates and real-work performance remain unverified.
- [Coding-protocol retirement trial](decisions/2026-09-07-coding-protocol-runtime-retirement-trial.md):
  the runtime entry remains retired; retained source supports restoration.

## Release Evidence

The [v2.0 candidate evidence summary](testing/20261117-v2.0-release-evidence-summary.md)
compares repository size with v1.0.0 and separates historical human preferences,
model comparisons, engineering checks, and unmeasured final-package behavior.
It is a pre-release report, not a release or a new evaluation run.

## Validation

[AGENTS.md](../AGENTS.md#validation) owns proportional check selection and the
complete gate; `pdm.lock` owns validation dependencies. The existing PDM tasks
remain the local and CI entrypoints. The [check-routing assessment](decisions/20261011-v1.0-check-routing-and-nx-decision-record.md)
records why Nx is not adopted in this cleanup.

## Historical Evidence

Use the [archive index](archive/README.md) for completed plans, corrected or
superseded comparisons, adoption decisions, and old AO guidance. Raw evidence,
manifests, hashes, provenance, and compatibility cleanup remain preserved.

The historical Codex writable-agent executor and progressive-validation controller
are [retired](../evaluations/archive/writable-agent-runtime/README.md).
Their source snapshots and independent evidence checks remain available.
