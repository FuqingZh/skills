"""The Promptfoo adapter only replays immutable visible records."""

from __future__ import annotations

import hashlib
import json
import runpy
from pathlib import Path
from typing import Any

import pytest

ROOT = (
    Path(__file__).resolve().parents[1]
    / "evaluations/communication-style/preference-calibration"
)
MOD = runpy.run_path(str(ROOT / "promptfoo_replay.py"))


def test_prepare_is_exclusive_and_reuses_exact_jobs(tmp_path: Path) -> None:
    destination = tmp_path / "replay"
    MOD["prepare"](destination)
    config = json.loads((destination / "promptfooconfig.json").read_text())
    assert len(config["tests"]) == 24
    assert len(config["providers"]) == 2
    assert config["evaluateOptions"] == {"cache": False, "maxConcurrency": 3}
    assert all(p["config"]["maxRetries"] == 0 for p in config["providers"])
    with pytest.raises(FileExistsError):
        MOD["prepare"](destination)


@pytest.mark.parametrize("version", [3, 4])
def test_replay_retains_errors_and_outputs(version: int, tmp_path: Path) -> None:
    options = {"config": {"version": version, "receipts": str(tmp_path)}}
    context = {"vars": {"case": "D05", "order": "original"}}
    path = ROOT / f"results-v{version}" / "D05-original.json"
    before = path.read_bytes()
    record = json.loads(before)
    result = MOD["call_api"]("ignored", options, context)
    assert result["output"] == record["answer"]
    assert result.get("error") == record.get("error")
    assert result["metadata"]["sha256"] == hashlib.sha256(before).hexdigest()
    with pytest.raises(FileExistsError):
        MOD["call_api"]("ignored", options, context)
    assert path.read_bytes() == before
    assert len(list(tmp_path.glob("*.json"))) == 1


def test_invalid_record_selection_has_no_side_effects(tmp_path: Path) -> None:
    options: dict[str, Any] = {"config": {"version": 5, "receipts": str(tmp_path)}}
    context = {"vars": {"case": "D05", "order": "original"}}
    with pytest.raises(ValueError, match="version"):
        MOD["call_api"]("ignored", options, context)
    options["config"]["version"] = 3
    context["vars"]["case"] = "../D05"
    with pytest.raises(ValueError, match="record"):
        MOD["call_api"]("ignored", options, context)
    assert not list(tmp_path.iterdir())


def test_assertion_is_artifact_check_not_human_agreement() -> None:
    for choice in ("A", "B", "tie", "uncertain"):
        result = MOD["get_assert"](json.dumps({"choice": choice}), {})
        assert result["pass"] is True
        assert "not a preference-agreement score" in result["reason"]
    with pytest.raises(ValueError):
        MOD["get_assert"]("invalid JSON", {})
