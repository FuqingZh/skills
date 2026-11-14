"""Static skill packaging and routing fixtures; these tests make no model calls."""

from __future__ import annotations

import json
from typing import TypedDict, cast

import pytest
import yaml

from scripts.validate_skills import discover_skills
from tests.support import REPOSITORY_ROOT

SKILLS = ("plainspoken", "dissect")


class RoutingCase(TypedDict):
    id: str
    scenario: str
    prompt: str
    expected: str
    expected_skills: list[str]


def test_global_template_contains_only_three_skill_routes() -> None:
    template = (REPOSITORY_ROOT / "templates/AGENTS.md.template").read_text()
    assert template == (
        "# Global AGENTS.md\n\n"
        "Use `plainspoken` for substantive natural-language responses.\n"
        "Use `dissect` for tasks requiring in-depth analysis.\n"
        "Use `calibration` when its scope matches the task.\n"
    )


@pytest.mark.parametrize("name", SKILLS)
def test_new_skills_are_discoverable_and_implicitly_invocable(name: str) -> None:
    directory = REPOSITORY_ROOT / "skills" / name
    assert directory in discover_skills(REPOSITORY_ROOT)
    _, frontmatter, body = (directory / "SKILL.md").read_text().split("---", 2)
    metadata = cast(dict[str, object], yaml.safe_load(frontmatter))
    assert metadata["name"] == name
    assert metadata.get("disable-model-invocation", False) is False
    description = metadata["description"]
    assert isinstance(description, str) and description.startswith("Use ")

    client = cast(
        dict[str, dict[str, object]],
        yaml.safe_load((directory / "agents/openai.yaml").read_text()),
    )
    assert client["policy"]["allow_implicit_invocation"] is True
    default_prompt = client["interface"]["default_prompt"]
    assert isinstance(default_prompt, str) and f"${name}" in default_prompt
    other = next(skill for skill in SKILLS if skill != name)
    assert f"${other}" not in body
    assert f"{other}/SKILL.md" not in body


@pytest.mark.parametrize("name", SKILLS)
def test_routing_fixtures_cover_applicable_combined_and_simple_tasks(name: str) -> None:
    cases = cast(
        list[RoutingCase],
        json.loads(
            (REPOSITORY_ROOT / "skills" / name / "test-prompts.json").read_text()
        ),
    )
    assert len({case["id"] for case in cases}) == len(cases)
    assert all(case["prompt"] and case["expected"] for case in cases)
    assert all(set(case["expected_skills"]) <= set(SKILLS) for case in cases)
    assert any(name in case["expected_skills"] for case in cases)
    assert any(not case["expected_skills"] for case in cases)
    assert any(set(case["expected_skills"]) == set(SKILLS) for case in cases)


@pytest.mark.parametrize("path", ("README.md", "README.zh-CN.md", "docs/README.md"))
def test_new_skills_are_linked_from_public_entrypoints(path: str) -> None:
    document = (REPOSITORY_ROOT / path).read_text()
    for name in SKILLS:
        assert f"skills/{name}/SKILL.md" in document
