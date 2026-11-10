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
