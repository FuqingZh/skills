"""Validate v4 diagnostics and frozen v3 reuse without model calls."""

from __future__ import annotations

import copy
import json
import runpy
from pathlib import Path
from typing import Any

import pytest

ROOT = (
    Path(__file__).resolve().parents[1]
    / "evaluations/communication-style/preference-calibration"
)
MOD = runpy.run_path(str(ROOT / "judge_v4.py"))
GLOBALS = MOD["execute"].__globals__
FIXTURE = runpy.run_path(str(Path(__file__).with_name("test_preference_judge.py")))[
    "judgment"
]


def judgment() -> dict[str, Any]:
    value = FIXTURE()
    value["checks"] = {
        side: {
            dimension: {"status": "clear", "reason": "Fixture", "evidence": []}
            for dimension in MOD["BASE"]["DIMENSIONS"]
        }
        for side in ("A", "B")
    }
    value["deletion_audit"] = {"A": [], "B": []}
    return value


def test_checks_require_each_dimension_and_match_issues() -> None:
    payload = {"answers": {"A": {"A1": "alpha"}, "B": {"B1": "beta"}}}
    value = judgment()
    assert MOD["validate"](value, payload) == {}
    value["checks"]["A"]["response"].update(status="issue", evidence=["A1"])
    with pytest.raises(ValueError, match="Checks and issues disagree"):
        MOD["validate"](value, payload)
    value["issues"]["A"] = [
        {"dimension": "response", "reason": "Fixture", "evidence": ["A1"]}
    ]
    assert MOD["validate"](value, payload) == {"A1": "alpha"}
    del value["checks"]["B"]["naturalness"]
    with pytest.raises(ValueError, match="fields"):
        MOD["validate"](value, payload)


@pytest.mark.parametrize("defect", ["cross", "status", "defense", "audit", "shared"])
def test_rejects_inconsistent_or_incomplete_diagnostics(defect: str) -> None:
    payload = {"answers": {"A": {"A1": "alpha"}, "B": {"B1": "beta"}}}
    value = judgment()
    if defect == "cross":
        value["checks"]["A"]["response"]["evidence"] = ["B1"]
    elif defect == "status":
        value["checks"]["A"]["response"]["status"] = "okay"
    elif defect == "defense":
        value["checks"]["A"]["self_defense"]["status"] = "uncertain"
    elif defect == "audit":
        value["deletion_audit"]["A"] = [{"evidence": ["A1"]}]
    else:
        value["shared_issues"] = [{"reason": "Fixture", "evidence": ["A1", "B1"]}]
    with pytest.raises(ValueError):
        MOD["validate"](value, payload)


def test_deletion_audit_keeps_exact_paragraphs() -> None:
    value = judgment()
    value["deletion_audit"]["A"] = [
        {
            "evidence": ["A1"],
            "target": "Fixture",
            "already_known": "Fixture",
            "increment": "Fixture",
            "lost_if_deleted": "Fixture",
            "verdict": "keep",
        }
    ]
    payload = {"answers": {"A": {"A1": "**alpha**"}, "B": {"B1": "beta"}}}
    assert MOD["validate"](value, payload) == {"A1": "**alpha**"}


def test_summary_restores_v3_namespace(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    namespace = MOD["BASE"]["summarize"].__globals__
    before = {key: namespace[key] for key in ("verify", "validate", "OUTPUT")}
    monkeypatch.setitem(GLOBALS, "OUTPUT", tmp_path)
    result = MOD["summarize"]()
    assert result["version"] == 4
    assert result["primary"]["eligible"] == result["primary"]["unavailable"] == 7
    assert result["attempts_present"] == 0
    assert all(namespace[key] is value for key, value in before.items())
    assert MOD["BASE"]["summarize"]() == MOD["BASE"]["read_json"]("summary-v3.json")


def test_v4_invocations_use_new_prompt_and_keep_invalid_outputs(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    output = tmp_path / "outputs"
    monkeypatch.setitem(GLOBALS, "OUTPUT", output)
    prompts: list[str] = []

    def invoke(system: str, *args: Any) -> dict[str, Any]:
        prompts.append(system)
        return {"answer": "bad JSON"}

    def version(*args: Any, **kwargs: Any) -> str:
        return "test"

    monkeypatch.setitem(MOD["CORE"], "invoke", invoke)
    monkeypatch.setattr(MOD["subprocess"], "check_output", version)
    MOD["execute"]()
    assert len(prompts) == 24
    assert all(prompt == (ROOT / "judge-v4.txt").read_text() for prompt in prompts)
    assert MOD["summarize"]()["primary"]["unavailable"] == 7
    with pytest.raises(FileExistsError):
        MOD["execute"]()
    assert len(prompts) == 24
    run = json.loads((output / "run.json").read_text())
    assert run["protocol"]["version"] == 4


def test_manifest_must_match(monkeypatch: pytest.MonkeyPatch) -> None:
    before = MOD["hashes"]()
    assert MOD["verify"]()["version"] == 4

    def changed() -> dict[str, str]:
        result = copy.deepcopy(before)
        result["judge-v4.txt"] = "changed"
        return result

    monkeypatch.setitem(GLOBALS, "hashes", changed)
    with pytest.raises(ValueError, match="Frozen v4"):
        MOD["verify"]()
