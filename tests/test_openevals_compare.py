"""Offline checks for prompt-only changes and bounded stage execution."""

from __future__ import annotations

import hashlib
import json
import runpy
from pathlib import Path
from unittest.mock import patch

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = (
    ROOT / "evaluations/communication-style/preference-calibration/openevals_compare.py"
)


@pytest.mark.parametrize("arm", ["baseline", "revised"])
@pytest.mark.parametrize("failure", [False, True])
def test_prompt_bundle_preserves_contract_and_restores_root(
    tmp_path: Path, arm: str, failure: bool
) -> None:
    module = runpy.run_path(str(SCRIPT))
    base_root = module["BASE_ROOT"]
    original_root = ROOT
    seen: list[Path] = []
    (tmp_path / "revised-helpfulness.txt").write_text("revised template")

    def evaluate(_context: str, _answer: str, _invoke: object) -> dict[str, object]:
        seen.append(ROOT)
        for name in ("schema.json", "instructions.txt"):
            assert (ROOT / name).read_bytes() == (base_root / name).read_bytes()
        assert (ROOT / "upstream-helpfulness.txt").read_text() == module["prompt"](
            tmp_path, arm
        )
        if failure:
            raise RuntimeError("fixture")
        return {"diagnostic": {"findings": []}, "invocations": 1}

    def forbidden(_system: str, _message: str) -> dict[str, object]:
        raise AssertionError("No model call allowed")

    with patch.dict(module["BASE"], {"evaluate": evaluate, "SCRATCH": tmp_path}):
        if failure:
            with pytest.raises(RuntimeError, match="fixture"):
                module["evaluate_prompt"](tmp_path, arm, "question", "甲", forbidden)
        else:
            result = module["evaluate_prompt"](
                tmp_path, arm, "question", "甲", forbidden
            )
            assert result["invocations"] == 1
    assert original_root == ROOT
    assert len(seen) == 1 and not seen[0].exists()
    assert seen[0].parent == tmp_path


def prepare(study: Path) -> None:
    (study / "manifest.json").write_text("{}")
    (study / "preflight.json").write_text(
        json.dumps(
            {
                "status": "passed",
                "manifest_sha256": hashlib.sha256(b"{}").hexdigest(),
            }
        )
    )
    (study / "protocol.json").write_text(
        json.dumps({"stages": ["targets", "safeguards"]})
    )
    (study / "jobs.json").write_text(
        json.dumps(
            [
                {
                    "id": "case-A",
                    "stage": "targets",
                    "context": "question",
                    "answer": "甲",
                    "order": ["revised", "baseline"],
                    "human_feedback": "DO NOT SEND",
                }
            ]
        )
    )


@pytest.mark.parametrize("failure", [False, True])
def test_stage_reservation_order_and_failure_stop(
    tmp_path: Path, failure: bool
) -> None:
    module = runpy.run_path(str(SCRIPT))
    prepare(tmp_path)
    calls: list[tuple[str, str, str]] = []

    def evaluate(
        _study: Path, arm: str, context: str, answer: str, _invoke: object
    ) -> dict[str, object]:
        calls.append((arm, context, answer))
        return {"error": "fixture"} if failure else {"diagnostic": {"findings": []}}

    with patch.dict(module["execute"].__globals__, {"evaluate_prompt": evaluate}):
        if failure:
            with pytest.raises(RuntimeError, match="Failed output retained"):
                module["execute"](tmp_path, "targets")
            assert calls == [("revised", "question", "甲")]
        else:
            module["execute"](tmp_path, "targets")
            assert calls == [
                ("revised", "question", "甲"),
                ("baseline", "question", "甲"),
            ]
        with pytest.raises(FileExistsError):
            module["execute"](tmp_path, "targets")
        assert len(calls) == (1 if failure else 2)


def test_stage_requires_matching_preflight_and_previous_review(tmp_path: Path) -> None:
    module = runpy.run_path(str(SCRIPT))
    prepare(tmp_path)
    with pytest.raises(FileNotFoundError):
        module["execute"](tmp_path, "safeguards")
    (tmp_path / "review-targets.json").write_text('{"decision":"stop"}')
    with pytest.raises(ValueError, match="Previous stage not approved"):
        module["execute"](tmp_path, "safeguards")
    (tmp_path / "manifest.json").write_text('{"changed":true}')
    with pytest.raises(ValueError, match="Matching preflight required"):
        module["execute"](tmp_path, "targets")
    assert not (tmp_path / "results").exists()
