from __future__ import annotations

import hashlib
import json
from pathlib import Path

from scripts.validate_skills import discover_skills

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
ARCHIVED_NAMES = {
    "brainstorming",
    "coding-protocol",
    "writing-great-skills",
    "writing-plans",
    "teach",
    "grilling",
}


def test_archived_sources_preserve_exact_bytes_and_stay_out_of_runtime() -> None:
    archive = REPOSITORY_ROOT / "thirdparty/archive"
    records = [
        row
        for name in (
            "manifest.json",
            "brainstorming-manifest.json",
            "teach-grilling-manifest.json",
        )
        for row in json.loads((archive / name).read_text(encoding="utf-8"))["files"]
    ]
    assert {Path(row["archived_path"]).parts[2] for row in records} == ARCHIVED_NAMES
    expected_paths: set[Path] = set()
    for row in records:
        path = REPOSITORY_ROOT / row["archived_path"]
        expected_paths.add(path)
        assert path.is_file()
        assert hashlib.sha256(path.read_bytes()).hexdigest() == row["sha256"]
        assert not (REPOSITORY_ROOT / row["original_path"]).exists()
    actual_paths = {
        path
        for name in ARCHIVED_NAMES
        for path in (archive / name).rglob("*")
        if path.is_file()
    }
    assert actual_paths == expected_paths
    assert not ARCHIVED_NAMES & {path.name for path in discover_skills(REPOSITORY_ROOT)}
