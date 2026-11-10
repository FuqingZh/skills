"""Offline contracts for the frozen cross-domain style experiment."""

from __future__ import annotations

import copy
import runpy
import subprocess
from pathlib import Path
from typing import Any

import pytest

BASE = Path(__file__).resolve().parents[1] / "evaluations/communication-style"
ROOT = BASE / "cross-domain"
BENCH = runpy.run_path(str(ROOT / "benchmark.py"))


def test_frozen_sources_and_balanced_cases() -> None:
    core = BENCH["engine"]()
    BENCH["verify"](core)
    cases = core["read_json"](ROOT / "cases.json")
    assert len(cases) == len({c["id"] for c in cases}) == 8
    assert {c["split"] for c in cases} == {"benchmark"}
    assert {c["domain"] for c in cases} == {
        "philosophy",
        "science",
        "sociology",
        "conversation",
    }
    for domain in {c["domain"] for c in cases}:
        assert sorted(c["length"] for c in cases if c["domain"] == domain) == [
            "long",
            "short",
        ]
    assert (ROOT / "prompts/baseline.txt").read_bytes() == (
        BASE / "prompts/baseline.txt"
    ).read_bytes()


def fixture_record(fixture: dict[str, Any]) -> dict[str, Any]:
    return {
        "ratings": [
            {
                "id": answer["id"],
                "content": [{"index": 0, "met": True, "reason": "fixture"}],
                "critical": [],
                "style": [
                    {
                        "kind": kind,
                        "quote": answer["answer"],
                        "reason": "fixture",
                        "region": "ending",
                    }
                    for kind in fixture["expected"][answer["id"]]
                ],
                "clarity": "clear",
                "clarity_reason": "fixture",
            }
            for answer in fixture["answers"]
        ]
    }


@pytest.mark.parametrize("index", [0, 1, 2])
def test_control_gate_checks_evidence_and_expected_labels(index: int) -> None:
    core = BENCH["engine"]()
    fixture = core["read_json"](ROOT / "controls.json")[index]
    record = fixture_record(fixture)
    assert BENCH["control_matches"](core, fixture, record)
    wrong = copy.deepcopy(record)
    wrong["ratings"][0]["content"][0]["met"] = False
    assert not BENCH["control_matches"](core, fixture, wrong)
    wrong = copy.deepcopy(record)
    wrong["ratings"][0]["style"] = [
        {
            "kind": "self_defense",
            "quote": "fabricated",
            "reason": "fixture",
            "region": "opening",
        }
    ]
    with pytest.raises(ValueError, match="Invalid style evidence"):
        BENCH["control_matches"](core, fixture, wrong)
    wrong["ratings"][0]["style"][0]["quote"] = fixture["answers"][0]["answer"]
    assert not BENCH["control_matches"](core, fixture, wrong)


def test_missing_controls_fail_closed(tmp_path: Path) -> None:
    module = runpy.run_path(str(ROOT / "benchmark.py"))
    module["check_controls"].__globals__["ROOT"] = tmp_path
    core = BENCH["engine"]()
    for name in ("execution-manifest.json", "controls.json"):
        (tmp_path / name).write_bytes((ROOT / name).read_bytes())
    with pytest.raises(FileNotFoundError):
        module["check_controls"](core)


def test_generate_exactly_32_isolated_requests(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    core = BENCH["engine"]()
    calls: list[tuple[str, str]] = []

    def fake_invoke(
        system: str, prompt: str, config: dict[str, Any], cwd: str, timeout: int
    ) -> dict[str, Any]:
        assert Path(cwd).is_dir() and not list(Path(cwd).iterdir())
        assert config["model"] == "gpt-6-astra" and timeout == 240
        calls.append((system, prompt))
        return {"answer": "fixture", "characters": 7, "seconds": 0, "usage": {}}

    def fake_version(*args: object, **kwargs: object) -> str:
        return "fixture\n"

    core["generate"].__globals__["invoke"] = fake_invoke
    monkeypatch.setattr(subprocess, "check_output", fake_version)
    core["generate"]("benchmark", ["baseline", "revised"], tmp_path)
    assert len(calls) == 32
    assert len(list(tmp_path.glob("*.json"))) == 33
    assert {system for system, _ in calls} == {
        (ROOT / f"prompts/{arm}.txt").read_text() for arm in ("baseline", "revised")
    }
    assert {prompt for _, prompt in calls} == {
        c["prompt"] for c in core["read_json"](ROOT / "cases.json")
    }
    with pytest.raises(FileExistsError):
        core["generate"]("benchmark", ["baseline", "revised"], tmp_path)
    assert len(calls) == 32


def test_controls_hide_labels_and_preserve_failed_attempts(tmp_path: Path) -> None:
    module = runpy.run_path(str(ROOT / "benchmark.py"))
    module["calibrate"].__globals__["ROOT"] = tmp_path
    core = BENCH["engine"]()
    for name in (
        "protocol.json",
        "controls.json",
        "judge.txt",
        "execution-manifest.json",
    ):
        (tmp_path / name).write_bytes((ROOT / name).read_bytes())
    fixtures = core["read_json"](ROOT / "controls.json")
    calls: list[dict[str, Any]] = []

    def fake_invoke(
        system: str, prompt: str, config: dict[str, Any], cwd: str, timeout: int
    ) -> dict[str, Any]:
        packet = core["json"].loads(prompt)
        assert set(packet) == {"task", "required", "critical_examples", "answers"}
        assert config["model"] == "gpt-6-sol"
        calls.append(packet)
        if len(calls) == 1:
            return {"error": "simulated transport failure"}
        return {"answer": core["json"].dumps(fixture_record(fixtures[len(calls) - 1]))}

    core["invoke"] = fake_invoke
    with pytest.raises(ValueError, match="Judge control failed: k1"):
        module["calibrate"](core)
    assert len(calls) == 3
    assert len(list((tmp_path / "results/controls").glob("*.json"))) == 3
    record = core["read_json"](tmp_path / "results/controls/k1.json")
    assert record["error"] == "simulated transport failure"
    with pytest.raises(FileExistsError):
        module["calibrate"](core)
    assert len(calls) == 3


def test_saved_results_reproduce_summary_and_validate_evidence() -> None:
    core = BENCH["engine"]()
    BENCH["verify"](core)
    BENCH["check_controls"](core)
    read = core["read_json"]
    assert BENCH["summary"]() == read(ROOT / "summary.json")
    metadata = read(ROOT / "results/benchmark/run.json")
    assert metadata["jobs"] == 32
    assert metadata["source_manifest"] == read(ROOT / "execution-manifest.json")
    cases = read(ROOT / "cases.json")
    expected = {"run.json"}
    for case in cases:
        answers: dict[str, str] = {}
        for arm in ("baseline", "revised"):
            for repetition in (1, 2):
                key = f"{case['id']}-{arm}-{repetition}"
                expected.add(f"{key}.json")
                record = read(ROOT / "results/benchmark" / f"{key}.json")
                assert "error" not in record
                assert record["provider"] == "openai"
                assert record["model"] == "gpt-6-astra"
                assert record["characters"] == len(record["answer"])
                answers[key] = record["answer"]
        judgment = read(ROOT / "results/benchmark-judgments" / f"{case['id']}.json")
        assert judgment["model"] == "gpt-6-sol"
        assert set(judgment["mapping"].values()) == set(answers)
        assert core["json"].loads(judgment["answer"])["ratings"] == judgment["ratings"]
        core["validate_ratings"](
            judgment,
            [
                {"id": key, "answer": answers[value]}
                for key, value in judgment["mapping"].items()
            ],
            len(case["required"]),
        )
    assert {p.name for p in (ROOT / "results/benchmark").glob("*.json")} == expected
    assert {p.stem for p in (ROOT / "results/benchmark-judgments").glob("*.json")} == {
        case["id"] for case in cases
    }
