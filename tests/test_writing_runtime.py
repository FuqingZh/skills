"""Offline contracts for the explicitly pinned successor runtime adapter."""

from __future__ import annotations

import hashlib
import json
import os
import runpy
from collections.abc import Iterator
from contextlib import nullcontext
from pathlib import Path
from types import SimpleNamespace
from typing import Any
from unittest.mock import patch

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = (
    ROOT / "evaluations/communication-style/preference-calibration/writing_runtime.py"
)


def freeze(module: dict[str, Any], study: Path) -> None:
    (study / "manifest.json").write_text(json.dumps(module["ENGINE"]["hashes"](study)))
    report = module["SUBSTITUTION"]["WRITING"]["preflight"](study)
    (study / "preflight.json").write_text(json.dumps(report))


@pytest.fixture
def bundle(tmp_path: Path) -> Iterator[tuple[dict[str, Any], Path, Path]]:
    module = runpy.run_path(str(SCRIPT))
    study = tmp_path / "study"
    study.mkdir()
    binary = tmp_path / "pi"
    binary.write_bytes(b"fixture, never executed")
    binary.chmod(0o700)
    baseline = (SCRIPT.parent.parent / "prompts/baseline.txt").read_text()
    replacement = {"old": baseline, "new": "Replacement fixture\n"}
    (study / "baseline.txt").write_text(baseline)
    (study / "revised.txt").write_text(replacement["new"])
    (study / "jobs.json").write_text(
        json.dumps(
            [
                {
                    "id": "C1",
                    "stage": "generation",
                    "order": ["revised", "baseline"],
                    "context": "Shared question and evidence",
                    "answer": "",
                    "review": "PRIVATE LABEL, NEVER SEND",
                }
            ]
        )
    )
    (study / "protocol.json").write_text(
        json.dumps(
            {
                "stages": ["generation"],
                "max_calls": 2,
                "generator": dict(module["BASE"]["CONFIG"]),
                "replacement": replacement,
                "runtime": {
                    "version": "1.5.2",
                    "executable": str(binary),
                    "sha256": hashlib.sha256(binary.read_bytes()).hexdigest(),
                },
                "frozen_files": [
                    str(SCRIPT),
                    "protocol.json",
                    "jobs.json",
                    "baseline.txt",
                    "revised.txt",
                ],
            }
        )
    )
    freeze(module, study)
    packages = module["BASE"]["load"](module["ENGINE"]["BASE_ROOT"] / "preflight.json")[
        "packages"
    ]
    distributions = [
        SimpleNamespace(metadata={"Name": name}, version=version)
        for name, version in packages.items()
    ]
    namespace = module["main"].__globals__
    with (
        patch.dict(namespace, {"ROOT": study.parent}),
        patch.dict(module["ENGINE"]["main"].__globals__, {"ROOT": study.parent}),
        patch.dict(module["BASE"], {"agent": lambda: nullcontext(str(study))}),
        patch.object(
            module["importlib"].metadata, "distributions", return_value=distributions
        ),
        patch.object(
            module["subprocess"], "run", return_value=SimpleNamespace(stdout="1.5.2\n")
        ),
    ):
        yield module, study, binary


def test_preflight_uses_pinned_binary_and_restores_state(
    bundle: tuple[dict[str, Any], Path, Path], capsys: pytest.CaptureFixture[str]
) -> None:
    module, study, binary = bundle
    checker = module["CHECKER"]
    before = {key: checker[key] for key in ("verify", "PI_DIR")}
    path_before = os.environ["PATH"]
    with patch("sys.argv", [str(SCRIPT), str(study), "check"]):
        module["main"]()
    report = json.loads(capsys.readouterr().out)
    assert report["status"] == "passed" and report["synthetic_calls"] == 2
    assert report["model_calls"] == report["in_process_network_attempts"] == 0
    assert os.environ["PATH"] == path_before
    assert all(checker[key] is value for key, value in before.items())
    probe = module["subprocess"].run
    probe.assert_called_once_with(
        ["pi", *module["BASE"]["CORE"]["ISOLATION"], "--version"],
        cwd=str(study),
        capture_output=True,
        text=True,
        timeout=20,
        check=True,
    )
    assert module["_runtime"](study) == binary.resolve()


@pytest.mark.parametrize(
    "change",
    [
        "version",
        "digest",
        "relative",
        "missing",
        "nonexecutable",
        "type",
        "adapter",
        "protocol",
    ],
)
def test_reject_invalid_refrozen_runtime(
    bundle: tuple[dict[str, Any], Path, Path], change: str
) -> None:
    module, study, binary = bundle
    protocol = json.loads((study / "protocol.json").read_text())
    if change == "version":
        protocol["runtime"]["version"] = "1.5.0"
    elif change == "digest":
        protocol["runtime"]["sha256"] = "0" * 64
    elif change == "relative":
        protocol["runtime"]["executable"] = "pi"
    elif change == "missing":
        binary.unlink()
    elif change == "nonexecutable":
        binary.chmod(0o600)
    elif change == "type":
        protocol["runtime"]["executable"] = None
    elif change == "adapter":
        protocol["frozen_files"].remove(str(SCRIPT))
    else:
        protocol["frozen_files"].remove("protocol.json")
    (study / "protocol.json").write_text(json.dumps(protocol))
    freeze(module, study)
    with pytest.raises(ValueError):
        module["_runtime"](study)
    module["subprocess"].run.assert_not_called()


def test_unfrozen_change_rejected_before_version_probe(
    bundle: tuple[dict[str, Any], Path, Path],
) -> None:
    module, study, _ = bundle
    (study / "revised.txt").write_text("Changed after freeze")
    with (
        patch("sys.argv", [str(SCRIPT), str(study), "generation"]),
        pytest.raises(ValueError, match="Runtime study freeze changed"),
    ):
        module["main"]()
    module["subprocess"].run.assert_not_called()
    assert not (study / "results").exists()


@pytest.mark.parametrize(
    "guard", ["first", "second", "dependencies", "selection", "version"]
)
def test_environment_guards_remain_active(
    bundle: tuple[dict[str, Any], Path, Path], guard: str
) -> None:
    module, study, binary = bundle
    if guard == "first":
        context = patch.dict(module["BASE"], {"hashes": lambda: {"changed": "fixture"}})
    elif guard == "second":
        context = patch.dict(
            module["CHECKER"], {"hashes": lambda: {"changed": "fixture"}}
        )
    elif guard == "dependencies":
        context = patch.object(
            module["importlib"].metadata, "distributions", return_value=[]
        )
    elif guard == "selection":
        context = patch.object(module["shutil"], "which", return_value=None)
    else:
        context = patch.object(
            module["subprocess"], "run", return_value=SimpleNamespace(stdout="1.5.3")
        )
    with (
        patch.dict(
            os.environ, {"PATH": str(binary.parent) + os.pathsep + os.environ["PATH"]}
        ),
        context,
        pytest.raises(ValueError),
    ):
        module["_verify_environment"](study)


@pytest.mark.parametrize("failure", [False, True])
def test_serial_generation_and_stop_contract(
    bundle: tuple[dict[str, Any], Path, Path], failure: bool
) -> None:
    module, study, binary = bundle
    seen: list[tuple[str, str]] = []

    def fake(system: str, context: str) -> dict[str, Any]:
        assert Path(module["shutil"].which("pi")).resolve() == binary.resolve()
        seen.append((system, context))
        return {"error": "fixture"} if failure else {"answer": "原样回答"}

    old = {key: module["CHECKER"][key] for key in ("verify", "PI_DIR")}
    with (
        patch.dict(fake.__globals__, {"CORE": {}}),
        patch.dict(module["BASE"], {"live": fake}),
        patch("sys.argv", [str(SCRIPT), str(study), "generation"]),
    ):
        if failure:
            with pytest.raises(RuntimeError, match="Failed output retained"):
                module["main"]()
        else:
            module["main"]()
        with pytest.raises(FileExistsError):
            module["main"]()
    assert all(module["CHECKER"][key] is value for key, value in old.items())
    arms = ["revised"] if failure else ["revised", "baseline"]
    assert seen == [
        ((study / f"{arm}.txt").read_text(), "Shared question and evidence")
        for arm in arms
    ]
    for arm in arms:
        record = json.loads((study / "results/C1" / f"{arm}.json").read_text())
        assert record["invocations"] == 1
        assert "PRIVATE LABEL" not in json.dumps(record)
    if failure:
        assert not (study / "results/C1/baseline.started.json").exists()
