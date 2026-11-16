from __future__ import annotations

import json

import pytest

from tests.support import REPOSITORY_ROOT

REFERENCES = REPOSITORY_ROOT / "skills/calibration/references"


@pytest.mark.parametrize(
    ("path", "sources"),
    [
        (
            "naming/README.md",
            (
                "https://peps.python.org/pep-0008/#naming-conventions",
                "https://rust-lang.github.io/api-guidelines/naming.html",
                "https://style.tidyverse.org/syntax.html#object-names",
            ),
        ),
        (
            "naming/version.md",
            (
                "https://semver.org/",
                "https://packaging.python.org/en/latest/discussions/versioning/",
                "https://packaging.python.org/en/latest/discussions/single-source-version/",
            ),
        ),
        (
            "naming/cli.md",
            (
                "https://www.gnu.org/prep/standards/html_node/"
                "Command_002dLine-Interfaces.html",
                "https://www.gnu.org/prep/standards/html_node/Option-Table.html",
                "https://clig.dev/",
            ),
        ),
        (
            "naming/schema.md",
            (
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


def test_current_naming_routes_reach_their_owning_sources() -> None:
    naming = REFERENCES / "naming"
    index = (naming / "README.md").read_text(encoding="utf-8")
    for target in (
        "cli.md",
        "version.md",
        "schema.md",
    ):
        assert f"]({target})" in index
        assert (naming / target).is_file()
    skill = (REFERENCES.parent / "SKILL.md").read_text(encoding="utf-8")
    assert "`references/naming/README.md`" in skill


def test_retired_naming_paths_are_not_shipped() -> None:
    for name in ("function", "method", "type", "variable", "loop", "branch"):
        assert not (REFERENCES / f"naming/{name}.md").exists()
    assert not (REFERENCES / "naming/artifact.md").exists()


def test_docs_compatibility_pointer_reaches_direct_routes() -> None:
    index = (REFERENCES / "docs_index.md").read_text(encoding="utf-8")
    assert "](../SKILL.md#route)" in index
    skill = (REFERENCES.parent / "SKILL.md").read_text(encoding="utf-8")
    assert "`references/docs/document-types/README.md`" in skill


def test_retired_collaboration_guide_is_not_shipped_or_routed() -> None:
    retired = "docs/workflow/branch_and_pr_collaboration/20260602-v1.0.md"
    assert not (REFERENCES / retired).exists()
    for path in REFERENCES.parent.rglob("*.md"):
        content = path.read_text(encoding="utf-8")
        assert "branch_and_pr_collaboration/" not in content, path


def test_cli_naming_scopes_sources_and_inherits_authority() -> None:
    path = REFERENCES / "naming/cli.md"
    cli = " ".join(path.read_text(encoding="utf-8").split())
    assert "](README.md#authority)" in cli
    assert "For GNU-style interfaces" in cli
    assert "for argument syntax and standard option names" in cli
    assert (
        "Consult [CLI Guidelines](https://clig.dev/) when the decision involves "
        "usability or interaction" in cli
    )
    assert (
        "For new long options without an established convention, default to "
        "lowercase kebab-case" in cli
    )
    for retired in ("native spelling", "Local additions", "Use operands", "--output"):
        assert retired not in cli
    authority = " ".join(
        (REFERENCES / "naming/README.md").read_text(encoding="utf-8").split()
    )
    assert "Preserve published compatibility" in authority
    assert "Follow repository conventions and the API being extended" in authority


def test_schema_naming_routes_by_surface_without_a_global_case_rule() -> None:
    body = " ".join(
        (REFERENCES / "naming/schema.md").read_text(encoding="utf-8").split()
    )
    for rule in (
        "](README.md#authority)",
        "target protocol and consumer schema, including native serialization mappings",
        "Consult only the source relevant to the current surface",
        "- Protobuf:",
        "New JSON interfaces without an adopted naming style",
        "as the naming default",
        "- SQL: follow the database or ORM rules",
        "The database governs identifier limits, quoting, and reserved words",
        "- Tabular exports:",
        "field names, human-readable titles, and column correspondence",
        "Preserve source or consumer names",
        "do not require adopting new formats or frameworks",
        "identity, uniqueness, stability, and cross-system mapping requirements",
        "reversibility and encoding are choices of the owning contract",
        "Assess published field changes for compatibility",
        "at the owning serialization or integration boundary",
        "](../discipline/verification.md)",
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
