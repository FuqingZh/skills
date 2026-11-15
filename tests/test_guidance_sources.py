from __future__ import annotations

import pytest

from tests.support import REPOSITORY_ROOT

REFERENCES = REPOSITORY_ROOT / "skills/calibration/references"
BRANCH_GUIDE = "docs/workflow/branch_and_pr_collaboration/20260602-v1.0.md"
GITHUB_BRANCHES = (
    "https://docs.github.com/en/repositories/"
    "configuring-branches-and-merges-in-your-repository/"
)


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
                "https://semver.org/spec/v2.0.0.html",
                "https://packaging.python.org/en/latest/discussions/versioning/",
                "https://packaging.python.org/en/latest/discussions/single-source-version/",
            ),
        ),
        (
            BRANCH_GUIDE,
            (
                "https://docs.github.com/en/get-started/using-github/github-flow",
                GITHUB_BRANCHES
                + "managing-protected-branches/about-protected-branches",
                GITHUB_BRANCHES
                + "configuring-pull-request-merges/managing-a-merge-queue",
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
        "artifact.md",
        f"../{BRANCH_GUIDE}",
    ):
        assert f"]({target})" in index
        assert (naming / target).is_file()
    skill = (REFERENCES.parent / "SKILL.md").read_text(encoding="utf-8")
    assert "`references/naming/README.md`" in skill


def test_retired_naming_paths_are_not_shipped() -> None:
    for name in ("function", "method", "type", "variable", "loop", "branch"):
        assert not (REFERENCES / f"naming/{name}.md").exists()


def test_docs_compatibility_pointer_reaches_direct_routes() -> None:
    index = (REFERENCES / "docs_index.md").read_text(encoding="utf-8")
    assert "](../SKILL.md#route)" in index
    skill = (REFERENCES.parent / "SKILL.md").read_text(encoding="utf-8")
    assert f"`references/{BRANCH_GUIDE}`" in skill


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
