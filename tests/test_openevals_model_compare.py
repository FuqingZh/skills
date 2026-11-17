"""Offline model binding, prompt equality, restoration and source checks."""

from __future__ import annotations

import json
import runpy
from pathlib import Path
from typing import Any
from unittest.mock import patch

import pytest

ROOT = Path(__file__).resolve().parents[1]
DIRECTORY = ROOT / "evaluations/communication-style/preference-calibration"
SCRIPT = DIRECTORY / "openevals_model_compare.py"
STUDY = DIRECTORY / "openevals-model-comparison-1"


@pytest.mark.parametrize("arm", ["baseline", "revised"])
@pytest.mark.parametrize("failure", [False, True])
def test_model_binding_reaches_native_transport_and_restores(
    tmp_path: Path, arm: str, failure: bool
) -> None:
    module = runpy.run_path(str(SCRIPT))
    base = module["BASE"]
    namespace = base["evaluate"].__globals__
    assert base["live"].__globals__ is namespace
    original_config = namespace["CONFIG"]
    original_prompt = module["ENGINE"]["prompt"]
    expected = module["configuration"](STUDY, arm)
    calls: list[dict[str, str]] = []

    def native(
        _system: str, _prompt: str, config: dict[str, str], directory: str, timeout: int
    ) -> dict[str, Any]:
        calls.append(config.copy())
        assert Path(directory).is_dir() and timeout == 300
        if failure:
            raise RuntimeError("fixture failure")
        return {"answer": "fixture", "provider": config["provider"]}

    def evaluator(
        study: Path, selected: str, _context: str, _answer: str, invoke: Any
    ) -> dict[str, Any]:
        assert selected == arm and namespace["CONFIG"] == expected
        assert (
            module["ENGINE"]["prompt"](study, selected)
            == (STUDY / "revised-helpfulness.txt").read_text()
        )
        return {"transport": invoke("system", "message")}

    with (
        patch.dict(namespace, {"SCRATCH": tmp_path}),
        patch.dict(namespace["CORE"], {"invoke": native}),
        patch.dict(module["evaluate_prompt"].__globals__, {"ID_EVALUATE": evaluator}),
    ):
        if failure:
            with pytest.raises(RuntimeError, match="fixture failure"):
                module["evaluate_prompt"](STUDY, arm, "q", "a", base["live"])
        else:
            record = module["evaluate_prompt"](STUDY, arm, "q", "a", base["live"])
            assert record["judge_configuration"] == expected
    assert calls == [expected]
    assert namespace["CONFIG"] is original_config
    assert module["ENGINE"]["prompt"] is original_prompt
    assert not list(tmp_path.iterdir())


@pytest.mark.parametrize(
    "config",
    [None, {}, {"provider": "x", "model": "y", "thinking": 1}],
)
def test_bad_configuration_fails_before_invocation(
    tmp_path: Path, config: object
) -> None:
    module = runpy.run_path(str(SCRIPT))
    (tmp_path / "protocol.json").write_text(
        json.dumps({"models": {"baseline": config}})
    )
    with pytest.raises(ValueError, match="Invalid model configuration"):
        module["configuration"](tmp_path, "baseline")
    with pytest.raises(ValueError, match="Unknown model arm"):
        module["configuration"](tmp_path, "other")


def test_both_models_have_identical_criteria_and_original_materials() -> None:
    module = runpy.run_path(str(SCRIPT))
    previous = DIRECTORY / "openevals-contribution-v1-id-evidence"
    for name in ("guidance.txt", "revised-helpfulness.txt", "id-instructions.txt"):
        assert (STUDY / name).read_bytes() == (previous / name).read_bytes()
    assert module["fixed_prompt"](STUDY, "baseline") == module["fixed_prompt"](
        STUDY, "revised"
    )
    original = json.loads(
        (DIRECTORY / "openevals-contribution-v1/jobs.json").read_text()
    )
    by_id = {job["id"]: job for job in original}
    jobs = json.loads((STUDY / "jobs.json").read_text())
    assert [job["id"] for job in jobs] == ["D02-A", "D05-A", "P02-A", "D06-B"]
    for job in jobs:
        for field in ("context", "answer", "case", "side"):
            assert job[field] == by_id[job["id"]][field]
    assert [job["order"] for job in jobs] == [
        ["baseline", "revised"],
        ["revised", "baseline"],
        ["baseline", "revised"],
        ["revised", "baseline"],
    ]
