from __future__ import annotations

import json
from pathlib import Path

from tests.support import REPOSITORY_ROOT


def _prompt_cases() -> dict[int, dict[str, str]]:
    path = REPOSITORY_ROOT / "skills/calibration/test-prompts.json"
    return {case["id"]: case for case in json.loads(path.read_text())}


def test_document_routing_overview_covers_all_current_neighbors() -> None:
    case = _prompt_cases()[2]
    expected = case["expected"]

    for document_type in (
        "architecture-overview",
        "decision-record",
        "implementation-plan",
        "tutorial",
        "how-to-guide",
        "runbook",
        "compatibility-record",
        "test-plan",
        "benchmark-record",
        "trace-retro",
    ):
        assert document_type in expected
    assert "PR body 不是长期文档" in expected
    assert "archive 是生命周期状态\uff0c不是文档类型" in expected


def test_focused_document_routing_cases_choose_one_primary_type() -> None:
    cases = _prompt_cases()
    expected_routes = {
        23: ("tutorial", "docs/tutorials/", ("how-to guide", "architecture overview")),
        24: ("how-to guide", "docs/how-to-guides/", ("tutorial", "runbook")),
        25: ("runbook", "docs/runbooks/", ("how-to guide", "未经验证")),
        26: (
            "compatibility record",
            "docs/compatibility/",
            ("architecture overview", "tutorial", ".traces/"),
        ),
        27: (
            "decision record",
            "docs/decisions/",
            ("architecture overview", "尚未决定"),
        ),
        28: (
            "implementation plan",
            "docs/implementation-plans/",
            ("design proposal", "decision record", "PR body"),
        ),
    }

    for case_id, (primary_type, path, rejected_neighbors) in expected_routes.items():
        expected = cases[case_id]["expected"]
        assert expected.count("主类型应是") == 1
        assert primary_type in expected
        assert path in expected
        for neighbor in rejected_neighbors:
            assert neighbor in expected


def test_document_type_index_contains_only_routes_to_type_files() -> None:
    directory = REPOSITORY_ROOT / "skills/calibration/references/docs/document-types"
    index = directory / "README.md"
    lines = index.read_text(encoding="utf-8").splitlines()
    assert lines[:2] == ["# Document Types", ""]
    targets: list[Path] = []
    for purpose, route in zip(lines[2::2], lines[3::2], strict=True):
        assert purpose.startswith("- ") and purpose.endswith(":")
        assert route.startswith("  `") and route.endswith(".md`")
        target = directory / route.removeprefix("  `").removesuffix("`")
        assert target.is_file()
        targets.append(target)
    assert len(targets) == len(set(targets)) == 10
    assert set(targets) == set(directory.glob("*.md")) - {index}


def test_architecture_overview_keeps_local_precedence_and_fallback() -> None:
    path = REPOSITORY_ROOT / (
        "skills/calibration/references/docs/document-types/architecture-overview.md"
    )
    overview = " ".join(path.read_text(encoding="utf-8").split())
    assert (
        "Follow the repository's documentation convention. If no architecture "
        "location is defined, use `docs/architecture/`."
    ) in overview
    assert "using the repository's current source of truth" in overview
    assert "ownership boundaries, and data flow" in overview
    assert "records when they exist" in overview
    assert (
        "Distinguish current behavior from proposals and historical behavior"
        in overview
    )


def test_design_proposal_keeps_fallback_and_decision_context() -> None:
    path = REPOSITORY_ROOT / (
        "skills/calibration/references/docs/document-types/design-proposal.md"
    )
    proposal = " ".join(path.read_text(encoding="utf-8").split())
    for guidance in (
        "Follow the repository's proposal location. If none is defined, use "
        "`docs/architecture/`.",
        "current architecture and contracts of the affected boundary",
        "Compare viable alternatives and recommend a direction with reasons",
        "Distinguish proposed directions from accepted decisions",
        "without reconstructing the conversation that produced it",
    ):
        assert guidance in proposal
    assert "separate from an implementation plan until" not in proposal


def test_decision_record_keeps_rationale_and_local_defaults() -> None:
    path = REPOSITORY_ROOT / (
        "skills/calibration/references/docs/document-types/decision-record.md"
    )
    record = " ".join(path.read_text(encoding="utf-8").split())
    for guidance in (
        "Record settled, high-impact choices whose rationale matters",
        "Follow the repository's decision-record location. If none is defined, use "
        "`docs/decisions/`.",
        "Follow the repository's record format when defined",
        "are optional format references",
        "Record the decision date and status",
        "alternatives that materially affected the choice",
        "consequences, including follow-up obligations",
        "Record conditions that would justify reopening it",
    ):
        assert guidance in record
    assert "https://adr.github.io/" in record
    assert "https://adr.github.io/adr-templates/" in record


def test_implementation_plan_preserves_defaults_and_readiness() -> None:
    path = REPOSITORY_ROOT / (
        "skills/calibration/references/docs/document-types/implementation-plan.md"
    )
    plan = " ".join(path.read_text(encoding="utf-8").split())
    for guidance in (
        "Follow the repository's planning location. If none is defined, use "
        "`docs/implementation-plans/`.",
        "Persist or commit the plan only when explicitly requested or required "
        "by repository workflow",
        "Preserve established boundaries unless the settled design "
        "explicitly changes them",
        "acceptance checks, and evidence locations",
        "before starting implementation that depends on them",
        "bounded investigations with questions, expected evidence, decision criteria",
        "conditions for starting dependent work",
        "representative inputs or states and observable acceptance results",
        "Describe review splits when needed for delivery",
        "Make ready slices executable",
        "Keep unresolved details explicit",
    ):
        assert guidance in plan
    assert "Use separate plans for independent subsystems" not in plan
    assert "before decomposing tasks" not in plan


def test_test_plan_keeps_reusable_checks_and_location_fallback() -> None:
    path = REPOSITORY_ROOT / (
        "skills/calibration/references/docs/document-types/test-plan.md"
    )
    plan = " ".join(path.read_text(encoding="utf-8").split())
    for guidance in (
        "need reuse across changes, releases, or environments",
        "Follow the repository's testing-documentation location. "
        "If none is defined, use `docs/testing/`.",
        "Use configured test and verification entrypoints",
        "implementation details with their owning code",
        "fixtures, data boundaries, environment assumptions, and required setup",
        "commands or CI checks, expected evidence, and failure interpretation",
        "acceptance criteria and any required manual artifact or runtime inspection",
        "compatibility, cleanup, and rollback implications when applicable",
    ):
        assert guidance in plan


def test_benchmark_record_keeps_evidence_and_comparison_scope() -> None:
    path = REPOSITORY_ROOT / (
        "skills/calibration/references/docs/document-types/benchmark-record.md"
    )
    record = " ".join(path.read_text(encoding="utf-8").split())
    for guidance in (
        "Follow the repository's benchmark-record location. If none is defined, use "
        "`docs/benchmarks/`.",
        "Follow project measurement and reproducibility rules",
        "For comparisons, identify the baseline and comparison method",
        "metrics, protocol, repetitions, and the random seed where relevant",
        "Preserve the output path or artifact needed to inspect the result",
        "uncertainty, limitations, and any failed or skipped checks",
        "conditions under which the result remains comparable or should be rerun",
        "the limits of its conclusions",
    ):
        assert guidance in record


def test_tutorial_keeps_learning_path_and_record_boundaries() -> None:
    path = REPOSITORY_ROOT / (
        "skills/calibration/references/docs/document-types/tutorial.md"
    )
    tutorial = " ".join(path.read_text(encoding="utf-8").split())
    for guidance in (
        "stated prerequisites to a demonstrable new capability",
        "without reconstructing the conversation that produced it",
        "https://diataxis.fr/tutorials/",
        "Follow the repository's tutorial location. If none is defined, use "
        "`docs/tutorials/`.",
        "audience, prerequisites, and one tangible learning outcome",
        "Sequence small steps that build toward the outcome",
        "verification or exercise that demonstrates the reader reached the outcome",
        "Link external sources for claims that are not project-owned facts",
        "personal learner records and teaching-session notes "
        "outside team documentation",
    ):
        assert guidance in tutorial


def test_how_to_keeps_task_verification_and_recovery() -> None:
    path = REPOSITORY_ROOT / (
        "skills/calibration/references/docs/document-types/how-to-guide.md"
    )
    guide = " ".join(path.read_text(encoding="utf-8").split())
    for guidance in (
        "stated prerequisites perform and verify one concrete task",
        "https://diataxis.fr/how-to-guides/",
        "Follow the repository's how-to location. If none is defined, use "
        "`docs/how-to-guides/`.",
        "prerequisites, applicable versions, and assumptions",
        "commands or exact interface labels where ambiguity would cause failure",
        "distinguish success from partial completion or failure",
        "Link architecture, compatibility, or runbook documents",
        "recovery or escalation guidance when a partial result can leave the "
        "system in a confusing or unsafe state",
    ):
        assert guidance in guide
