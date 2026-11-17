"""Offline substitution contracts and integration with the frozen serial runner."""

from __future__ import annotations

import json
import runpy
from pathlib import Path
from typing import Any
from unittest.mock import patch

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = (
    ROOT
    / "evaluations/communication-style/preference-calibration/writing_substitution.py"
)


def freeze(study: Path, module: dict[str, Any]) -> None:
    (study / "manifest.json").write_text(json.dumps(module["ENGINE"]["hashes"](study)))
    report = module["WRITING"]["preflight"](study)
    (study / "preflight.json").write_text(json.dumps(report))


@pytest.fixture
def bundle(tmp_path: Path) -> tuple[dict[str, Any], Path]:
    module = runpy.run_path(str(SCRIPT))
    baseline = (SCRIPT.parent.parent / "prompts/baseline.txt").read_text()
    replacement = {
        "old": "Use brief clarification",
        "new": "Explain the requested distinctions",
    }
    (tmp_path / "baseline.txt").write_text(baseline)
    (tmp_path / "revised.txt").write_text(
        baseline.replace(replacement["old"], replacement["new"], 1)
    )
    (tmp_path / "jobs.json").write_text(
        json.dumps(
            [
                {
                    "id": "C1",
                    "stage": "generation",
                    "order": ["revised", "baseline"],
                    "context": "Question only",
                    "answer": "",
                    "review": "PRIVATE AUDIT LABEL, NEVER SEND",
                }
            ]
        )
    )
    (tmp_path / "protocol.json").write_text(
        json.dumps(
            {
                "stages": ["generation"],
                "max_calls": 2,
                "generator": dict(module["BASE"]["CONFIG"]),
                "replacement": replacement,
                "frozen_files": [
                    "protocol.json",
                    "jobs.json",
                    "baseline.txt",
                    "revised.txt",
                ],
            }
        )
    )
    freeze(tmp_path, module)
    return module, tmp_path


def test_cli_preflight_and_dispatch_restoration(
    bundle: tuple[dict[str, Any], Path], capsys: pytest.CaptureFixture[str]
) -> None:
    module, study = bundle
    namespace = module["ENGINE"]["main"].__globals__
    old = {name: namespace[name] for name in ("verify", "preflight", "evaluate_prompt")}
    checks: list[str] = []
    with (
        patch.dict(namespace, {"ROOT": study.parent}),
        patch.dict(
            module["ENGINE"]["CHECKER"], {"verify": lambda: checks.append("checked")}
        ),
        patch("sys.argv", [str(SCRIPT), str(study), "check"]),
    ):
        module["main"]()
    report = json.loads(capsys.readouterr().out)
    assert checks == ["checked"]
    assert report["status"] == "passed"
    assert report["synthetic_calls"] == 2 and report["model_calls"] == 0
    assert report["in_process_network_attempts"] == 0
    assert all(namespace[name] is value for name, value in old.items())


@pytest.mark.parametrize(
    "change",
    [
        "budget",
        "model",
        "stage",
        "empty_jobs",
        "duplicate",
        "id",
        "order",
        "empty_question",
        "reference",
        "baseline",
        "extra_text",
        "old_absent",
        "old_repeated",
        "empty_old",
        "empty_new",
        "same",
        "new_type",
        "extra_field",
        "omitted_freeze",
    ],
)
def test_reject_refrozen_invalid_contract(
    bundle: tuple[dict[str, Any], Path], change: str
) -> None:
    module, study = bundle
    protocol = json.loads((study / "protocol.json").read_text())
    jobs = json.loads((study / "jobs.json").read_text())
    if change == "budget":
        protocol["max_calls"] = 4
    elif change == "model":
        protocol["generator"]["model"] = "other"
    elif change == "stage":
        protocol["stages"] = ["other"]
    elif change == "empty_jobs":
        jobs = []
        protocol["max_calls"] = 0
    elif change == "duplicate":
        jobs.append(dict(jobs[0]))
        protocol["max_calls"] = 4
    elif change == "id":
        jobs[0]["id"] = "../escape"
    elif change == "order":
        jobs[0]["order"] = ["baseline", "baseline"]
    elif change == "empty_question":
        jobs[0]["context"] = " "
    elif change == "reference":
        jobs[0]["answer"] = "Reference must never be sent"
    elif change == "baseline":
        (study / "baseline.txt").write_text("Changed baseline")
    elif change == "extra_text":
        path = study / "revised.txt"
        path.write_text(path.read_text() + "Unrelated addition")
    elif change == "old_absent":
        protocol["replacement"]["old"] = "absent fixture"
    elif change == "old_repeated":
        protocol["replacement"]["old"] = "the"
    elif change == "empty_old":
        protocol["replacement"]["old"] = " "
    elif change == "empty_new":
        protocol["replacement"]["new"] = ""
    elif change == "same":
        protocol["replacement"]["new"] = protocol["replacement"]["old"]
    elif change == "new_type":
        protocol["replacement"]["new"] = 123
    elif change == "extra_field":
        protocol["replacement"]["extra"] = "not allowed"
    else:
        protocol["frozen_files"].remove("jobs.json")
    (study / "protocol.json").write_text(json.dumps(protocol))
    (study / "jobs.json").write_text(json.dumps(jobs))
    (study / "manifest.json").write_text(json.dumps(module["ENGINE"]["hashes"](study)))
    with (
        patch.dict(module["ENGINE"]["CHECKER"], {"verify": lambda: None}),
        pytest.raises(ValueError),
    ):
        module["verify"](study)


def test_unfrozen_change_stops_before_generation(
    bundle: tuple[dict[str, Any], Path],
) -> None:
    module, study = bundle
    (study / "revised.txt").write_text("Changed after freeze")
    with (
        patch.dict(module["ENGINE"]["main"].__globals__, {"ROOT": study.parent}),
        patch.dict(module["ENGINE"]["CHECKER"], {"verify": lambda: None}),
        patch("sys.argv", [str(SCRIPT), str(study), "generation"]),
        pytest.raises(ValueError, match="Substitution freeze changed"),
    ):
        module["main"]()
    assert not (study / "results").exists()


@pytest.mark.parametrize("failure", ["none", "returned", "raised"])
def test_serial_requests_failure_retention_and_no_retry(
    bundle: tuple[dict[str, Any], Path], failure: str
) -> None:
    module, study = bundle
    engine = module["ENGINE"]
    seen: list[tuple[str, str]] = []

    def fake(system: str, context: str) -> dict[str, Any]:
        seen.append((system, context))
        if failure == "raised":
            raise RuntimeError("private failure detail")
        return {"error": "fixture"} if failure == "returned" else {"answer": "原样回答"}

    namespace = engine["main"].__globals__
    old = {name: namespace[name] for name in ("verify", "preflight", "evaluate_prompt")}
    # The CLI binds diagnostics through the invocation function's CORE namespace.
    with (
        patch.dict(namespace, {"ROOT": study.parent}),
        patch.dict(engine["CHECKER"], {"verify": lambda: None}),
        patch.dict(fake.__globals__, {"CORE": {}}),
        patch.dict(module["BASE"], {"live": fake}),
        patch("sys.argv", [str(SCRIPT), str(study), "generation"]),
    ):
        if failure == "none":
            module["main"]()
        else:
            with pytest.raises(RuntimeError, match="Failed output retained"):
                module["main"]()
        with pytest.raises(FileExistsError):
            module["main"]()
    assert all(namespace[name] is value for name, value in old.items())
    arms = ["revised", "baseline"] if failure == "none" else ["revised"]
    assert seen == [
        (module["WRITING"]["prompt"](study, a), "Question only") for a in arms
    ]
    for arm in arms:
        record = json.loads((study / "results/C1" / f"{arm}.json").read_text())
        assert record["invocations"] == 1
        assert record["request"] == {
            "system": module["WRITING"]["prompt"](study, arm),
            "messages": [{"role": "user", "content": "Question only"}],
        }
        assert "private failure detail" not in json.dumps(record)
        assert "PRIVATE AUDIT LABEL" not in json.dumps(record)
        assert ("error" in record) == (failure != "none")
    if failure != "none":
        assert not (study / "results/C1/baseline.started.json").exists()
