"""Offline invariants for sentence deletion, blind scoring and source freezing."""

from __future__ import annotations

import copy
import json
import runpy
import subprocess
from pathlib import Path
from typing import Any

import pytest

ROOT = (
    Path(__file__).resolve().parents[1]
    / "evaluations/communication-style/sentence-ablation"
)
BENCH = runpy.run_path(str(ROOT / "benchmark.py"))


def test_exact_deletions_and_case_identity() -> None:
    core = BENCH["engine"]()
    BENCH["verify"](core)
    spec = core["read_json"](ROOT / "sentences.json")
    original = (ROOT.parent / "cross-domain/prompts/revised.txt").read_text()
    sentences = [s["text"] for s in spec["sentences"]]
    assert " ".join(original.split()) == " ".join(sentences)
    for arm, removed in spec["arms"].items():
        prompt = (ROOT / f"prompts/{arm}.txt").read_text()
        expected = " ".join(
            [
                spec["anchor"],
                *[text for i, text in enumerate(sentences, 1) if i not in removed],
            ]
        )
        assert " ".join(prompt.split()) == expected
    assert len(spec["arms"]) == 10
    cases = core["read_json"](ROOT / "cases.json")
    original_cases = core["read_json"](ROOT.parent / "cross-domain/cases.json")
    assert [
        {k: v for k, v in c.items() if k != "dimensions"} for c in cases
    ] == original_cases
    assert len(cases) == 8
    assert all(set(c["dimensions"]) <= set(BENCH["DIMENSIONS"]) for c in cases)


def fixture(case: dict[str, Any], answers: list[dict[str, str]]) -> dict[str, Any]:
    return {
        "ratings": [
            {
                "id": a["id"],
                "content": [
                    {"index": i, "met": True, "reason": "fixture"}
                    for i in range(len(case["required"]))
                ],
                "critical": [],
                "style": [],
                "clarity": "clear",
                "clarity_reason": "fixture",
                "quality": {
                    d: {"score": 4, "quote": "", "reason": "fixture"}
                    for d in case["dimensions"]
                },
            }
            for a in answers
        ]
    }


@pytest.mark.parametrize("bad", [True, -1, 5, 3.5, "3"])
def test_score_type_and_bounds(bad: object) -> None:
    core = BENCH["engine"]()
    case = core["read_json"](ROOT / "controls.json")[0]
    record = fixture(case, case["answers"])
    record["ratings"][0]["quality"]["progression"]["score"] = bad
    with pytest.raises(ValueError, match="Invalid quality evidence"):
        BENCH["validate"](core, case, case["answers"], record)


def test_deficiency_requires_answer_specific_evidence() -> None:
    core = BENCH["engine"]()
    case = core["read_json"](ROOT / "controls.json")[0]
    record = fixture(case, case["answers"])
    BENCH["validate"](core, case, case["answers"], record)
    for quote in ("", "fabricated"):
        wrong = copy.deepcopy(record)
        wrong["ratings"][0]["quality"]["progression"].update(score=3, quote=quote)
        with pytest.raises(ValueError, match="Invalid quality evidence"):
            BENCH["validate"](core, case, case["answers"], wrong)
    del record["ratings"][0]["quality"]["progression"]
    with pytest.raises(ValueError, match="Incomplete quality"):
        BENCH["validate"](core, case, case["answers"], record)


def test_generate_isolated_160_and_blind_packets(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = runpy.run_path(str(ROOT / "benchmark.py"))
    module["packets"].__globals__["ROOT"] = tmp_path
    core = BENCH["engine"]()
    for name in ("protocol.json", "cases.json", "execution-manifest.json"):
        (tmp_path / name).write_bytes((ROOT / name).read_bytes())
    calls: list[tuple[str, str]] = []

    def invoke(
        system: str, prompt: str, config: dict[str, Any], cwd: str, timeout: int
    ) -> dict[str, Any]:
        assert Path(cwd).is_dir() and not list(Path(cwd).iterdir())
        assert config["model"] == "gpt-6-astra" and timeout == 300
        calls.append((system, prompt))
        return {
            "answer": "fixture",
            "characters": 7,
            "model": "gpt-6-astra",
            "provider": "openai",
            "usage": {"cost": {"total": 0}},
            "seconds": 0,
        }

    core["generate"].__globals__["invoke"] = invoke

    def version(*args: object, **kwargs: object) -> str:
        return "fixture\n"

    monkeypatch.setattr(subprocess, "check_output", version)
    arms = core["read_json"](ROOT / "protocol.json")["arms"]
    output = tmp_path / "results/benchmark"
    core["generate"]("benchmark", arms, output)
    assert len(calls) == 160
    assert {s for s, _ in calls} == {
        (ROOT / f"prompts/{a}.txt").read_text() for a in arms
    }
    packets = module["packets"](core)
    assert len(packets) == 16
    assert all(len(p["answers"]) == 10 and len(p["mapping"]) == 10 for p in packets)
    assert all(set(a) == {"id", "answer"} for p in packets for a in p["answers"])
    with pytest.raises(FileExistsError):
        core["generate"]("benchmark", arms, output)
    assert len(calls) == 160
    path = output / "p1-full-1.json"
    record = core["read_json"](path)
    record["error"] = "simulated failure"
    path.write_text(json.dumps(record))
    with pytest.raises(ValueError, match="Invalid generation"):
        module["packets"](core)


def test_control_failures_are_preserved_and_expected_labels_hidden(
    tmp_path: Path,
) -> None:
    module = runpy.run_path(str(ROOT / "benchmark.py"))
    module["calibrate"].__globals__["ROOT"] = tmp_path
    core = BENCH["engine"]()
    for name in (
        "controls.json",
        "protocol.json",
        "judge.txt",
        "execution-manifest.json",
    ):
        (tmp_path / name).write_bytes((ROOT / name).read_bytes())
    calls: list[str] = []

    def invoke(
        system: str, prompt: str, config: dict[str, Any], cwd: str, timeout: int
    ) -> dict[str, Any]:
        packet = json.loads(prompt)
        assert set(packet) == {
            "task",
            "required",
            "critical_examples",
            "dimensions",
            "answers",
        }
        calls.append(prompt)
        return {"error": "simulated transport failure"}

    core["invoke"] = invoke
    with pytest.raises(ValueError, match="Invalid control"):
        module["calibrate"](core)
    assert len(calls) == 3
    assert len(list((tmp_path / "results/controls").glob("*.json"))) == 3
    with pytest.raises(FileExistsError):
        module["calibrate"](core)
    assert len(calls) == 3


def test_cluster_interval_constant_and_zero_crossing() -> None:
    assert BENCH["interval"]([2.0] * 8) == [2.0, 2.0]
    low, high = BENCH["interval"]([-2.0, 2.0] * 4)
    assert low < 0 < high
