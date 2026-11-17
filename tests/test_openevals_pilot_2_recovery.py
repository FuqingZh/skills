"""Offline checks for recovery routing and preservation of attempt identity."""

from __future__ import annotations

import json
import runpy
from pathlib import Path
from unittest.mock import patch

import pytest

SCRIPT = (
    Path(__file__).resolve().parents[1]
    / "evaluations/communication-style/preference-calibration"
    / "openevals-pilot-2-recovery-1/resume.py"
)


@pytest.mark.parametrize("failure", [False, True])
def test_recovery_uses_new_root_and_numbers_retry(
    tmp_path: Path, failure: bool
) -> None:
    module = runpy.run_path(str(SCRIPT))
    output = tmp_path / "recovery"
    (tmp_path / "deletion-pilot-2.json").write_text(
        json.dumps(
            {
                "cases": [
                    {
                        "id": "P03",
                        "context": "question",
                        "answers": {"A": "甲", "B": "乙"},
                    }
                ]
            },
            ensure_ascii=False,
        )
    )

    def evaluate(*_args: object) -> dict[str, object]:
        return {"error": "fixture"} if failure else {"diagnostic": {"findings": []}}

    with (
        patch.dict(module["execute"].__globals__, {"ROOT": output}),
        patch.dict(module["PILOT"]["BASE"], {"evaluate": evaluate}),
    ):
        if failure:
            with pytest.raises(RuntimeError, match="Failed output retained"):
                module["execute"]("P03")
            assert not (output / "results/P03/B.started.json").exists()
        else:
            module["execute"]("P03")
            started_b = output / "results/P03/B.started.json"
            assert json.loads(started_b.read_text())["attempt"] == 1
        started_a = output / "results/P03/A.started.json"
        assert json.loads(started_a.read_text())["attempt"] == 2
        with pytest.raises(FileExistsError):
            module["execute"]("P03")


def test_recovery_second_case_requires_its_own_review(tmp_path: Path) -> None:
    module = runpy.run_path(str(SCRIPT))
    with (
        patch.dict(module["execute"].__globals__, {"ROOT": tmp_path}),
        pytest.raises(FileNotFoundError),
    ):
        module["execute"]("P04")
    assert not (tmp_path / "results").exists()
