"""Mechanical cross-file invariants for first-party skills and repository maps."""

from __future__ import annotations

import re
from pathlib import Path
from typing import cast

import yaml

from scripts.validate_skills import discover_skills
from tests.support import REPOSITORY_ROOT

SKILLS_ROOT = REPOSITORY_ROOT / "skills"
CLIENT_SKILL_SYNTAX = re.compile(
    r"\$(?:calibration|closeout|dissect|grilling|plainspoken|retrospect|writing-code-docs)\b"
)
PRIVATE_DISCOVERY_TOKENS = (
    "HOST_AUTHORITY",
    "HOST_CONFIG_ROOT",
    "XDG_CONFIG_HOME",
    ".config/calibration",
    "calibration/AGENTS.md",
)


def _skill_dirs() -> list[Path]:
    return discover_skills(REPOSITORY_ROOT)


def _frontmatter(skill_md: Path) -> dict[str, object]:
    _, raw, _ = skill_md.read_text(encoding="utf-8").split("---", 2)
    return cast(dict[str, object], yaml.safe_load(raw))


def test_first_party_skill_directories_ship_only_skill_markdown() -> None:
    skill_dirs = _skill_dirs()
    assert skill_dirs
    for skill_dir in skill_dirs:
        metadata = _frontmatter(skill_dir / "SKILL.md")
        assert metadata.get("disable-model-invocation", False) is False

        files = sorted(
            path.relative_to(skill_dir).as_posix()
            for path in skill_dir.rglob("*")
            if path.is_file()
        )
        for relative in files:
            assert relative == "SKILL.md" or (
                relative.startswith("references/") and relative.endswith(".md")
            ), f"unexpected shipped file in {skill_dir.name}: {relative}"


def test_skill_entrypoints_have_no_duplicate_reference_routes() -> None:
    for skill_dir in _skill_dirs():
        body = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
        targets = re.findall(r"`(references/[^`]+\.md)`", body)
        assert len(targets) == len(set(targets)), (
            f"duplicate route target in {skill_dir.name}/SKILL.md: {targets}"
        )


def test_public_entrypoints_and_adr_index_stay_in_sync() -> None:
    skill_names = {path.name for path in _skill_dirs()}
    for index_path in ("README.md", "README.zh-CN.md", "docs/README.md"):
        content = (REPOSITORY_ROOT / index_path).read_text(encoding="utf-8")
        for name in skill_names:
            assert f"skills/{name}/SKILL.md" in content, (
                f"{index_path} missing link to skills/{name}/SKILL.md"
            )

    docs_readme = (REPOSITORY_ROOT / "docs/README.md").read_text(encoding="utf-8")
    adr_files = sorted((REPOSITORY_ROOT / "docs/adr").glob("*.md"))
    assert adr_files
    for adr in adr_files:
        assert f"](adr/{adr.name})" in docs_readme, (
            f"docs/README.md missing ADR entry for {adr.name}"
        )

    template = (REPOSITORY_ROOT / "templates/AGENTS.md.template").read_text(
        encoding="utf-8"
    )
    routed_skills = set(re.findall(r"`([a-z0-9-]+)`", template))
    assert routed_skills
    assert routed_skills <= skill_names


def test_skills_are_client_neutral_and_public_surfaces_avoid_private_discovery() -> (
    None
):
    for path in SKILLS_ROOT.rglob("*.md"):
        content = path.read_text(encoding="utf-8")
        assert not CLIENT_SKILL_SYNTAX.search(content), path

    public_files = [
        REPOSITORY_ROOT / "install.sh",
        REPOSITORY_ROOT / "templates/AGENTS.md.template",
        *(path for path in SKILLS_ROOT.rglob("*") if path.is_file()),
    ]
    for path in public_files:
        content = path.read_text(encoding="utf-8", errors="ignore")
        for token in PRIVATE_DISCOVERY_TOKENS:
            assert token not in content, f"{path} references private token {token!r}"
