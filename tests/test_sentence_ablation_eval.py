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


def test_summary_effect_signs_interaction_and_corrupt_raw(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = runpy.run_path(str(ROOT / "benchmark.py"))
    core = BENCH["engine"]()
    read = core["read_json"]
    cases = read(ROOT / "cases.json")
    protocol = read(ROOT / "protocol.json")
    records: dict[Path, Any] = {
        ROOT / "cases.json": cases,
        ROOT / "protocol.json": protocol,
        ROOT / "controls.json": [],
    }
    jobs: list[dict[str, Any]] = []
    for case in cases:
        for rep in (1, 2):
            answers = [
                {"id": f"R{i}", "answer": "fixture"}
                for i in range(len(protocol["arms"]))
            ]
            mapping = {
                a["id"]: f"{case['id']}-{arm}-{rep}"
                for a, arm in zip(answers, protocol["arms"], strict=True)
            }
            record = fixture(case, answers)
            for rating, arm in zip(record["ratings"], protocol["arms"], strict=True):
                for dimension, item in rating["quality"].items():
                    score = 4
                    if arm == "minimal":
                        score = 2
                    if arm == "drop1" and dimension == "plain_depth":
                        score = 3
                    if arm in {"drop6", "drop67"} and dimension == "no_self_defense":
                        score = 3
                    if arm in {"drop7", "drop67"} and dimension == "requested_meta":
                        score = 3
                    item.update(score=score, quote="fixture" if score < 4 else "")
                key = mapping[rating["id"]]
                records[ROOT / "results/benchmark" / f"{key}.json"] = {
                    "characters": 7,
                    "usage": {"cost": {"total": 0}},
                }
            record.update(
                mapping=mapping, answer=json.dumps(record), usage={"cost": {"total": 0}}
            )
            records[ROOT / "results/judgments" / f"{case['id']}-{rep}.json"] = record
            jobs.append(
                {"case": case, "rep": rep, "mapping": mapping, "answers": answers}
            )
    core["read_json"] = records.__getitem__

    def packets(_core: dict[str, Any]) -> list[dict[str, Any]]:
        return jobs

    monkeypatch.setitem(module["summarize"].__globals__, "packets", packets)
    result = module["summarize"](core)
    assert result["arms"]["full"]["score"] == 100
    assert result["paragraph_net"]["mean"] == 50
    assert result["effects"]["S1"]["overall"]["mean"] == pytest.approx(
        4.873511904761905
    )
    assert result["effects"]["S1"]["target"]["mean"] == 25
    assert result["effects"]["S7"]["target"]["mean"] == 25
    assert len(result["effects"]["S7"]["target"]["task_deltas"]) == 2
    assert result["interaction67"]["mean"] == pytest.approx(0, abs=1e-12)
    assert len(result["scores"]) == 160
    records[ROOT / "results/judgments/p1-1.json"]["answer"] = "invalid JSON"
    with pytest.raises(ValueError):
        module["summarize"](core)


def test_saved_artifacts_preserve_failures_and_reproduce_partial_summary() -> None:
    core = BENCH["engine"]()
    BENCH["verify"](core)
    BENCH["check_controls"](core)
    recovery = runpy.run_path(str(ROOT / "recovery.py"))
    with pytest.raises(ValueError, match="Invalid recovery record"):
        recovery["summarize"]()
    partial = runpy.run_path(str(ROOT / "partial.py"))["summarize"]()
    assert partial == core["read_json"](ROOT / "partial-summary.json")
    assert partial["full_study_scores"] is None
    assert partial["analysis_responses"] == 140
    assert "c1" not in partial["included_cases"]
    with pytest.raises(ValueError, match="Invalid judgment: c1-1"):
        BENCH["summarize"](core)
    with pytest.raises(FileExistsError, match="single retry already exists"):
        recovery["retry"]()
    assert len(list((ROOT / "results/retries").glob("*.json"))) == 1
    assert core["read_json"](ROOT / "summary.json")["status"] == "incomplete"
    valid = 0
    for job in BENCH["packets"](core):
        name = f"{job['case']['id']}-{job['rep']}"
        record = core["read_json"](ROOT / "results/judgments" / f"{name}.json")
        assert record["mapping"] == job["mapping"]
        if record.get("error"):
            assert name == "c1-1"
            retry = core["read_json"](ROOT / "results/retries/c1-1-attempt2.json")
            assert retry["mapping"] == job["mapping"]
            for failed in (record, retry):
                with pytest.raises(ValueError, match="Invalid quality evidence"):
                    BENCH["validate"](
                        core, job["case"], job["answers"], json.loads(failed["answer"])
                    )
            continue
        BENCH["validate"](core, job["case"], job["answers"], record)
        assert json.loads(record["answer"])["ratings"] == record["ratings"]
        valid += 1
    assert valid == 15
    assert len(list((ROOT / "results/benchmark").glob("*.json"))) == 161
    assert len(list((ROOT / "results/judgments").glob("*.json"))) == 16
    assert len(list((ROOT / "results/controls").glob("*.json"))) == 3
    for case in core["read_json"](ROOT / "controls.json"):
        record = core["read_json"](ROOT / "results/controls" / f"{case['id']}.json")
        assert json.loads(record["answer"])["ratings"] == record["ratings"]
