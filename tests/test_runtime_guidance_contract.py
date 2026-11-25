from __future__ import annotations

import json
import re
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]


def text(path: str) -> str:
    return (REPOSITORY_ROOT / path).read_text(encoding="utf-8")


def compact(path: str) -> str:
    return " ".join(text(path).split())


def test_public_entrypoints_do_not_discover_private_profiles() -> None:
    for entrypoint in ("templates/AGENTS.md.template", "install.sh"):
        content = text(entrypoint)
        assert "HOST_AUTHORITY" not in content
        assert "HOST_CONFIG_ROOT" not in content
        assert "XDG_CONFIG_HOME" not in content
        assert ".config/calibration" not in content
        assert "calibration/AGENTS.md" not in content

    for root in ("skills", "references"):
        for path in (REPOSITORY_ROOT / root).rglob("*"):
            if path.is_file():
                content = path.read_text(encoding="utf-8", errors="ignore")
                assert ".config/calibration" not in content
                assert "calibration/AGENTS.md" not in content

    for skill_dir in (REPOSITORY_ROOT / "skills").iterdir():
        if skill_dir.name == "calibration" or not skill_dir.is_dir():
            continue
        skill = skill_dir / "SKILL.md"
        if skill.is_file():
            assert "Agent Orchestrator" not in skill.read_text(encoding="utf-8")


def test_shared_aggregation_root_has_behavioral_prompt_coverage() -> None:
    prompts = text("skills/calibration/test-prompts.json")

    assert "共享聚合根下的递归搜索边界" in prompts
    assert "sibling worktrees" in prompts
    assert "traversal-aware bound" in prompts
    assert "file size" in prompts
    assert "concurrency" in prompts


def test_docs_keep_only_active_authority_without_archive_tree() -> None:
    docs = text("docs/README.md")
    assert not (REPOSITORY_ROOT / "docs/archive").exists()
    assert "skills/calibration/SKILL.md" in docs
    assert "adr/" in docs
    for path in (
        "skills/calibration/SKILL.md",
        "skills/calibration/references/discipline/harness.md",
    ):
        assert "docs/archive" not in text(path)


def test_runtime_entrypoints_are_independent_of_retired_integration() -> None:
    for path in (
        "AGENTS.md",
        "templates/AGENTS.md.template",
        "skills/calibration/SKILL.md",
        "skills/calibration/references/discipline/harness.md",
        "skills/calibration/test-prompts.json",
    ):
        current = text(path)
        assert not re.search(r"\bAO\b|agent-orchestrator|using-ao", current)
    assert not (REPOSITORY_ROOT / "scripts/adopt_ao_repository.py").exists()
    assert not (
        REPOSITORY_ROOT
        / "skills/calibration/references/agent-orchestrator-review-continuation.md"
    ).exists()


def test_generic_boundaries_have_reachable_reference_owners() -> None:
    skill = compact("skills/calibration/SKILL.md")
    discipline = compact("skills/calibration/references/discipline/README.md")
    workspace = compact(
        "skills/calibration/references/discipline/workspace-ownership.md"
    )
    verification = compact("skills/calibration/references/discipline/verification.md")
    debugging = compact("skills/calibration/references/discipline/debugging.md")
    assert "references/discipline/README.md" in skill
    assert "references/discipline/harness.md" not in skill
    for reference in (
        "harness.md",
        "debugging.md",
        "workspace-ownership.md",
        "verification.md",
        "../linters/ruff.md",
    ):
        assert f"]({reference})" in discipline
    assert "Implementation or contract verification" in discipline
    assert "| Completion claim," not in discipline
    assert "environment evidence boundaries" in discipline
    assert "workspace search boundaries, or branch/worktree ownership" in discipline
    for rule in (
        "sibling worktree",
        "spawned child processes have exited",
        "traversal-aware bound",
        "rejected filesystem escalation",
    ):
        assert rule in workspace
    assert "Repair real errors in first-party code and interfaces" in verification
    assert "diagnostic suppressions or weaker checker configuration" in verification
    assert "For demonstrated external or checker gaps" in verification
    assert "keep each exception narrow" in verification
    assert "the exact diagnostic, and retain reviewable evidence" in verification
    assert "environment actually observed" in debugging
    assert "before changing persistent configuration" in debugging
    assert "exact check still needed" in debugging
    assert "runtime state implicated by the failure" in debugging
    assert "When claiming a fix or a verified runtime outcome" in debugging


def test_calibration_keeps_verification_without_unsolicited_retrospectives() -> None:
    skill = text("skills/calibration/SKILL.md")
    assert skill.count("references/discipline/verification.md") == 1
    assert "When the task requires implementation or delivery verification" in skill
    assert "$retrospect" not in skill
    assert "continue from the baseline" not in skill
    assert "public or cross-boundary contract claims" in compact(
        "skills/calibration/SKILL.md"
    )
    assert "## Baseline" not in skill
    retired = REPOSITORY_ROOT / "skills/calibration/references/principles.md"
    assert not retired.exists()


def test_calibration_retires_general_evaluation_routing() -> None:
    root = REPOSITORY_ROOT / "skills/calibration"
    assert not (root / "references/discipline/evaluation.md").exists()
    skill = compact("skills/calibration/SKILL.md")
    assert "agent or workflow evaluation" not in skill
    assert "repository harnesses" in skill
    for path in root.rglob("*.md"):
        assert "evaluation.md" not in path.read_text(), path
    assert "discipline/evaluation.md" not in text("docs/README.md")
    harness = compact("skills/calibration/references/discipline/harness.md")
    assert "Evaluate representative behavior separately" in harness


def test_retained_principles_have_task_specific_owners() -> None:
    skill = compact("skills/calibration/SKILL.md")
    design = compact("skills/calibration/references/design/codebase.md")
    harness = compact("skills/calibration/references/discipline/harness.md")
    verification = compact("skills/calibration/references/discipline/verification.md")
    docs = compact("skills/calibration/references/docs/project-layout.md")
    assert "Correct false constraints, abstractions, or requirements" in skill
    assert "Within authorized, reversible local work" in skill
    assert "revise it as feedback changes the evidence" in skill
    for guidance in (
        "established domain parsers",
        "algorithm or consumer boundary",
        "installed version and applicable API",
        "sources inspectable",
        "Preserve tolerated metadata and extension keys",
        "Expose an override only when",
        "Keep caller taste, product defaults, and presentation policy",
    ):
        assert guidance in design
    assert "A code change alone does not require these stages" in harness
    assert "validate outputs as well as runtime" in verification
    assert "seed explicit when it materially affects reproducibility" in verification
    assert "reconstructable reference or an approved evidence location" in verification
    assert "Follow repository-owned documentation contracts and existing paths" in docs
    for path in (REPOSITORY_ROOT / "skills/calibration").rglob("*.md"):
        assert "principles.md" not in path.read_text(), path


def test_verification_scopes_checks_and_reports_to_material_claims() -> None:
    verification = compact("skills/calibration/references/discipline/verification.md")
    harness = compact("skills/calibration/references/discipline/harness.md")
    for guidance in (
        "Discussion of a proposed approach alone does not require delivery checks",
        "smallest relevant checks at a repository-owned validation entrypoint",
        "Broaden only when repository-local policy explicitly requires it",
        "evidence leaves an obligation uncovered",
        "Inspect generated outputs at their expected path",
        "verify the live endpoint, process, rollout, or service state",
        "documentation consistency affected by the change",
        "unverified items that materially affect the completion judgment",
        "Give follow-up commands or evidence locations when needed",
        "do not invent a prior failure or imply an old version was executed",
        "effects that would remain after reverting the code",
    ):
        assert guidance in verification
    assert "State the completion claim" not in verification
    assert "For checks not run, state the exact command" not in verification
    assert "risk acceptance" in harness
    assert "irreversible or high-impact external operations" in harness


def test_refactoring_preserves_contracts_and_bounds_cleanup() -> None:
    refactor = compact("skills/calibration/references/discipline/refactor.md")
    for guidance in (
        "Identify the public behavior and compatibility contracts to preserve",
        "documented separately from structural changes",
        "justify any necessary increase in complexity",
        "transition debt created or exposed by this move",
        "Keep the cleanup within the affected scope",
        "when deciding whether to introduce, retain, or remove",
        "verification.md#diagnostic-exceptions",
        "preserve historical records and frozen evidence",
        "where existing coverage is insufficient",
        "explicit retirement condition",
        "checks that would detect a regression",
        "[verification discipline](verification.md)",
    ):
        assert guidance in refactor


def test_harness_cleanup_keeps_boundaries_without_deployment_recipes() -> None:
    harness = compact("skills/calibration/references/discipline/harness.md")
    workspace = compact(
        "skills/calibration/references/discipline/workspace-ownership.md"
    )
    verification = compact("skills/calibration/references/discipline/verification.md")
    router = compact("skills/calibration/references/discipline/README.md")
    for retired in (
        "Orchestration Adoption Gate",
        "Symphony",
        "WebSocket Origin",
        ".traces/",
        "invoke calibration",
    ):
        for reference in (harness, workspace, verification):
            assert retired not in reference
    assert "orchestration adoption" not in router
    assert (
        "intent and authorization remain governed by applicable instructions" in harness
    )
    assert "decisions that exceed current authorization" in harness
    assert "without treating that request as authorization to execute" in workspace
    assert "Do not hide them with diagnostic suppressions" in verification
    for retained in (
        "accepted responsibility for observing the work",
        "stop expanding the change, preserve the current branch",
        "When transport or polling failures prevent observing",
    ):
        assert retained in harness
    cases = {
        case["id"]: case
        for case in json.loads(text("skills/calibration/test-prompts.json"))
    }
    assert {7, 9, 14}.isdisjoint(cases)
    assert "升级给用户" in cases[21]["expected"]


def test_calibration_routes_directly_to_codebase_design() -> None:
    skill = text("skills/calibration/SKILL.md")
    assert "Load only the references required" in skill
    assert skill.count("references/design/codebase.md") == 1
    assert "references/design/README.md" not in skill
    design = REPOSITORY_ROOT / "skills/calibration/references/design"
    assert (design / "codebase.md").is_file()
    assert not (design / "README.md").exists()


def test_design_guidance_uses_contracts_without_absolute_shape_rules() -> None:
    design = compact("skills/calibration/references/design/codebase.md")
    assert "## Vocabulary" not in design
    assert "## Completion Criteria" not in design
    for guidance in (
        "Give each boundary a clear caller and responsibility",
        "call ordering, lifecycle, and any performance guarantees",
        "Justify necessary increases in complexity through concrete benefits",
        "Keep thin wrappers that provide a stable interface",
        "As an optional aid, imagine inlining",
        "without duplicating policy, exposing hidden complexity",
        "temporary compatibility paths a retirement condition",
        "For long-lived parallel interfaces, document their distinct contracts",
        "When accepting an implemented design change",
        "[verification discipline](../discipline/verification.md)",
    ):
        assert guidance in design


def test_document_routes_defer_to_local_contracts_without_duplicate_indexes() -> None:
    skill = compact("skills/calibration/SKILL.md")
    assert "Load only the references required" in skill
    assert "Follow repository-owned documentation and collaboration contracts" in skill
    assert "guidance to fill gaps in those contracts" in skill
    assert "project documentation scope" in skill
    assert "references/docs_index.md" not in skill
    retired = "docs/technology/main_path_readability/20260318-v1.0.md"
    assert not (REPOSITORY_ROOT / "skills/calibration/references" / retired).exists()
    for retired in ("$retrospect", ".traces/", "## Schema", "## Technology"):
        assert retired not in skill
    for retained in (
        "references/docs/project-layout.md",
        "for routine PR body generation",
    ):
        assert retained in skill
    assert "task retrospectives" not in skill
    naming = text("skills/calibration/references/naming.md")
    assert "## Schemas, Headers, And Identifiers" in naming
    assert "](artifact.md)" not in naming
    refactor = compact("skills/calibration/references/discipline/refactor.md")
    assert "For outputs consumed downstream" in refactor
    assert "names, locations, formats, and delivery behavior" in refactor


def test_seed_and_ruff_defaults_preserve_existing_choices() -> None:
    verification = compact("skills/calibration/references/discipline/verification.md")
    for guidance in (
        "tests, experiments, or benchmarks that require reproducible randomness",
        "use `42` as the fallback seed when no repository rule, caller value",
        "compatibility contract, or domain requirement supplies one",
        "Preserve existing seeds and allow caller overrides where needed",
        "Do not apply this fallback to security-sensitive randomness",
    ):
        assert guidance in verification
    ruff = compact("skills/calibration/references/linters/ruff.md")
    for guidance in (
        "When Ruff is appropriate for the repository",
        "follow its existing rule selection",
        "If no repository-local selection exists",
        "start with `E`, `F`, `I`, `UP`, `B`, `SIM`, and `RUF`",
        "Additional rule families, `ALL`, and preview rules",
        "repository-specific choices, not defaults",
    ):
        assert guidance in ruff
    router = text("skills/calibration/references/discipline/README.md")
    assert "Linter selection or rule defaults" in router
    assert "](../linters/ruff.md)" in router
    assert "reproducible benchmarks or randomness seeds" in router
    assert not (
        REPOSITORY_ROOT / "skills/calibration/references/linters/README.md"
    ).exists()


def test_linter_and_diagnostic_cases_cover_defaults_and_exception_boundaries() -> None:
    cases = {
        case["id"]: case
        for case in json.loads(text("skills/calibration/test-prompts.json"))
    }
    expectations = {
        46: "fallback selection E, F, I, UP, B, SIM, and RUF",
        47: "Preserve the repository's existing rule selection",
        48: "These constraints apply to type checkers as well as linters",
        49: "No mandatory adapter-first sequence applies",
    }
    for case_id, expected in expectations.items():
        assert expected in cases[case_id]["expected"]


def test_workspace_discovery_bounds_do_not_impose_generic_intake() -> None:
    workspace = compact(
        "skills/calibration/references/discipline/workspace-ownership.md"
    )
    assert "Before recursive searches or broad discovery" in workspace
    assert "within the assigned repository or task workspace" in workspace
    assert "stop the broad search and report the narrower check needed" in workspace
    assert "Keep partial cleanup observable and retryable" in workspace
    assert "preserve dirty worktrees" in workspace
    assert "accepted delivery path" not in workspace
    assert "issue tracker or an orchestrator session" not in workspace
    for retired in ("transferring ownership", "runtime release"):
        assert retired not in workspace
    cases = {
        case["id"]: case
        for case in json.loads(text("skills/calibration/test-prompts.json"))
    }
    assert "traversal-aware bound" in cases[18]["expected"]
    assert "Use a targeted read of the authorized file" in cases[50]["expected"]


def test_harness_scopes_handoff_and_preserves_review_stop_conditions() -> None:
    harness = compact("skills/calibration/references/discipline/harness.md")
    for required in (
        "When authorized unfinished work must continue after foreground tracking ends",
        "notifying a reachable recipient",
        "Saved task state or PR submission alone does not establish",
        "continue bounded observation within scope or report the blocker",
        "When review feedback exceeds the authorized contract",
        "stop expanding the change, preserve the current branch, worktree, and state",
        "escalate the scope decision",
        "When transport or polling failures prevent observing",
    ):
        assert required in harness
    cases = {
        case["id"]: case
        for case in json.loads(text("skills/calibration/test-prompts.json"))
    }
    for case_id, expected in (
        (51, "Report completion of the authorized PR-submission task"),
        (52, "Saved state alone does not establish background continuation"),
        (53, "report the observation gap"),
    ):
        assert expected in cases[case_id]["expected"]


def test_first_party_skill_markdown_uses_client_neutral_skill_names() -> None:
    skill_reference = re.compile(
        r"\$(?:calibration|closeout|dissect|grilling|plainspoken|retrospect|writing-code-docs)\b"
    )
    for path in (REPOSITORY_ROOT / "skills").rglob("*.md"):
        content = path.read_text(encoding="utf-8")
        assert not skill_reference.search(content), path
        assert "grilling" not in content.casefold(), path


def test_calibration_cases_drop_retired_github_plugin_routes() -> None:
    cases = {
        case["id"]: case
        for case in json.loads(text("skills/calibration/test-prompts.json"))
    }
    assert {30, 31, 32, 33}.isdisjoint(cases)
    for case_id in (20, 21):
        assert "LOC" not in cases[case_id]["expected"]
        assert "review-round" not in cases[case_id]["expected"]
