# Repository releases

FuqingZh/skills uses one SemVer version in `pyproject.toml`, one Git tag `vX.Y.Z`,
and one release-notes entry in [CHANGELOG.md](../CHANGELOG.md). The version covers
all first-party skills, references, global templates, and installer interfaces.
There are no per-skill versions and no published Python or npm skill package.

Breaking installation, invocation, or documented consumer contracts require a
major release. Backward-compatible capabilities use a minor release; corrections
that preserve those contracts use a patch release. Prompt changes still need
scope-appropriate behavioral evidence for behavioral claims.

The first versioned distribution is **1.0.0 (2026-11-09)**. Earlier commits remain
available by full SHA. Publication is a separate authorized action: update the
version and release notes, run the repository gate and current-head review, then
tag that reviewed commit and publish matching release notes. Do not move tags.
No tag or release is created by installation or bootstrap.

The [v2 migration guide](migrations/v2.md) covers the six-skill router, removed
reference paths, private-host routing change, and historical runtime retirement.
The frozen v2.0 evidence snapshot remains available at tag `v2.0.0`
(`docs/testing/20261117-v2.0-release-evidence-summary.md`).

With skills CLI 1.7.6, use `owner/repo#ref` for a tag or full commit. A pinned
installation stays on that ref during `skills update`. Upgrade or rollback with
an explicit `skills add` of the selected ref, accepting replacement of installed
content. Check CLI help when changing CLI versions; newer upstream documentation
may describe syntax absent from the installed release.

Global instructions are refreshed separately by running `install.sh` from the
same selected release checkout. Review the backup and personal text during a
Codex legacy migration. Release pinning does not cover client versions, model
behavior, personal settings, or external skill sources.
