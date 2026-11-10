"""Offline contract checks for the five-check preference judge."""

from __future__ import annotations

import copy
import json
import runpy
from collections import Counter
from pathlib import Path
from typing import Any

import pytest

ROOT = (
    Path(__file__).resolve().parents[1]
    / "evaluations/communication-style/preference-calibration"
)
MOD = runpy.run_path(str(ROOT / "judge_v3.py"))
GLOBALS = MOD["execute"].__globals__


def judgment(choice: str = "tie") -> dict[str, Any]:
    return {
        "choice": choice,
        "reason": "Fixture reason",
        "issues": {"A": [], "B": []},
        "shared_issues": [],
        "strengths": {"A": [], "B": []},
        "content_issues": {"A": [], "B": []},
        "self_defense": {
            side: {
                "status": "absent",
                "target": "none",
                "increment": "none",
                "deletion": "none",
                "evidence": [],
            }
            for side in ("A", "B")
        },
    }


def test_admission_and_request_blinding() -> None:
    meta = MOD["materials"]()
    assert len(meta) == 24
    assert meta["D09"]["category"] == "correctness"
    assert meta["D03"]["category"] == "mixed"
    assert Counter(row["category"] for row in meta.values()) == {
        "style": 15,
        "mixed": 5,
        "correctness": 4,
    }
    jobs = MOD["jobs"]()
    assert len(jobs) == 24
    assert all(job["id"] != "D09" and not job["id"].startswith("H") for job in jobs)
    assert all(set(job["payload"]) == {"context", "answers"} for job in jobs)
    assert len({(job["id"], job["order"]) for job in jobs}) == 24
    assert MOD["verify"]()["max_calls"] == 24


def test_swap_is_an_involution_and_preserves_markdown() -> None:
    for row in MOD["materials"]().values():
        item = row["item"]
        assert MOD["swapped"](MOD["swapped"](item)) == item
    for choice, expected in (
        ("A", "B"),
        ("B", "A"),
        ("tie", "tie"),
        ("uncertain", "uncertain"),
    ):
        assert MOD["normalize"](choice, "swapped") == expected
        assert MOD["normalize"](choice, "original") == choice


def test_empty_findings_are_valid_and_evidence_is_extracted() -> None:
    payload = {"answers": {"A": {"A1": "**alpha**"}, "B": {"B1": "beta"}}}
    value = judgment()
    assert MOD["validate"](value, payload) == {}
    value["issues"]["A"] = [
        {
            "dimension": "self_defense",
            "reason": "Fixture",
            "evidence": ["A1"],
        }
    ]
    value["self_defense"]["A"]["status"] = "present"
    value["self_defense"]["A"]["evidence"] = ["A1"]
    value["shared_issues"] = [{"reason": "Fixture", "evidence": ["A1", "B1"]}]
    assert MOD["validate"](value, payload) == {"A1": "**alpha**", "B1": "beta"}


@pytest.mark.parametrize(
    "defect",
    [
        "unknown",
        "choice",
        "reason",
        "side",
        "reference",
        "duplicate",
        "shared",
        "present",
        "dimension",
    ],
)
def test_rejects_invalid_judgments(defect: str) -> None:
    payload = {"answers": {"A": {"A1": "alpha"}, "B": {"B1": "beta"}}}
    value = judgment()
    if defect == "unknown":
        value["extra"] = 1
    elif defect == "choice":
        value["choice"] = "neither"
    elif defect == "reason":
        value["reason"] = " "
    elif defect == "shared":
        value["shared_issues"] = [{"reason": "Fixture", "evidence": ["A1"]}]
    elif defect == "present":
        value["self_defense"]["A"]["status"] = "present"
    else:
        refs = {
            "side": ["B1"],
            "reference": ["A9"],
            "duplicate": ["A1", "A1"],
            "dimension": ["A1"],
        }[defect]
        value["issues"]["A"] = [
            {
                "dimension": "bogus" if defect == "dimension" else "response",
                "reason": "Fixture",
                "evidence": refs,
            }
        ]
    with pytest.raises(ValueError):
        MOD["validate"](value, payload)


def test_freeze_detects_source_change(monkeypatch: pytest.MonkeyPatch) -> None:
    def empty_hashes() -> dict[str, str]:
        return {}

    monkeypatch.setitem(GLOBALS, "hashes", empty_hashes)
    with pytest.raises(ValueError, match="Frozen source"):
        MOD["verify"]()


def test_admission_cannot_omit_or_duplicate(monkeypatch: pytest.MonkeyPatch) -> None:
    original = MOD["read_json"]
    bad = copy.deepcopy(original("admission-v3.json"))
    bad["pairs"].append(bad["pairs"][0])

    def read(name: str) -> Any:
        return bad if name == "admission-v3.json" else original(name)

    monkeypatch.setitem(GLOBALS, "read_json", read)
    with pytest.raises(ValueError, match="admission"):
        MOD["materials"]()


def test_failed_attempts_are_kept_and_not_retried(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    output = tmp_path / "results"
    monkeypatch.setitem(GLOBALS, "OUTPUT", output)
    calls: list[str] = []

    def invoke(*args: Any) -> dict[str, Any]:
        calls.append(args[1])
        return {"answer": "malformed", "usage": {"totalTokens": 2}}

    monkeypatch.setitem(MOD["CORE"], "invoke", invoke)

    def version(*args: Any, **kwargs: Any) -> str:
        return "test"

    monkeypatch.setattr(MOD["subprocess"], "check_output", version)
    MOD["execute"]()
    assert len(calls) == 24
    assert len(list(output.glob("*.json"))) == 25
    summary = MOD["summarize"]()
    assert summary["attempts_present"] == 24
    assert summary["primary"]["eligible"] == 7
    assert summary["primary"]["unavailable"] == 7
    assert summary["total_tokens"] == 48
    with pytest.raises(FileExistsError):
        MOD["execute"]()
    assert len(calls) == 24


def test_summary_separates_mixed_unknown_missing_and_order_conflicts(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setitem(GLOBALS, "OUTPUT", tmp_path)
    labels = {
        row["id"]: row["choice"]
        for row in MOD["read_json"]("labels.round-1.json")["ratings"]
    }
    for job in MOD["jobs"]():
        if job["id"] == "D05":
            continue
        choice = labels.get(job["id"]) or "tie"
        if job["order"] == "swapped" and job["id"] != "D04":
            choice = MOD["normalize"](choice, "swapped")
        value = judgment(choice)
        record = {
            **job,
            "answer": json.dumps(value),
            "judgment": value,
            "evidence_text": {},
        }
        MOD["CORE"]["save_new"](tmp_path / f"{job['id']}-{job['order']}.json", record)
    result = MOD["summarize"]()
    assert result["primary"] == {
        "eligible": 7,
        "agree": 5,
        "disagree": 0,
        "conflict": 1,
        "unavailable": 1,
        "uncertain": 0,
    }
    rows = {row["id"]: row for row in result["rows"]}
    assert rows["D03"]["human"] == "B"
    assert rows["D03"]["primary_agreement"] is None
    assert rows["D08"]["human"] is None
    assert rows["I01"]["prediction"] == "tie"


def test_saved_v3_run_reproduces_without_model_calls() -> None:
    saved = MOD["read_json"]("summary-v3.json")
    assert MOD["summarize"]() == saved
    assert saved["attempts_present"] == saved["expected_attempts"] == 24
    assert saved["primary"] == {
        "eligible": 7,
        "agree": 4,
        "disagree": 1,
        "conflict": 2,
        "unavailable": 0,
        "uncertain": 0,
    }
    run = MOD["read_json"]("results-v3/run.json")
    assert run["manifest"] == MOD["read_json"]("manifest-v3.json")
    assert {(row["id"], row["order"]) for row in run["jobs"]} == {
        (row["id"], row["order"]) for row in MOD["jobs"]()
    }
    for job in MOD["jobs"]():
        record = MOD["read_json"](f"results-v3/{job['id']}-{job['order']}.json")
        assert "error" not in record
        assert record["model"] == run["protocol"]["judge"]["model"]
        assert record["provider"] == run["protocol"]["judge"]["provider"]
