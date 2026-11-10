"""Offline contracts for human calibration; no preference labels are inferred."""

from __future__ import annotations

import copy
import json
import runpy
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest

ROOT = (
    Path(__file__).resolve().parents[1]
    / "evaluations/communication-style/preference-calibration"
)
MODULE = runpy.run_path(str(ROOT / "packet.py"))


def test_separation_and_excerpt_provenance() -> None:
    pairs = MODULE["_load"]()
    original = json.loads((ROOT / "../cross-domain/cases.json").read_text())
    families = {case["id"]: case["family"] for case in original}
    for pair in pairs:
        assert pair["family"] == families[pair["case_id"]]
        provenance = pair["provenance"]
        assert provenance["case_file"] == "../cross-domain/cases.json"
        if provenance["record"] is not None:
            answer = json.loads((ROOT / provenance["record"]).read_text())["answer"]
            assert provenance["excerpt"] and provenance["excerpt"] in answer
        else:
            assert provenance["excerpt"] is None
    by_id = {pair["id"]: pair for pair in pairs}
    for left, right in (
        ("p1-transition", "p1-context"),
        ("p2-requested", "p2-unrequested"),
    ):
        assert by_id[left]["candidates"] == by_id[right]["candidates"]
        assert by_id[left]["context"] != by_id[right]["context"]
        assert by_id[left]["split"] == by_id[right]["split"]


@pytest.mark.parametrize("split", ["calibration", "holdout"])
def test_blind_payload_swap_and_exact_evidence(split: str) -> None:
    items = MODULE["_items"](split)
    assert items == MODULE["_items"](split)
    swapped = MODULE["_items"](split, swap=True)
    assert len(items) == 12
    for item, other in zip(items, swapped, strict=True):
        assert set(item) == {"id", "context", "answers"}
        assert item["id"] == other["id"] and item["context"] == other["context"]
        assert list(item["answers"]["A"].values()) == list(
            other["answers"]["B"].values()
        )
        assert list(item["answers"]["B"].values()) == list(
            other["answers"]["A"].values()
        )
        assert MODULE["_evidence"](item, ["A1"]) == {"A1": item["answers"]["A"]["A1"]}
        with pytest.raises(ValueError, match="Unknown paragraph"):
            MODULE["_evidence"](item, ["A99"])
        with pytest.raises(ValueError, match="Duplicate paragraph"):
            MODULE["_evidence"](item, ["A1", "A1"])
    formatted = {"answers": {"A": {"A1": "**literal bold**"}, "B": {"B1": "other"}}}
    assert MODULE["_evidence"](formatted, ["A1"])["A1"] == "**literal bold**"


def test_blank_form_and_saved_packet_reproduce() -> None:
    materials = MODULE["_materials"]("calibration")
    assert materials["packet"] == (ROOT / "calibration.md").read_text()
    assert materials["form"] == json.loads((ROOT / "labels.template.json").read_text())
    assert MODULE["_validate"]("calibration", materials["form"]) == {
        "pairs": 12,
        "labeled": 0,
        "content_labeled": 0,
    }
    assert not (ROOT / "holdout.md").exists()
    form = copy.deepcopy(materials["form"])
    for index, rating in enumerate(form["ratings"]):
        rating.update(choice=MODULE["CHOICES"][index % 4], evidence=["A1"])
    assert MODULE["_validate"]("calibration", form) == {
        "pairs": 12,
        "labeled": 12,
        "content_labeled": 0,
    }


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("choice", "winner"),
        ("content_issue", False),
        ("evidence", ["B99"]),
        ("reason", None),
        ("id", "H01"),
    ],
)
def test_invalid_rating_rejected(field: str, value: Any) -> None:
    form = MODULE["_materials"]("calibration")["form"]
    form["ratings"][0][field] = value
    with pytest.raises(ValueError):
        MODULE["_validate"]("calibration", form)


def test_identity_duplicate_and_missing_rows_rejected() -> None:
    form = MODULE["_materials"]("calibration")["form"]
    for change in ("hash", "split", "duplicate", "missing", "extra"):
        altered = copy.deepcopy(form)
        if change == "hash":
            altered["packet_sha256"] = "stale"
        elif change == "split":
            altered["split"] = "holdout"
        elif change == "duplicate":
            altered["ratings"][1] = altered["ratings"][0]
        elif change == "missing":
            altered["ratings"].pop()
        else:
            altered["expected_winner"] = "A"
        with pytest.raises(ValueError):
            MODULE["_validate"]("calibration", altered)


@pytest.mark.parametrize("field", ["family", "case_id"])
def test_leakage_rejected(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    field: str,
) -> None:
    module = runpy.run_path(str(ROOT / "packet.py"))
    pairs = MODULE["_load"]()
    pairs[12][field] = pairs[0][field]
    (tmp_path / "pairs.json").write_text(json.dumps(pairs))
    monkeypatch.setitem(module["_load"].__globals__, "ROOT", tmp_path)
    with pytest.raises(ValueError, match="leakage"):
        module["_load"]()


def test_cli_is_read_only(tmp_path: Path) -> None:
    labels = tmp_path / "labels.json"
    labels.write_text(json.dumps(MODULE["_materials"]("calibration")["form"]))
    before = labels.read_bytes()
    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "packet.py"),
            "validate",
            "calibration",
            str(labels),
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    assert json.loads(result.stdout)["labeled"] == 0
    assert labels.read_bytes() == before
    invalid = subprocess.run(
        [sys.executable, str(ROOT / "packet.py"), "render", "calibration", str(labels)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert invalid.returncode != 0 and labels.read_bytes() == before
