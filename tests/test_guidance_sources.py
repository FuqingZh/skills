from __future__ import annotations

import json

import pytest

from tests.support import REPOSITORY_ROOT

REFERENCES = REPOSITORY_ROOT / "skills/calibration/references"


@pytest.mark.parametrize(
    ("path", "sources"),
    [
        (
            "naming.md",
            (
                "https://peps.python.org/pep-0008/#naming-conventions",
                "https://rust-lang.github.io/api-guidelines/naming.html",
                "https://style.tidyverse.org/syntax.html#object-names",
                "https://semver.org/",
                "https://packaging.python.org/en/latest/discussions/versioning/",
                "https://packaging.python.org/en/latest/discussions/single-source-version/",
                "https://www.gnu.org/prep/standards/html_node/"
                "Command_002dLine-Interfaces.html",
                "https://www.gnu.org/prep/standards/html_node/Option-Table.html",
                "https://clig.dev/",
                "https://google.aip.dev/140",
                "https://protobuf.dev/programming-guides/json/"
                "#field-names-as-json-keys",
                "https://google.github.io/styleguide/jsoncguide.html"
                "#property-name-format",
                "https://www.sqlstyle.guide/#naming-conventions",
                "https://datapackage.org/standard/table-schema/",
            ),
        ),
        (
            "linters/ruff.md",
            (
                "https://docs.astral.sh/ruff/linter/#rule-selection",
                "https://docs.astral.sh/ruff/rules/",
            ),
        ),
    ],
)
def test_adopted_upstream_sources_remain_linked(
    path: str, sources: tuple[str, ...]
) -> None:
    text = (REFERENCES / path).read_text(encoding="utf-8")
    for source in sources:
        assert f"]({source})" in text


def test_naming_is_consolidated_into_a_single_reference() -> None:
    assert (REFERENCES / "naming.md").is_file()
    assert not (REFERENCES / "naming").exists()
    skill = (REFERENCES.parent / "SKILL.md").read_text(encoding="utf-8")
    assert "`references/naming.md`" in skill
    assert "references/naming/" not in skill


def test_indexes_keep_direct_routes_and_repository_naming_fallback() -> None:
    discipline = (REFERENCES / "discipline/README.md").read_text(encoding="utf-8")
    assert "## Related References" not in discipline
    assert "../design/" not in discipline
    assert "../docs/" not in discipline
    skill = (REFERENCES.parent / "SKILL.md").read_text(encoding="utf-8")
    assert "`references/design/codebase.md`" in skill
    assert "`references/docs/project-layout.md`" in skill
    naming = " ".join((REFERENCES / "naming.md").read_text(encoding="utf-8").split())
    assert (
        "If no applicable source is available, follow the nearest "
        "existing repository convention" in naming
    )
    assert "state the gap" not in naming


def test_retired_docs_index_is_not_shipped_or_routed() -> None:
    assert not (REFERENCES / "docs_index.md").exists()
    assert not (REFERENCES / "docs/document-types").exists()
    for path in REFERENCES.parent.rglob("*.md"):
        assert "docs_index.md" not in path.read_text(encoding="utf-8"), path
    skill = (REFERENCES.parent / "SKILL.md").read_text(encoding="utf-8")
    assert "`references/docs/project-layout.md`" in skill


def test_retired_collaboration_guide_is_not_shipped_or_routed() -> None:
    retired = "docs/workflow/branch_and_pr_collaboration/20260602-v1.0.md"
    assert not (REFERENCES / retired).exists()
    for path in REFERENCES.parent.rglob("*.md"):
        content = path.read_text(encoding="utf-8")
        assert "branch_and_pr_collaboration/" not in content, path


def test_cli_and_schema_naming_preserve_authority_and_surface_rules() -> None:
    body = " ".join((REFERENCES / "naming.md").read_text(encoding="utf-8").split())
    for rule in (
        "Preserve published compatibility",
        "Follow repository conventions and the API being extended",
        "For GNU-style interfaces",
        "for argument syntax and standard option names",
        "Consult [CLI Guidelines](https://clig.dev/) when the decision involves "
        "usability or interaction",
        "For new long options without an established convention, default to "
        "lowercase kebab-case",
        "Follow the target protocol and consumer schema, including native "
        "serialization mappings",
        "- Protobuf:",
        "New JSON interfaces without an adopted naming style",
        "as the naming default",
        "- SQL: follow the database or ORM rules",
        "The database governs identifier limits, quoting, and reserved words",
        "- Tabular exports:",
        "Preserve source or consumer names",
        "do not require adopting new formats or frameworks",
        "Assess published field changes for compatibility",
        "](discipline/verification.md)",
    ):
        assert rule in body
    assert "at explicit adapters" not in body
    assert "default to lowercase snake_case" not in body


def test_schema_cases_cover_defaults_native_mappings_and_existing_contracts() -> None:
    path = REFERENCES.parent / "test-prompts.json"
    cases = {case["id"]: case for case in json.loads(path.read_text(encoding="utf-8"))}
    for case_id, requirements in {
        41: ("AIP-140", "displayName", "native serializer", "new adapter"),
        42: ("Google JSON", "lowerCamelCase", "framework"),
        43: ("Keep the adopted", "not rename", "consumer schema"),
        44: ("actual database", "global 30-byte", "word separation"),
        45: ("Table Schema", "human-readable", "case conversion"),
    }.items():
        for requirement in requirements:
            assert requirement in cases[case_id]["expected"]
