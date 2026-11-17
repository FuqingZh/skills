"""Offline checks for second-batch reservation, stopping and input isolation."""

from __future__ import annotations

import runpy
from pathlib import Path
from typing import Any
from unittest.mock import patch

import pytest

SCRIPT = (
    Path(__file__).resolve().parents[1]
    / "evaluations/communication-style/preference-calibration"
    / "openevals-pilot-2/run.py"
)


@pytest.mark.parametrize("failure", [False, True])
def test_case_is_once_only_and_stops_on_failure(tmp_path: Path, failure: bool) -> None:
    module = runpy.run_path(str(SCRIPT))
    calls: list[tuple[str, str]] = []
    base = dict(module["BASE"])
    original_load = base["load"]

    def load(path: Path) -> Any:
        if path.name == "deletion-pilot-2.json":
            return {
                "cases": [
                    {
                        "id": "P03",
                        "context": "fixture question",
                        "answers": {"A": "甲", "B": "乙"},
                        "human_preference": "B",
                        "human_comment": "LABEL MUST NOT BE SENT",
                    }
                ]
            }
        return original_load(path)

    def evaluate(context: str, answer: str, _invoke: Any) -> dict[str, Any]:
        calls.append((context, answer))
        return {"error": "fixture"} if failure else {"diagnostic": {"findings": []}}

    base.update(load=load, evaluate=evaluate)
    with patch.dict(module["execute"].__globals__, {"ROOT": tmp_path, "BASE": base}):
        if failure:
            with pytest.raises(RuntimeError, match="Failed output retained"):
                module["execute"]("P03")
            assert calls == [("fixture question", "甲")]
            assert not (tmp_path / "results/P03/B.started.json").exists()
            assert original_load(tmp_path / "results/P03/A.json")["error"] == "fixture"
        else:
            module["execute"]("P03")
            assert calls == [("fixture question", "甲"), ("fixture question", "乙")]
            assert (tmp_path / "results/P03/B.started.json").is_file()
        with pytest.raises(FileExistsError):
            module["execute"]("P03")
        assert len(calls) == (1 if failure else 2)


def test_second_case_requires_review(tmp_path: Path) -> None:
    module = runpy.run_path(str(SCRIPT))
    with (
        patch.dict(module["execute"].__globals__, {"ROOT": tmp_path}),
        pytest.raises(FileNotFoundError),
    ):
        module["execute"]("P04")
    assert not (tmp_path / "results").exists()
