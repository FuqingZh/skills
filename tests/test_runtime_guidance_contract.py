from __future__ import annotations

import hashlib
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


def test_docs_separate_current_authority_from_archived_plans() -> None:
    source = REPOSITORY_ROOT / "docs/README.md"
    docs = source.read_text(encoding="utf-8")
    authority = docs.split("## Current Authority\n", 1)[1].split("\n## ", 1)[0]
    current_targets = {
        (source.parent / target.split("#", 1)[0]).resolve()
        for target in re.findall(r"\[[^]]+\]\(([^)]+)\)", authority)
    }
    assert all("ao-integration" not in str(path) for path in current_targets)
    assert REPOSITORY_ROOT / "skills/calibration/SKILL.md" in current_targets
    archive = REPOSITORY_ROOT / "docs/archive/README.md"
    assert (source.parent / "archive/README.md").resolve() in {
        (source.parent / target.split("#", 1)[0]).resolve()
        for target in re.findall(r"\[[^]]+\]\(([^)]+)\)", docs)
    }
    archived_targets = {
        (archive.parent / target.split("#", 1)[0]).resolve()
        for target in re.findall(
            r"\[[^]]+\]\(([^)]+)\)", archive.read_text(encoding="utf-8")
        )
    }
    for relative in (
        "docs/implementation-plans/"
        "20260731-v2.1-portable-orchestrator-containment-implementation-plan.md",
        "docs/implementation-plans/"
        "20260826-v1.0-self-contained-first-party-skills-migration-implementation-plan.md",
        "docs/testing/20260825-v2.1-progressive-validation-relative-replacement-test-plan.md",
        "docs/testing/"
        "20260825-v2.2-progressive-validation-relative-replacement-correction-plan.md",
        "evaluations/teach-adaptation/results.md",
        "evaluations/teach-adaptation/v2/README.md",
    ):
        assert REPOSITORY_ROOT / relative in archived_targets
        assert REPOSITORY_ROOT / relative not in current_targets


def test_retired_guidance_preserves_exact_bytes_outside_skill_loading() -> None:
    archive = REPOSITORY_ROOT / "docs/archive/ao-guidance-before-v0.12.12"
    records = json.loads(text("docs/archive/retired-guidance-manifest.json"))["files"]
    recorded_paths = {row["path"] for row in records}
    assert len(recorded_paths) == len(records)
    assert recorded_paths == {
        "docs/implementation-plans/"
        "20260731-v2.1-portable-orchestrator-containment-implementation-plan.md",
        *(
            path.relative_to(REPOSITORY_ROOT).as_posix()
            for path in archive.rglob("*")
            if path.is_file()
        ),
    }
    for row in records:
        path = REPOSITORY_ROOT / row["path"]
        assert hashlib.sha256(path.read_bytes()).hexdigest() == row["sha256"], path
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
    assert (
        REPOSITORY_ROOT / "docs/archive/ao-integration-retired-2026-10-15.md"
    ).is_file()


def test_generic_boundaries_have_reachable_reference_owners() -> None:
    skill = compact("skills/calibration/SKILL.md")
    discipline = compact("skills/calibration/references/discipline/README.md")
    harness = compact("skills/calibration/references/discipline/harness.md")
    debugging = compact("skills/calibration/references/discipline/debugging.md")
    assert "references/discipline/README.md" in skill
    assert "references/discipline/harness.md" not in skill
    assert "`harness.md`" in discipline
    assert "`debugging.md`" in discipline
    assert "Implementation or contract verification" in discipline
    assert "| Completion claim," not in discipline
    assert "environment evidence boundaries" in discipline
    assert (
        "Workspace search boundaries, ownership transfer, or runtime release"
        in discipline
    )
    for rule in (
        "write-authority revocation and runtime release",
        "sibling worktree",
        "empty OS-owned containment boundary",
        "traversal-aware bound",
        "terminated session is not proof",
        "rejected filesystem escalation",
    ):
        assert rule in harness
    assert (
        "For first-party code and interfaces, repair the contract or implementation"
        in harness
    )
    assert "do not use an ignore comment" in harness.lower()
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
    docs = compact("skills/calibration/references/docs_index.md")
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
    assert "Follow its existing layout" in docs
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
        "harness.md#diagnostic-suppression-baseline",
        "preserve historical records and frozen evidence",
        "where existing coverage is insufficient",
        "explicit retirement condition",
        "checks that would detect a regression",
        "[verification discipline](verification.md)",
    ):
        assert guidance in refactor


def test_harness_cleanup_keeps_boundaries_without_deployment_recipes() -> None:
    harness = compact("skills/calibration/references/discipline/harness.md")
    router = compact("skills/calibration/references/discipline/README.md")
    for retired in (
        "Orchestration Adoption Gate",
        "Symphony",
        "WebSocket Origin",
        ".traces/",
        "invoke calibration",
    ):
        assert retired not in harness
    assert "orchestration adoption" not in router
    for retained in (
        "intent and authorization remain governed by applicable instructions",
        "without treating that request as authorization to execute",
        "Do not broaden suppressions to hide first-party failures",
        "accepted responsibility for observing the work",
        "pause remote review and preserve branch, head, worktree",
        "Transport, polling, or idempotent-operation retry exhaustion",
        "decisions that exceed current authorization",
    ):
        assert retained in harness
    cases = {
        case["id"]: case
        for case in json.loads(text("skills/calibration/test-prompts.json"))
    }
    assert {7, 9, 14}.isdisjoint(cases)
    assert "不能因为预算耗尽就必须选择 PR 拓扑" in cases[21]["expected"]


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


def test_docs_index_defers_to_local_contracts_without_duplicate_routes() -> None:
    index = compact("skills/calibration/references/docs_index.md")
    assert "Load only references material to the current task" in index
    assert "Follow repository-owned documentation and collaboration contracts" in index
    assert "guidance to fill gaps in those contracts" in index
    assert "project documentation layout" in index
    retired = "docs/technology/main_path_readability/20260318-v1.0.md"
    assert retired not in index
    assert not (REPOSITORY_ROOT / "skills/calibration/references" / retired).exists()
    assert "## Technology" not in index
    for retired in ("$retrospect", ".traces/", "## Schema", "stricter local contract"):
        assert retired not in index
    for retained in (
        "docs/document-types/README.md",
        "branch_and_pr_collaboration/20260602-v1.0.md",
        "20260805-v1.1-project-docs-architecture.md",
        "Do not use it for PR body generation",
    ):
        assert retained in index
    naming = text("skills/calibration/references/naming/README.md")
    assert "](schema.md)" in naming
    assert "](artifact.md)" in naming


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
    harness = compact("skills/calibration/references/discipline/harness.md")
    for guidance in (
        "When Ruff is appropriate for the repository",
        "follow its existing rule selection",
        "If no repository-local selection exists",
        "start with `E`, `F`, `I`, `UP`, `B`, `SIM`, and `RUF`",
        "Additional rule families, `ALL`, and preview rules",
        "repository-specific choices, not defaults",
    ):
        assert guidance in harness
    router = text("skills/calibration/references/discipline/README.md")
    assert (
        "| Repository quality-gate adoption or Ruff rule defaults | `harness.md` |"
        in router
    )
