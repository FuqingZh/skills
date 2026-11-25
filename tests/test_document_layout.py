"""Static code-first documentation layout contracts without model execution."""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

from tests.support import REPOSITORY_ROOT

CALIBRATION = REPOSITORY_ROOT / "skills/calibration"
LAYOUT = CALIBRATION / "references/docs/project-layout.md"


def compact(path: Path) -> str:
    return " ".join(path.read_text(encoding="utf-8").split())


def test_documentation_guidance_is_single_file_and_code_first() -> None:
    assert LAYOUT.is_file()
    assert not (CALIBRATION / "references/docs/document-types").exists()
    body = compact(LAYOUT)
    for rule in (
        "Follow repository-owned documentation contracts and existing paths",
        "code, types, schemas, executable tests, and CI as the source of truth",
        "Do not maintain prose mirrors",
        "Create only the files and directories needed",
        "`docs/adr/`",
        "Flat `docs/<topic>.md` files",
        "Keep implementation plans and proposals ephemeral",
        "Rely on Git history as the archive",
        "Do not maintain a `docs/archive/` directory",
        "compact the reason the old choice was abandoned into the replacing ADR",
        "remove the superseded file from `HEAD`",
        "](../discipline/harness.md#agentsmd-contract)",
        "](../discipline/verification.md)",
        "fallback seed defaults",
        "Keep one current summary updated in place for active benchmarks",
        "fold negative or one-off experiment takeaways into the owning ADR",
        "ordered checkpoints, verification, recovery, rollback, escalation, and stop",
        "without embedded version numbers",
        "`YYYY-MM-DD-topic.md`",
    ):
        assert rule in body
    for retired in (
        "document-types/",
        "YYYYMMDD-vMAJOR.MINOR",
        "docs/design/",
        "docs/contributing/",
        "docs/architecture/",
    ):
        assert retired not in body


def test_current_layout_uses_a_stable_path_without_version_metadata() -> None:
    body = LAYOUT.read_text(encoding="utf-8")
    assert body.startswith("# Project Documentation\n\nUse when")
    assert not re.search(r"^(Version|Date|Status):", body, flags=re.MULTILINE)
    assert not (CALIBRATION / "references/docs/workflow").exists()


def test_repository_docs_follow_minimal_active_model() -> None:
    docs_root = REPOSITORY_ROOT / "docs"
    for retired_dir in ("archive", "decisions", "implementation-plans", "testing"):
        assert not (docs_root / retired_dir).exists()
    assert not (REPOSITORY_ROOT / ".traces").exists()
    adr_dir = docs_root / "adr"
    assert adr_dir.is_dir()
    adr_files = sorted(adr_dir.glob("*.md"))
    assert len(adr_files) >= 1
    readme = (docs_root / "README.md").read_text(encoding="utf-8")
    for adr in adr_files:
        assert f"](adr/{adr.name})" in readme


@pytest.mark.parametrize(
    ("case_id", "phrases"),
    [
        (2, ("project-layout.md", "docs/adr/", "docs/archive/")),
        (25, ("runbook", "检查点", "回滚")),
        (26, ("docs/", ".calibration/notes/", "外部边界")),
        (27, ("docs/adr/", "YYYY-MM-DD-topic.md", "HEAD")),
        (28, ("临时态", "ADR")),
        (34, ("local authority", "docs/decisions/", "Do not migrate")),
        (35, ("source of truth", "docs/adr/", "Git history")),
        (37, ("updated in place", "owning ADR", "Git reference")),
    ],
)
def test_documentation_cases_cover_code_first_model(
    case_id: int, phrases: tuple[str, ...]
) -> None:
    cases = json.loads((CALIBRATION / "test-prompts.json").read_text(encoding="utf-8"))
    selected = [case for case in cases if case["id"] == case_id]
    assert len(selected) == 1
    for phrase in phrases:
        assert phrase in selected[0]["expected"]
