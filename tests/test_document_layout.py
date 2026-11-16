"""Static layout contracts and synthetic routing cases, without model execution."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

import pytest

from tests.support import REPOSITORY_ROOT

CALIBRATION = REPOSITORY_ROOT / "skills/calibration"
TYPES = CALIBRATION / "references/docs/document-types"
LAYOUT = CALIBRATION / "references/docs/project-layout.md"
DEFAULTS = {
    "architecture-overview": "architecture",
    "design-proposal": "design",
    "decision-record": "architecture/decisions",
    "implementation-plan": "design",
    "test-plan": "contributing",
    "benchmark-record": "contributing",
    "tutorial": "guides",
    "how-to-guide": "guides",
    "runbook": "runbooks",
    "compatibility-record": "reference",
}


def compact(path: Path) -> str:
    return " ".join(path.read_text(encoding="utf-8").split())


@pytest.mark.parametrize(("document", "location"), DEFAULTS.items())
def test_type_fallbacks_share_directories_with_local_precedence(
    document: str, location: str
) -> None:
    body = compact(TYPES / f"{document}.md")
    assert re.findall(r"`docs/([a-z/-]+)/`", body) == [location]
    assert "Follow the repository's" in body
    assert "If no" in body


def test_layout_has_eight_optional_locations_without_mandatory_scaffolding() -> None:
    source = LAYOUT.read_text(encoding="utf-8")
    assert set(re.findall(r"^  ([a-z-]+)/$", source, flags=re.MULTILINE)) == {
        "architecture",
        "design",
        "guides",
        "reference",
        "contributing",
        "runbooks",
        "assets",
        "archive",
    }
    body = compact(LAYOUT)
    for rule in (
        "Follow repository-owned documentation contracts",
        "Preserve established paths until a reviewed migration",
        "Do not create empty directories",
        "Existing files such as `ARCHITECTURE.md` or `CONTRIBUTING.md`",
        "Introduce subdirectories only when navigation, ownership, or maintenance",
        "a document type need not own a separate directory",
        "`runbooks/` is optional",
        "`archive/` is a lifecycle location, not a document type",
    ):
        assert rule in body


def test_co_location_preserves_contracts_and_source_ownership() -> None:
    body = compact(LAYOUT)
    for rule in (
        "groups proposals and durable implementation plans by change topic",
        "Use one document with distinct sections when sufficient",
        "A plan can stand alone without inventing a proposal",
        "Do not require a proposal, plan, and decision record for every change",
        "tutorials and how-to pages distinguishable by purpose",
        "Link generated or code-owned references",
        "checks specific to one proposed change can stay with that change",
        "Keep executable tests and benchmark artifacts with their owners",
        "Co-location does not merge document contracts",
    ):
        assert rule in body
    decisions = compact(TYPES / "decision-record.md")
    assert "Keep other decisions with their owning project topic" in decisions


def test_acceptance_and_implementation_have_distinct_authority() -> None:
    body = compact(LAYOUT)
    for rule in (
        "agreement on a direction, not evidence that it is implemented",
        "proposed, accepted, implemented, rejected, or superseded",
        "Update current architecture and reference material "
        "when implementation evidence",
        "Retain the original rationale",
        "records may remain in place with explicit status",
        "do not move every completed plan or superseded decision",
        "A directory or filename alone does not establish "
        "acceptance or evidence quality",
    ):
        assert rule in body
    assert "keeps its original document type and is not current authority" in body
    assert "unless a current document explicitly cites it" not in body


def test_current_layout_uses_a_stable_path_without_version_metadata() -> None:
    body = LAYOUT.read_text(encoding="utf-8")
    assert body.startswith("# Project Documentation Layout\n\nUse for")
    assert not re.search(r"^(Version|Date|Status):", body, flags=re.MULTILINE)
    retired = CALIBRATION / "references/docs/workflow/project_docs_architecture"
    assert not retired.exists()
    for path in CALIBRATION.rglob("*.md"):
        assert "20260805-v1.1-project-docs-architecture.md" not in path.read_text(
            encoding="utf-8"
        ), path


def test_superseded_layout_is_archived_without_active_routes() -> None:
    old_name = "20260527-v1.0-project-docs-architecture.md"
    old_path = f"references/docs/workflow/project_docs_architecture/{old_name}"
    archive = REPOSITORY_ROOT / "docs/archive/project-docs-layout" / f"{old_name}.txt"
    expected_digest = "f6b60bfdcf1960de69c95d39d391019dc800e61c442fec7f31c3039ec3c3a61d"
    assert hashlib.sha256(archive.read_bytes()).hexdigest() == expected_digest
    assert not (CALIBRATION / old_path).exists()
    assert "Supersedes:" not in LAYOUT.read_text(encoding="utf-8")
    for path in CALIBRATION.rglob("*.md"):
        body = path.read_text(encoding="utf-8")
        assert old_name not in body, path
        assert "project-docs-layout/" not in body, path
    index = (REPOSITORY_ROOT / "docs/archive/README.md").read_text(encoding="utf-8")
    assert f"`skills/calibration/{old_path}`" in index
    assert f"](project-docs-layout/{old_name}.txt)" in index
    current_path = LAYOUT.relative_to(REPOSITORY_ROOT).as_posix()
    assert f"](../../{current_path})" in index


@pytest.mark.parametrize(
    ("case_id", "phrases"),
    [
        (34, ("as local authority", "without creating parallel", "Do not migrate")),
        (35, ("distinct sections", "can also stand alone", "implementation evidence")),
        (36, ("docs/reference/", "generated CLI reference", "rather than copying")),
        (37, ("docs/contributing/", "docs/design/", "raw benchmark artifacts")),
        (38, ("no empty scaffolding", "at its existing path", "stop conditions")),
    ],
)
def test_synthetic_cases_cover_grouping_and_preservation(
    case_id: int, phrases: tuple[str, ...]
) -> None:
    cases = json.loads((CALIBRATION / "test-prompts.json").read_text(encoding="utf-8"))
    selected = [case for case in cases if case["id"] == case_id]
    assert len(selected) == 1
    for phrase in phrases:
        assert phrase in selected[0]["expected"]
