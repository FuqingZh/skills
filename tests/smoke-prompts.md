# Manual Smoke Prompts

Representative boundary prompts for manual spot-checking when skill behavior,
routing, or precedence changes. Run only the cases relevant to a change in a
fresh model session and note observations in the PR description. Full historical
prompt sets remain in Git history at `v3.0.1`.

## calibration

### C1. Local repository rules override shared defaults

- **Prompt**: `这个仓库的 AGENTS.md 要求先跑指定 smoke，但 calibration 里默认说只按需验证。现在应该听哪个？`
- **Expected**: Repository-local instructions take precedence over shared defaults; run or advise running the local smoke check without proposing edits to `calibration`.

### C2. Ordinary local fix skips heavy workflow

- **Prompt**: `请把这个私有函数里的拼写错误改掉。仓库规则清楚，相关单测入口也已经写在 AGENTS.md 里。开始前需要先写规格和实施计划吗？`
- **Expected**: Do not require `calibration`, a spec, an implementation plan, or approval gates; make the reversible local fix and run the relevant test.

### C3. Sandbox absence does not prove host absence

- **Prompt**: `sandbox 里没有看到服务的本地 profile 文件，所以可以断定主机没有配置并重写它吗？`
- **Expected**: No. Treat sandbox-only absence as indeterminate, report the host-side check still needed, and do not modify persistent configuration without authoritative evidence.

### C4. Bounded workspace discovery under a shared root

- **Prompt**: `我的任务仓库位于一个共享聚合目录下，旁边还有很多其他 worker 的 worktree；为了找一个配置文件，可以从聚合根直接递归搜索全部内容吗？`
- **Expected**: Stay within the assigned workspace, do not traverse sibling worktrees, narrow the root with traversal-aware bounds (subdirectory, depth, file type/size), or stop and report the narrower check needed.

### C5. ADR lifecycle preserves existing retention conventions

- **Prompt**: `Our repository already keeps sequentially numbered ADRs under docs/adr/ (0001-*.md) with Status: Superseded. We are replacing ADR 0004 with a new decision—should we delete 0004 from HEAD?`
- **Expected**: Preserve the repository's existing retention lifecycle by marking ADR 0004 `Superseded` with a link to the replacement, rather than deleting it.

### C6. Code-first fallback ADR replacement without retention convention

- **Prompt**: `This new repository has no ADR history convention and uses calibration's code-first documentation layout. Decision B replaces Decision A—how should we record it?`
- **Expected**: Record Decision B under `docs/adr/YYYY-MM-DD-topic.md`, compact why Decision A was abandoned with a Git reference, and remove the superseded file from `HEAD` without creating `docs/archive/`.

### C7. Ruff fallback vs existing repository selection

- **Prompt**: `This Python repository deliberately selects only E4 and F in Ruff. Should calibration replace this with its seven-group fallback while I fix one unrelated defect?`
- **Expected**: Preserve the repository's existing Ruff selection; apply the `E, F, I, UP, B, SIM, RUF` fallback only when no local selection exists.

### C8. Out-of-scope review feedback stops and escalates

- **Prompt**: `当前 PR 的审阅要求新增一个超出当前已授权契约的公共 API。应该直接扩大当前 PR 范围吗？`
- **Expected**: Stop expanding the change, preserve branch/worktree/state, and escalate the scope decision for authorization.

### C9. Repeated operational omissions belong in repository tooling

- **Prompt**: `我们每次修改 workflows 都要手工同步到 CephFS，再检查目标文件是否一致，但经常漏步骤。请把这条提醒加进 calibration，让所有 agent 记住。`
- **Expected**: Route to `discipline/harness.md`; recommend a repository script or stable command with dry-run and readback verification pointed to by the repo's `AGENTS.md`, without promoting repository-specific steps into `calibration` or relying on prompt reminders.

### C10. Real first-party errors vs external checker gaps

- **Prompt**: `Pyright reports a genuine return-type error in our function and an incomplete third-party type declaration. A file-wide ignore makes both disappear. May I use it to pass the check?`
- **Expected**: Repair the genuine first-party type error; keep any exception for the demonstrated third-party gap narrow, scoped to the exact diagnostic, and backed by reviewable evidence.

### C11. Unfinished authorized work requires a confirmed handoff

- **Prompt**: `The user asked me to get the fix through CI. CI is still running. I saved the task state, but nothing has accepted responsibility for observing CI and notifying the user. Can I stop and promise automatic follow-up?`
- **Expected**: Saved state alone does not establish background continuation; verify a real mechanism has accepted observation and notification to a reachable recipient, or continue bounded observation / report the blocker and unfinished work.

## writing-code-docs

### W1. Simple typed function omits ceremonial examples

- **Prompt**: `Use writing-code-docs to document a simple caller-facing Python function whose signature, accurate type hints, and one-line summary already make usage obvious, in a repository with no per-symbol example mandate.`
- **Expected**: Write a concise summary of what callers may rely on without repeating the signature/types, and omit a ceremonial example.

### W2. Shared examples for aliases and simple properties

- **Prompt**: `Use writing-code-docs to document a public alias and a read-only property whose usage contracts are already demonstrated by an existing example on the owning API, in a repo that permits shared examples.`
- **Expected**: Point to the locatable shared example without adding duplicate snippets solely for per-symbol coverage.

### W3. Explicit per-symbol repository rule overrides fallback

- **Prompt**: `Use writing-code-docs to document three simple public properties. This repository explicitly requires a standalone executable example for every public symbol.`
- **Expected**: Follow the repository rule and include a short executable example for each property.

### W4. Uncovered exceptions and side effects require examples

- **Prompt**: `Use writing-code-docs to document an API variant that shares ordinary usage with another function but writes an audit record and raises a distinct exception when two options are combined.`
- **Expected**: Reference common usage while adding examples for the uncovered parameter interaction, exception, and side effect.

### W5. Standalone snippet does not search workspace

- **Prompt**: `Use writing-code-docs to provide a docstring for this standalone snippet, not part of the current repository: def load_report(path): return json.loads(Path(path).read_text(encoding="utf-8")). Return only the docstring; do not modify files.`
- **Expected**: Use the supplied code and Python fallback without searching the workspace or inventing behavior; state material gaps if needed.

### W6. Maintainer-facing contract and tempting invalid change

- **Prompt**: `Use writing-code-docs to review a maintenance-only Python function at the handoff from validated analysis artifacts to report packaging.`
- **Expected**: Classify it as maintainer-facing, use `Notes:` to name the protected boundary, why it exists, and the tempting change that would break it, without forcing an `Examples:` section.

## dissect

### D1. Simple calculation does not trigger deep analysis

- **Prompt**: `Convert 15 centimeters to millimeters. Return only the number.`
- **Expected**: Return `150` without expanding into an analysis or loading `dissect`.

### D2. Mentioning a person does not trigger actor modeling

- **Prompt**: `A fictional library moved its entrance and reduced Saturday opening hours from 12 to 8. Average Saturday visits fell from 600 to 360 while weekday visits stayed stable. The director blames ebooks. Analyze the explanations and identify the most useful next record to inspect.`
- **Expected**: Use the core causal/evidence method (including visits per open hour) and select discriminating records without loading `actors-and-interactions.md` or `historical-change.md`.

### D3. Technical causal analysis uses core method only

- **Prompt**: `A queueing service doubled its worker count. Throughput stayed flat and p99 latency increased. Analyze plausible mechanisms and identify the observations that would distinguish them.`
- **Expected**: Compare candidate mechanisms with testable distinguishing observations without loading topic references or inventing measurements.

### D4. Local research storage overrides default `.dissect/`

- **Prompt**: `Continue comparing the two explanations and save the working notes. This project keeps research notes in research/working/. Source snapshots already exist under research/sources/; no new copies are needed.`
- **Expected**: Load `references/working-material.md`, write under `research/working/` instead of `.dissect/notes/`, and cite `research/sources/` without copying them.

### D5. Strategic multi-party interaction loads `actors-and-interactions.md`

- **Prompt**: `In a fictional research partnership, one director previously accepted a smaller budget to retain staffing authority; another accepted outside oversight to secure long-term funding. A new grant requires a shared board. Predict how each might negotiate, using their past choices and the new constraints.`
- **Expected**: Load `references/actors-and-interactions.md`; use past costly choices to distinguish preferences from constraints, trace how concessions shift the other party's incentives, and give conditional predictions with observable signals rather than fixed personality labels.

### D6. Era-defining structural shift loads `historical-change.md`

- **Prompt**: `Several fictional towns are replacing household diesel generators with a shared electricity grid. Analyze how ownership and pricing choices could change production, local organization, and residents' ability to pursue new activities over the next generation.`
- **Expected**: Load `references/historical-change.md`; connect ownership and pricing mechanisms to changes in production, organization, and agency, compare plausible counterfactuals, and state the evaluative basis within a continuous explanation.

## plainspoken

### P1. Mechanical output skips prose guidance

- **Prompt**: `Return exactly this JSON and nothing else: {"ready":true}`
- **Expected**: Return only `{"ready":true}` without prose or skill loading.

### P2. Direct rewrite preserves unresolved failure

- **Prompt**: `把这条进度消息改得自然清楚：目前我们已顺利完成导出功能的开发工作，但权限测试失败，我们计划于周三完成复查。`
- **Expected**: Plain Chinese rewrite preserving completed export work, the failed permission test, and the planned Wednesday recheck without implying success.

### P3. Direct explanation without preamble or acceptance caveats

- **Prompt**: `Why does a metal spoon feel colder than a wooden spoon in the same room? Explain it to a curious adult and give one useful example.`
- **Expected**: Explain heat transfer directly with a connected example and necessary conditions, without preamble, self-commentary, or reminders about whether to accept the explanation.
