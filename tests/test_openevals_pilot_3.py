"""Offline checks for bounded reuse of the original human-labeled packet."""

from __future__ import annotations

import json
import runpy
from pathlib import Path
from unittest.mock import patch

import pytest

SCRIPT = (
    Path(__file__).resolve().parents[1]
    / "evaluations/communication-style/preference-calibration/openevals-pilot-3/run.py"
)


def prepare(root: Path) -> None:
    (root / "protocol.json").write_text(json.dumps({"cases": ["D02", "D05"]}))
    (root / "cases.json").write_text(
        json.dumps(
            {
                "cases": [
                    {
                        "id": case,
                        "context": "question",
                        "answers": {"A": "甲", "B": "乙"},
                        "human_feedback": "PRIVATE_LABEL",
                    }
                    for case in ("D02", "D05")
                ]
            }
        )
    )


@pytest.mark.parametrize("failure", [False, True])
def test_once_only_and_label_isolation(tmp_path: Path, failure: bool) -> None:
    module = runpy.run_path(str(SCRIPT))
    prepare(tmp_path)
    calls: list[tuple[str, str]] = []

    def evaluate(context: str, answer: str, _invoke: object) -> dict[str, object]:
        calls.append((context, answer))
        return {"error": "fixture"} if failure else {"diagnostic": {"findings": []}}

    with (
        patch.dict(module["execute"].__globals__, {"ROOT": tmp_path}),
        patch.dict(module["BASE"], {"evaluate": evaluate}),
    ):
        if failure:
            with pytest.raises(RuntimeError, match="Failed output retained"):
                module["execute"]("D02")
            assert calls == [("question", "甲")]
            assert not (tmp_path / "results/D02/B.started.json").exists()
        else:
            module["execute"]("D02")
            assert calls == [("question", "甲"), ("question", "乙")]
            (tmp_path / "review-D02.json").write_text('{"decision":"continue"}')
            module["execute"]("D05")
            assert calls == [("question", "甲"), ("question", "乙")] * 2
        with pytest.raises(FileExistsError):
            module["execute"]("D02")
        assert len(calls) == (1 if failure else 4)


def test_second_case_requires_review_and_unknown_cases_fail(tmp_path: Path) -> None:
    module = runpy.run_path(str(SCRIPT))
    prepare(tmp_path)
    with patch.dict(module["execute"].__globals__, {"ROOT": tmp_path}):
        with pytest.raises(FileNotFoundError):
            module["execute"]("D05")
        (tmp_path / "review-D02.json").write_text('{"decision":"stop"}')
        with pytest.raises(ValueError, match="Previous case not approved"):
            module["execute"]("D05")
        with pytest.raises(ValueError):
            module["execute"]("D99")
    assert not (tmp_path / "results").exists()
