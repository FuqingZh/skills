# Code-first minimal documentation model

Date: 2026-11-24
Status: Accepted

## Context

Both `skills/calibration/references/docs/` (12 files, 8 fallback directories,
10 document types, `YYYYMMDD-vMAJOR.MINOR-topic-kind.md` filenames) and this
repository's own `docs/` (92 files across `archive/`, `decisions/`,
`implementation-plans/`, and `testing/`) accumulated heavy scaffolding from
earlier pre-indexing agent workflows. That structure duplicated facts owned by
code, tests, CI, and Git history, and polluted `HEAD` search surfaces with
retired AO, Symphony, and historical plan prose (full prior state preserved at
`v2.1.0` and commit `2a552d4`).

## Decision

- Consolidate cross-project documentation guidance into a single concise
  reference,
  [`skills/calibration/references/docs/project-layout.md`](../../skills/calibration/references/docs/project-layout.md),
  removing the 11-file `document-types/` tree.
- Adopt a code-first documentation boundary: code, types, schemas, tests, and
  CI own current behavior and verification; durable docs hold only non-derivable
  decisions (`docs/adr/`), outside-the-code facts (`docs/<topic>.md` on demand),
  and human/agent entrypoints (`README.md`, `AGENTS.md`).
- Keep implementation plans ephemeral (conversation, native tasks, PRs, or
  local working notes) and rely on Git history as the archive instead of
  maintaining `docs/archive/`, `docs/implementation-plans/`, or dated
  `docs/testing/` logs.
- Compact superseded decisions into the replacing ADR's rejected-alternatives
  section with a Git reference (commit, tag, or PR) and delete the superseded
  file from `HEAD` so every file in `docs/adr/` remains active truth.

## Rejected Alternatives

- **10-type Diátaxis/enterprise document taxonomy (`document-types/`)**:
  Encouraged prose architecture mirrors, static test matrices, and permanent
  planning folders that drifted from code (`2a552d4`).
- **Keeping `docs/archive/` and `Status: Superseded` files on `HEAD`**:
  Polluted agent search/grep context with retired terminology and required
  special linter/link exclusions and hash-preservation tests (`2a552d4`).
- **Keeping dated `docs/testing/` pilot reports on `HEAD`**: Deterministic test
  results belong to `tests/` and CI; non-deterministic experiment takeaways
  belong compacted inside the owning ADR, while full historical runs remain
  recoverable via Git tags (`v2.0.0`, `v2.1.0`).

## Consequences

- `skills/calibration/references/docs/` shrinks from 12 files to 1, and
  repository `docs/` holds only active contracts and 4 live ADRs.
- Removing published `references/docs/document-types/` paths is a breaking
  reference change under [`docs/releases.md`](../releases.md) for the next
  major release.

## Reopen When

- External compliance or permanent-URL obligations require keeping frozen
  superseded files directly on `HEAD`.
- A project grows a distinct multi-document external reference surface that
  requires dedicated subdirectory navigation.
