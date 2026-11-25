# Project Documentation

Use when deciding whether a fact belongs in project documentation, where it
lives, and what contract it must preserve. Follow repository-owned documentation
contracts and existing paths; this guidance fills gaps when none exist.

## Code First

Treat code, types, schemas, executable tests, and CI as the source of truth for
current system behavior and verification. Do not maintain prose mirrors of
module structure, API details, or test matrices that code or CI already owns.

Persist durable documentation only for information that code cannot reliably
convey:

- **Why a choice was made**: architecture or product decisions, rejected
  alternatives, constraints, and reopening conditions.
- **Facts outside the codebase**: third-party compatibility quirks, reproducible
  empirical benchmarks, and controlled operational procedures.
- **Human and agent entrypoints**: repository onboarding (`README.md`) and
  operational maps (`AGENTS.md`, see the
  [AGENTS.md contract](../discipline/harness.md#agentsmd-contract)).

## Minimal Fallback Structure

Create only the files and directories needed; do not pre-create empty folders.

- `README.md` for human entrypoints; `AGENTS.md` when repository-specific agent
  routing adds value.
- `docs/adr/` as the default directory for Architecture Decision Records (ADRs)
  when no local decision path exists.
- Flat `docs/<topic>.md` files for genuine outside-the-code references (such as
  compatibility facts, benchmarks, runbooks, or external-user guides). Group
  into subdirectories only when file count warrants navigation.
- Keep implementation plans and proposals ephemeral (in conversation, native
  task state, PR descriptions, or local working notes). Do not treat completed
  plans as permanent authority.
- Rely on Git history as the archive. Do not maintain a `docs/archive/`
  directory unless an external publication or audit contract requires frozen
  files on `HEAD`.

## Core Contracts

- **ADR (`docs/adr/`, Markdown)**: Record date, status, context, viable
  rejected alternatives, chosen decision and consequences, and conditions for
  reopening. When a new decision replaces an old one, compact the reason the
  old choice was abandoned into the replacing ADR with a Git reference (commit,
  tag, or PR) and remove the superseded file from `HEAD`.
- **External compatibility and empirical records**: Name the external boundary,
  versions, environment, and inputs; distinguish stated contracts from observed
  behavior; cite reproducible checks and evidence paths (consult
  [verification discipline](../discipline/verification.md) for benchmark
  evidence and fallback seed defaults); state limitations and revalidation
  conditions. Keep one current summary updated in place for active benchmarks
  instead of accumulating dated run logs; fold negative or one-off experiment
  takeaways into the owning ADR.
- **Runbooks** (only for controlled or production-adjacent operations): State
  owner, prerequisites, access requirements, ordered checkpoints, verification,
  recovery, rollback, escalation, and stop conditions. Keep secrets and private
  host state out of public documents.

## Naming And Working Material

Use lowercase kebab-case filenames without embedded version numbers:
`YYYY-MM-DD-topic.md` (or sequential numbering when locally adopted) for ADRs,
and stable undated names for current reference documents.

Investigation notes belong to the owning task. Follow repository task-record
locations or the user's destination; otherwise keep them local and untracked
(for example under `.calibration/notes/`, with extra non-reconstructable
evidence under `.calibration/evidence/`). Reference reconstructable Git
history, sessions, test outputs, and logs instead of copying them. Do not
commit working notes or evidence unless repository policy or the user
explicitly permits it. Hidden paths do not provide privacy or publication
rights; apply appropriate access controls to sensitive material.

Formal project documents remain project-owned regardless of which skill helped
write them. One-off observations need not be persisted automatically.
