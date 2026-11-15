# Task Traces And Retros

Use when the user asks to persist a confirmed task-level lesson from retrospect.
Record expectation versus outcome, the consequential delta, and the action that
should change next time. Routine investigation notes remain with their owning
task; this contract does not turn them into retrospectives or require a new
permanent rule for an omission already covered by existing guidance.

## Placement And Evidence

Follow repository-local retrospective rules. Otherwise use `.retrospect/`
and lowercase kebab-case filenames:

```text
YYYYMMDD-topic-retro.md
```

Name the actual task or failure pattern rather than an agent, thread, or person.
Keep existing records and links, including `.traces/` material, in place;
no bulk migration is required. Cite evidence held by another task or skill
rather than copying it into the retrospective's directory.

Reference git history, session logs, command history, test artifacts, product
logs, and formal artifacts instead of copying reconstructable raw history.
When additional evidence cannot be reconstructed from those sources, use the
repository's evidence location, falling back to `.retrospect/evidence/`. Keep
that fallback out of Git unless repository-local policy explicitly permits a
narrow evidence file. Follow repository policy for committing retrospectives;
absent a policy, keep them local pending publication review. A hidden directory
does not provide privacy or publication rights; apply appropriate access
controls to sensitive material.

Create only the files and directories needed for the requested record. Do not
scaffold `.retrospect/raw/` or `.retrospect/tmp/`, or require a trace for small edits,
direct answers, simple test runs, or routine low-risk changes.

## Record

Use concise sections that preserve the judgment signal, not a transcript. The
record should let the next similar task start from a better assumption,
validation path, or action. The following fields are a starting template; follow
the repository's format when it supplies one.

```markdown
# <Task Title>

Date:
Project:
Status:

## Expected

- Goal:
- Risk:
- Validation plan:
- Key assumptions:

## Actual

- Changes:
- Validation and evidence locations:
- Result:

## Delta

- Underestimated:
- Overestimated:
- Surprise:
- Remaining hypotheses and verification gaps:

## Action To Carry Forward

- Future action:
- Promotion destination, if warranted:
```

## Navigation And Promotion

When a collection needs navigation, keep its README or index a short map of
important retros, repeated patterns, promoted observations, and open hypotheses.
Under the fallback layout, use `.retrospect/index.md` for that map; do not maintain
a second archive in it.

Stable project contracts and validation rules belong in project documentation;
repository workflow exceptions belong in local instructions or docs;
cross-project engineering judgment may belong in calibration. Promotion needs
the separate authorization required by retrospect. Once promoted, retain the
retrospective as evidence and make the promoted location the source of truth.
