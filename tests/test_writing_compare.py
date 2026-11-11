"""Offline contract tests for the writing adapter and reused execution gate."""

from __future__ import annotations

import json
import runpy
from pathlib import Path
from typing import Any
from unittest.mock import patch

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = (
    ROOT / "evaluations/communication-style/preference-calibration/writing_compare.py"
)


def prepare(study: Path, module: dict[str, Any]) -> None:
    baseline = (SCRIPT.parent.parent / "prompts/baseline.txt").read_text()
    (study / "baseline.txt").write_text(baseline)
    (study / "guidance.txt").write_text("Fixture guidance.\n")
    (study / "revised.txt").write_text(baseline.rstrip() + "\n\nFixture guidance.\n")
    (study / "jobs.json").write_text(
        json.dumps(
            [
                {
                    "id": "C1",
                    "stage": "generation",
                    "order": ["revised", "baseline"],
                    "context": "Question only",
                    "answer": "",
                    "review": "SECRET AUDIT LABEL, NEVER SEND",
                }
            ]
        )
    )
    (study / "protocol.json").write_text(
        json.dumps(
            {
                "stages": ["generation"],
                "max_calls": 2,
                "generator": module["BASE"]["CONFIG"],
                "frozen_files": [
                    "jobs.json",
                    "protocol.json",
                    "baseline.txt",
                    "revised.txt",
                    "guidance.txt",
                ],
            }
        )
    )
    freeze(study, module)


def freeze(study: Path, module: dict[str, Any]) -> None:
    (study / "manifest.json").write_text(json.dumps(module["ENGINE"]["hashes"](study)))
    (study / "preflight.json").write_text(json.dumps(module["preflight"](study)))


@pytest.mark.parametrize("failure", ["none", "returned", "raised"])
def test_serial_generation_isolated_request_and_stop(
    tmp_path: Path, failure: str
) -> None:
    module = runpy.run_path(str(SCRIPT))
    prepare(tmp_path, module)
    seen: list[tuple[str, str]] = []

    def fake(system: str, context: str) -> dict[str, Any]:
        seen.append((system, context))
        if failure == "raised":
            raise RuntimeError("private failure detail")
        return {"error": "fixture"} if failure == "returned" else {"answer": "原样回答"}

    engine = module["ENGINE"]
    with (
        patch.dict(
            engine["execute"].__globals__, {"evaluate_prompt": module["generate"]}
        ),
        patch.dict(module["BASE"], {"live": fake}),
    ):
        if failure == "none":
            engine["execute"](tmp_path, "generation")
        else:
            with pytest.raises(RuntimeError, match="Failed output retained"):
                engine["execute"](tmp_path, "generation")
        with pytest.raises(FileExistsError):
            engine["execute"](tmp_path, "generation")
    arms = ["revised", "baseline"] if failure == "none" else ["revised"]
    assert seen == [(module["prompt"](tmp_path, arm), "Question only") for arm in arms]
    for arm in arms:
        record = json.loads((tmp_path / "results/C1" / f"{arm}.json").read_text())
        assert record["invocations"] == 1
        assert record["request"] == {
            "system": module["prompt"](tmp_path, arm),
            "messages": [{"role": "user", "content": "Question only"}],
        }
        assert "private failure detail" not in json.dumps(record)
        assert ("error" in record) == (failure != "none")
    if failure != "none":
        assert not (tmp_path / "results/C1/baseline.started.json").exists()


def test_verify_and_preflight(tmp_path: Path) -> None:
    module = runpy.run_path(str(SCRIPT))
    prepare(tmp_path, module)
    checks: list[str] = []
    with patch.dict(
        module["ENGINE"]["CHECKER"], {"verify": lambda: checks.append("ok")}
    ):
        module["verify"](tmp_path)
    assert checks == ["ok"]
    report = module["preflight"](tmp_path)
    assert report["synthetic_calls"] == 2 and report["model_calls"] == 0
    (tmp_path / "guidance.txt").write_text("Changed")
    with (
        patch.dict(module["ENGINE"]["CHECKER"], {"verify": lambda: None}),
        pytest.raises(ValueError, match="Writing freeze changed"),
    ):
        module["verify"](tmp_path)


@pytest.mark.parametrize("change", ["budget", "model", "reference", "id", "prompt"])
def test_reject_invalid_contract(tmp_path: Path, change: str) -> None:
    module = runpy.run_path(str(SCRIPT))
    prepare(tmp_path, module)
    protocol = json.loads((tmp_path / "protocol.json").read_text())
    jobs = json.loads((tmp_path / "jobs.json").read_text())
    if change == "budget":
        protocol["max_calls"] = 4
    elif change == "model":
        protocol["generator"]["model"] = "other"
    elif change == "reference":
        jobs[0]["answer"] = "Do not send this answer"
    elif change == "id":
        jobs[0]["id"] = "../escape"
    else:
        (tmp_path / "revised.txt").write_text("unfrozen intervention")
    (tmp_path / "protocol.json").write_text(json.dumps(protocol))
    (tmp_path / "jobs.json").write_text(json.dumps(jobs))
    (tmp_path / "manifest.json").write_text(
        json.dumps(module["ENGINE"]["hashes"](tmp_path))
    )
    with (
        patch.dict(module["ENGINE"]["CHECKER"], {"verify": lambda: None}),
        pytest.raises(ValueError),
    ):
        module["verify"](tmp_path)


def test_reject_reference_and_unknown_arm_before_invocation(tmp_path: Path) -> None:
    module = runpy.run_path(str(SCRIPT))
    with pytest.raises(ValueError, match="Reference answers prohibited"):
        module["generate"](tmp_path, "baseline", "question", "reference", None)
    with pytest.raises(ValueError, match="Unknown writing arm"):
        module["prompt"](tmp_path, "unknown")


def test_main_restores_dispatch_after_failure(tmp_path: Path) -> None:
    module = runpy.run_path(str(SCRIPT))
    prepare(tmp_path, module)
    engine = module["ENGINE"]
    namespace = engine["main"].__globals__
    old = {name: namespace[name] for name in ("verify", "preflight", "evaluate_prompt")}

    def failing(study: Path) -> None:
        assert study == tmp_path
        assert namespace["evaluate_prompt"] is module["generate"]
        raise RuntimeError("fixture")

    with (
        patch.dict(namespace, {"ROOT": tmp_path.parent}),
        patch.dict(module["main"].__globals__, {"verify": failing}),
        patch("sys.argv", ["writing_compare.py", str(tmp_path), "check"]),
        pytest.raises(RuntimeError, match="fixture"),
    ):
        module["main"]()
    assert all(namespace[name] is value for name, value in old.items())
