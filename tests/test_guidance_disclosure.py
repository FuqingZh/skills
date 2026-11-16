from __future__ import annotations

import re
from pathlib import Path

from tests.support import REPOSITORY_ROOT

CALIBRATION = REPOSITORY_ROOT / "skills/calibration"
REFERENCES = CALIBRATION / "references"
DISCIPLINE = REFERENCES / "discipline"
TYPES = REFERENCES / "docs/document-types"
LAYOUT = REFERENCES / (
    "docs/workflow/project_docs_architecture/20260805-v1.1-project-docs-architecture.md"
)
RETROSPECT = REPOSITORY_ROOT / "skills/retrospect"


def compact(path: Path) -> str:
    return " ".join(path.read_text(encoding="utf-8").split())


def test_document_selection_is_direct_and_layout_is_a_separate_branch() -> None:
    skill = (CALIBRATION / "SKILL.md").read_text(encoding="utf-8")
    targets = re.findall(r"`(references/[^`]+\.md)`", skill)
    assert len(targets) == len(set(targets))
    assert all((CALIBRATION / target).is_file() for target in targets)
    assert "references/docs/document-types/README.md" in targets
    assert LAYOUT.relative_to(CALIBRATION).as_posix() in targets
    assert "references/docs_index.md" not in targets
    assert "task retrospectives" not in skill
    assert "document type and minimum content" in skill
    assert "project documentation layout, naming, navigation, and lifecycle" in skill


def test_discipline_routes_bypass_retired_harness_forwarders() -> None:
    router = (DISCIPLINE / "README.md").read_text(encoding="utf-8")
    harness = (DISCIPLINE / "harness.md").read_text(encoding="utf-8")
    branches = {
        "Linter selection": (
            "../linters/README.md",
            "### Ruff Defaults",
        ),
        "diagnostic suppression or exclusion decisions": (
            "verification.md",
            "### Diagnostic suppression baseline",
        ),
        "runtime release": (
            "workspace-ownership.md",
            "## Implementation Task Intake",
        ),
    }
    for trigger, (target, retired_heading) in branches.items():
        row = next(line for line in router.splitlines() if trigger in line)
        assert f"`{target}`" in row
        assert "`harness.md`" not in row
        assert (DISCIPLINE / target).is_file()
        assert retired_heading not in harness
    assert "](verification.md#diagnostic-exceptions)" in (
        DISCIPLINE / "refactor.md"
    ).read_text(encoding="utf-8")


def test_extracted_rules_have_one_body_owner() -> None:
    owners = {
        "linters/ruff.md": ("When Ruff is appropriate for the repository",),
        "discipline/verification.md": (
            "Repair real errors in first-party code and interfaces",
            "For demonstrated external or checker gaps",
        ),
        "discipline/workspace-ownership.md": (
            "A terminated session is not proof",
            "Follow the user's authorized scope",
        ),
        "discipline/harness.md": (
            "When authorized unfinished work must continue",
            "If review on the exact current head exceeds the authorized contract",
        ),
    }
    texts = {
        path.relative_to(REFERENCES).as_posix(): compact(path)
        for path in REFERENCES.rglob("*.md")
    }
    for owner, rules in owners.items():
        for rule in rules:
            assert {name for name, body in texts.items() if rule in body} == {owner}


def test_continuation_and_review_boundaries_route_to_harness() -> None:
    router = (DISCIPLINE / "README.md").read_text(encoding="utf-8")
    for trigger in (
        "durable continuation",
        "cross-contract review",
        "review-convergence exhaustion",
    ):
        row = next(line for line in router.splitlines() if trigger in line)
        assert "`harness.md`" in row
    assert not (DISCIPLINE / "delivery-feedback.md").exists()
    for path in REFERENCES.rglob("*.md"):
        assert "delivery-feedback.md" not in path.read_text(encoding="utf-8"), path
    harness = (DISCIPLINE / "harness.md").read_text(encoding="utf-8")
    assert "## Repository Delivery Feedback Loop" in harness
    for removed in (
        "Keep the repository as the source of truth across execution environments",
        "Add recurring monitoring",
        "Handle same-scope mechanical review feedback",
    ):
        assert removed not in harness


def test_linter_routes_keep_tool_defaults_separate_from_shared_constraints() -> None:
    index = compact(REFERENCES / "linters/README.md")
    naming = compact(REFERENCES / "naming/README.md")
    assert (
        "Read only the reference for the linter relevant to the current task" in index
    )
    assert "](ruff.md)" in index
    assert "selection or rule defaults, use [linter references]" in naming
    assert "](../linters/README.md)" in naming
    assert not (DISCIPLINE / "quality-gates.md").exists()
    for path in REFERENCES.rglob("*.md"):
        body = compact(path)
        for retired in (
            "quality-gates.md",
            "typed adapter, stub, wrapper",
            "Use a source-level suppression only when no such boundary",
        ):
            assert retired not in body, path


def test_layout_and_type_defaults_agree_without_duplicate_type_rules() -> None:
    source = LAYOUT.read_text(encoding="utf-8")
    layout = compact(LAYOUT)
    directories = set(re.findall(r"^  ([a-z-]+)/$", source, flags=re.MULTILINE))
    type_directories: set[str] = set()
    for path in TYPES.glob("*.md"):
        type_directories.update(
            location.split("/", 1)[0]
            for location in re.findall(r"`docs/([a-z/-]+)/`", path.read_text())
        )
    assert directories == type_directories | {"assets", "archive"}
    assert "](../../document-types/README.md)" in source
    assert "Each type owns its minimum content and fallback location" in layout
    assert "a document type need not own a separate directory" in layout
    assert "Co-location does not merge document contracts" in layout
    assert (
        "acceptance records agreement on a direction, "
        "not evidence that it is implemented" in layout
    )
    for retired in (
        "do not use for unapproved future direction",
        "## Document Selection Boundaries",
        "## Minimal Authoring Contract",
        "Use When",
        "Method Reference",
        "Local Requirements",
        "Complete When",
    ):
        assert retired not in source


def test_working_material_ownership_does_not_depend_on_directory_name() -> None:
    layout = compact(LAYOUT)
    compatibility = compact(TYPES / "compatibility-record.md")
    for rule in (
        "Investigation notes belong to the task",
        "Retrospect owns records of expectation versus outcome",
        "ordinary investigation or project-document writing does not invoke",
        "Formal project documents remain project-owned",
        "One-off observations need not be persisted automatically",
        "Hidden paths do not provide privacy",
        "otherwise use `.calibration/notes/`",
    ):
        assert rule in layout
    assert "owning investigation's task records" in compatibility
    assert "#working-material)" in compatibility
    assert "retrospect" not in compatibility.lower()


def test_retrospect_loads_one_persistence_contract_and_preserves_fallbacks() -> None:
    skill = (RETROSPECT / "SKILL.md").read_text(encoding="utf-8")
    assert re.findall(r"`(references/[^`]+\.md)`", skill) == [
        "references/task-traces-and-retros.md"
    ]
    assert "disable-model-invocation: true" in skill
    assert "only after a separate explicit request" in compact(RETROSPECT / "SKILL.md")
    pointer = compact(RETROSPECT / "references/trace-retro.md")
    assert "](task-traces-and-retros.md)" in pointer
    assert "adds no separate requirements" in pointer
    contract = compact(RETROSPECT / "references/task-traces-and-retros.md")
    for rule in (
        "user asks to persist a confirmed task-level lesson",
        "Routine investigation notes remain with their owning task",
        "Follow repository-local retrospective rules",
        ".retrospect/",
        ".retrospect/evidence/",
        "fallback out of Git unless repository-local policy explicitly permits",
        "no bulk migration is required",
        "Remaining hypotheses and verification gaps",
        "Future action",
        "separate authorization required by retrospect",
        "make the promoted location the source of truth",
    ):
        assert rule in contract
