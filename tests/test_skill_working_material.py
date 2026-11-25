"""Static skill contracts and synthetic cases; no model calls or evidence migration."""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

from tests.support import REPOSITORY_ROOT

SKILLS = REPOSITORY_ROOT / "skills"
DISSECT = SKILLS / "dissect"
LAYOUT = SKILLS / "calibration/references/docs/project-layout.md"


def compact(path: Path) -> str:
    return " ".join(path.read_text(encoding="utf-8").split())


def test_dissect_discloses_topics_and_persistence_by_condition() -> None:
    core = compact(DISSECT / "SKILL.md")
    references = re.findall(r"`(references/[^`]+\.md)`", core)
    assert set(references) == {
        "references/actors-and-interactions.md",
        "references/historical-change.md",
        "references/working-material.md",
    }
    assert len(references) == len(set(references))
    assert all((DISSECT / reference).is_file() for reference in references)
    for rule in (
        "Load only the references needed",
        "When the conclusion depends on actors' choices",
        "When assessing an event's long-term structural or historical effects",
        "When asked to retain research working material",
        "A person's mention alone does not require an actor model",
        "mathematical analysis can use the core method without these topic references",
        "Attribute claims accurately",
        "do not invent support",
        "For forecasts or judgments about future developments, compare the relative "
        "likelihood of possible paths",
        "Develop a continuous explanation",
    ):
        assert rule in core
    assert "build actor profiles" not in core
    assert "anticipate subsequent paths" not in core
    assert "changes that define an era" not in core
    actors = compact(DISSECT / "references/actors-and-interactions.md")
    for rule in (
        "what they want, believe, can do, and are most likely to choose",
        "independent investigation, distributed disclosures",
        "how it changes expectations",
        "explaining how their choices vary across situations",
    ):
        assert rule in actors
    history = compact(DISSECT / "references/historical-change.md")
    assert "production and organization, institutions" in history
    assert "compare plausible counterfactuals" in history
    assert "empirical basis, and values" in history


def test_explanation_rules_prohibit_added_objections_without_hiding_failures() -> None:
    core = compact(DISSECT / "SKILL.md")
    prose = compact(SKILLS / "plainspoken/SKILL.md")
    assert "without adding your own objections, corrections" in core
    assert "judgments about its adequacy or acceptability" in core
    assert "Explain source-internal disagreements as part of the argument" in core
    assert "not as a fixed outline or required headings" in core
    assert "without adding corrective commentary or reminders" in prose
    assert "whether to accept it" in prose
    assert "Report failures and permission or capability limits accurately" in prose
    assert "weigh the support and relevant objections" not in core
    assert (
        "Test profiles against different situations and counterexamples"
        not in compact(DISSECT / "references/actors-and-interactions.md")
    )


@pytest.mark.parametrize(
    ("path", "notes", "evidence"),
    [
        (LAYOUT, ".calibration/notes/", ".calibration/evidence/"),
        (
            DISSECT / "references/working-material.md",
            ".dissect/notes/",
            ".dissect/evidence/",
        ),
    ],
)
def test_skill_working_locations_preserve_local_authority_and_evidence(
    path: Path, notes: str, evidence: str
) -> None:
    body = compact(path)
    assert f"`{notes}`" in body
    assert f"`{evidence}`" in body
    assert "repository" in body
    assert "unless repository" in body
    assert "publication rights" in body
    assert "access controls" in body
    assert ".traces/" not in body
    assert "Create only the files and directories needed" in body


def test_skills_without_working_material_do_not_acquire_storage_defaults() -> None:
    for name in ("plainspoken", "writing-code-docs"):
        assert f".{name}/" not in compact(SKILLS / name / "SKILL.md")
    assert "Formal project documents remain project-owned" in compact(LAYOUT)
    assert "Formal reports remain" in compact(
        DISSECT / "references/working-material.md"
    )
    assert "investigation working material" in compact(SKILLS / "calibration/SKILL.md")


def test_code_doc_format_fallback_preserves_material_gap_reporting() -> None:
    body = compact(SKILLS / "writing-code-docs/SKILL.md")
    assert (
        "For other languages without a local convention, use the official "
        "documentation convention when one is available." in body
    )
    assert "state the gap before choosing a format" not in body
    assert "State material gaps rather than inventing behavior" in body


def test_code_examples_cover_contracts_with_local_per_symbol_overrides() -> None:
    body = compact(SKILLS / "writing-code-docs/SKILL.md")
    for rule in (
        "Cover each distinct caller-facing usage contract",
        "short, locatable example",
        "parameter interactions, boundary results, exceptions, and side effects",
        "Simple properties, aliases",
        "point to a shared example on their owning type or API",
        "Cover any distinct behavior that the shared example does not demonstrate",
        "Follow repository rules that explicitly require an example "
        "for every public symbol",
        "Show each distinct public consequence once",
    ):
        assert rule in body
    assert "even when its contract is simple" not in body
    assert "Give every caller-facing" not in body
    case_path = SKILLS / "writing-code-docs/test-prompts.json"
    cases = {case["id"]: case for case in json.loads(case_path.read_text())}
    assert "shared example" in cases[8]["expected"]
    assert "explicit repository per-symbol rule" in cases[9]["expected"]
    assert "exception, and side effect" in cases[10]["expected"]


def test_dissect_cases_cover_conditional_loading_and_local_storage() -> None:
    cases = {
        case["id"]: case
        for case in json.loads((DISSECT / "test-prompts.json").read_text())
    }
    assert "mentioning a director alone" in cases["D01"]["expected"]
    assert "Read references/actors-and-interactions.md" in cases["D02"]["expected"]
    assert "Read references/historical-change.md" in cases["D03"]["expected"]
    assert "without loading" in cases["D05"]["expected"]
    assert (
        "testable predictions tied to the candidate mechanisms"
        in cases["D05"]["expected"]
    )
    assert "conditional predictions with observable signals" in cases["D02"]["expected"]
    assert "Do not append future scenarios" in cases["D07"]["expected"]
    assert "explicit cost assumptions" in cases["D07"]["expected"]
    assert cases["D07"]["expected_skills"] == ["plainspoken", "dissect"]
    assert "Read references/working-material.md" in cases["D06"]["expected"]
    assert (
        "research/working/ rather than creating .dissect/notes/"
        in cases["D06"]["expected"]
    )
    assert "without copying" in cases["D06"]["expected"]
