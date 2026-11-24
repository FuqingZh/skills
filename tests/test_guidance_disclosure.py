from __future__ import annotations

import re
from pathlib import Path

from tests.support import REPOSITORY_ROOT

CALIBRATION = REPOSITORY_ROOT / "skills/calibration"
REFERENCES = CALIBRATION / "references"
DISCIPLINE = REFERENCES / "discipline"
LAYOUT = REFERENCES / "docs/project-layout.md"


def compact(path: Path) -> str:
    return " ".join(path.read_text(encoding="utf-8").split())


def test_document_selection_is_direct_and_single_branch() -> None:
    skill = (CALIBRATION / "SKILL.md").read_text(encoding="utf-8")
    targets = re.findall(r"`(references/[^`]+\.md)`", skill)
    assert len(targets) == len(set(targets))
    assert all((CALIBRATION / target).is_file() for target in targets)
    assert LAYOUT.relative_to(CALIBRATION).as_posix() in targets
    assert "references/docs/document-types/README.md" not in targets
    assert "references/docs_index.md" not in targets
    assert "task retrospectives" not in skill
    assert "ADRs, external-fact records, runbooks" in skill


def test_discipline_routes_bypass_retired_harness_forwarders() -> None:
    router = (DISCIPLINE / "README.md").read_text(encoding="utf-8")
    harness = (DISCIPLINE / "harness.md").read_text(encoding="utf-8")
    branches = {
        "Linter selection": (
            "../linters/ruff.md",
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
        assert f"]({target})" in row
        assert "](harness.md)" not in row
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
        assert "](harness.md)" in row
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
    naming = compact(REFERENCES / "naming/README.md")
    assert not (REFERENCES / "linters/README.md").exists()
    assert (REFERENCES / "linters/ruff.md").is_file()
    assert "selection or rule defaults, use [Ruff defaults]" in naming
    assert "](../linters/ruff.md)" in naming
    assert not (DISCIPLINE / "quality-gates.md").exists()
    for path in REFERENCES.rglob("*.md"):
        body = compact(path)
        for retired in (
            "quality-gates.md",
            "typed adapter, stub, wrapper",
            "Use a source-level suppression only when no such boundary",
        ):
            assert retired not in body, path


def test_working_material_ownership_does_not_depend_on_directory_name() -> None:
    layout = compact(LAYOUT)
    for rule in (
        "Investigation notes belong to the owning task",
        "Formal project documents remain project-owned",
        "One-off observations need not be persisted automatically",
        "Hidden paths do not provide privacy",
        "otherwise use `.calibration/notes/`",
    ):
        assert rule in layout
