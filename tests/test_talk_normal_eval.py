"""Offline contract tests for the pinned upstream follow-up comparison."""

from __future__ import annotations

import json
import runpy
import subprocess
from pathlib import Path
from typing import Any

import pytest

BASE = Path(__file__).resolve().parents[1] / "evaluations/communication-style"
ROOT = BASE / "talk-normal"
BENCH = runpy.run_path(str(ROOT / "benchmark.py"))


def test_followup_only_remaps_split_and_preserves_original_cases() -> None:
    core = BENCH["engine"]()
    load = core["generate"].__globals__["read_json"]
    original = json.loads((BASE / "cases.json").read_text())
    actual = load(ROOT / "cases.json")
    assert len(actual) == 12
    assert actual == [{**case, "split": "benchmark"} for case in original]
    assert {c["split"] for c in original} == {"development", "holdout"}
    assert sum(c["length"] == "long" for c in actual) == 6
    assert (ROOT / "judge.txt").read_bytes() == (BASE / "judge.txt").read_bytes()
    assert (ROOT / "prompts/baseline.txt").read_bytes() == (
        BASE / "prompts/baseline.txt"
    ).read_bytes()


def test_followup_manifest_and_original_manifest_both_verify() -> None:
    BENCH["verify"](BENCH["engine"]())
    runpy.run_path(str(BASE / "run.py"))["verify_sources"]()


def test_followup_generates_48_fresh_attempts_without_model_calls(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    core = BENCH["engine"]()
    namespace = core["generate"].__globals__
    calls: list[tuple[str, str]] = []

    def fake_invoke(
        system: str, prompt: str, config: dict[str, Any], cwd: str, timeout: int
    ) -> dict[str, Any]:
        assert Path(cwd).is_dir()
        assert not list(Path(cwd).iterdir())
        assert config["model"] == "gpt-6-astra"
        assert timeout == 240
        calls.append((system, prompt))
        return {"answer": "fixture", "characters": 7, "seconds": 0, "usage": {}}

    namespace["invoke"] = fake_invoke

    def fake_version(*args: object, **kwargs: object) -> str:
        return "fixture\n"

    monkeypatch.setattr(subprocess, "check_output", fake_version)
    core["generate"]("benchmark", ["baseline", "talk-normal"], tmp_path)
    assert len(calls) == 48
    systems = {
        (ROOT / "prompts/baseline.txt").read_text(),
        (ROOT / "prompts/talk-normal.txt").read_text(),
    }
    assert {system for system, _prompt in calls} == systems
    expected_prompts = {
        c["prompt"] for c in json.loads((BASE / "cases.json").read_text())
    }
    assert {prompt for _system, prompt in calls} == expected_prompts
    assert len(list(tmp_path.glob("*.json"))) == 49
    with pytest.raises(FileExistsError):
        core["generate"]("benchmark", ["baseline", "talk-normal"], tmp_path)
    assert len(calls) == 48
