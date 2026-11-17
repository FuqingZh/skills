"""Offline checks for exact ID resolution without modifying old quotation rules."""

from __future__ import annotations

import json
import runpy
from pathlib import Path
from typing import Any
from unittest.mock import patch

import pytest

ROOT = Path(__file__).resolve().parents[1]
DIRECTORY = ROOT / "evaluations/communication-style/preference-calibration"
SCRIPT = DIRECTORY / "openevals_id_evidence.py"
STUDY = DIRECTORY / "openevals-contribution-v1-id-evidence"


def finding(evidence: str = "P1") -> dict[str, Any]:
    return {"findings": [{"kind": "issue", "evidence": evidence, "reason": "fixture"}]}


def test_catalog_preserves_markdown_whitespace_crlf_and_unicode() -> None:
    module = runpy.run_path(str(SCRIPT))
    answer = "\r\n  甲 **乙。** 丙。 \r\n \t\r\n😀 {inputs}\n后一行。\n\n"
    spans = module["catalog"](answer)
    assert list(spans) == ["P1", "P2"]
    assert spans["P1"]["text"] == "\r\n  甲 **乙。** 丙。 "
    assert spans["P2"]["text"] == "😀 {inputs}\n后一行。"
    for span in spans.values():
        assert answer[span["start"] : span["end"]] == span["text"]
    raw = finding("P1")
    resolved = module["resolve"](raw, spans, answer)
    assert resolved["findings"][0]["evidence"] == spans["P1"]["text"]
    assert raw == finding("P1")
    assert module["resolve"]({"findings": []}, spans, answer) == {"findings": []}


@pytest.mark.parametrize("identifier", ["P", "P99", "p1", "P1 ", "P1\nP2", "甲"])
def test_unknown_or_inexact_ids_are_not_repaired(identifier: str) -> None:
    module = runpy.run_path(str(SCRIPT))
    answer = "甲\n\n乙"
    with pytest.raises(ValueError, match="Unknown evidence ID"):
        module["resolve"](finding(identifier), module["catalog"](answer), answer)


@pytest.mark.parametrize(
    "value",
    [
        {"findings": [{"kind": "other", "evidence": "P1", "reason": "fixture"}]},
        {"findings": [{"kind": "issue", "evidence": "P1", "reason": ""}]},
        {"findings": [], "score": 1},
        {"findings": [{"kind": "issue", "evidence": ["P1"], "reason": "fixture"}]},
    ],
)
def test_original_shape_checks_remain(value: object) -> None:
    module = runpy.run_path(str(SCRIPT))
    with pytest.raises(ValueError):
        module["resolve"](value, module["catalog"]("甲"), "甲")


def test_bad_catalog_and_empty_source_fail() -> None:
    module = runpy.run_path(str(SCRIPT))
    with pytest.raises(ValueError, match="No nonblank"):
        module["catalog"](" \n\n ")
    spans = module["catalog"]("甲乙")
    spans["P1"]["start"] = 1
    with pytest.raises(ValueError, match="Source catalog mismatch"):
        module["resolve"](finding(), spans, "甲乙")


@pytest.mark.parametrize("arm", ["baseline", "revised"])
@pytest.mark.parametrize("failure", [False, True])
def test_bundle_restores_namespace_and_preserves_raw_output(
    tmp_path: Path, arm: str, failure: bool
) -> None:
    module = runpy.run_path(str(SCRIPT))
    original_root = ROOT
    raw = json.dumps(finding("P99" if failure else "P1"))
    seen: list[Path] = []
    calls = 0

    def fake_transport(_system: str, _message: str) -> dict[str, Any]:
        nonlocal calls
        calls += 1
        return {"answer": raw, "usage": {"totalTokens": 5}, "seconds": 1}

    def fake_evaluate(_context: str, answer: str, invoke: Any) -> dict[str, Any]:
        seen.append(ROOT)
        schema = json.loads((ROOT / "schema.json").read_text())
        evidence = schema["properties"]["findings"]["items"]["properties"]["evidence"]
        assert evidence["enum"] == ["P1"]
        prompt = (
            (ROOT / "upstream-helpfulness.txt")
            .read_text()
            .format(inputs="question", outputs=answer)
        )
        assert "**乙。**" in prompt and "{inputs}" in prompt
        assert (ROOT / "instructions.txt").read_bytes() == (
            STUDY / "id-instructions.txt"
        ).read_bytes()
        transport = invoke("fixture", prompt)
        record: dict[str, Any] = {"transport": transport, "invocations": 1}
        parsed = json.loads(transport["answer"])
        try:
            # The evaluator normally resolves this global at its validation boundary.
            validator = fake_evaluate.__globals__["validate"]
            validator(parsed, answer)
            record["diagnostic"] = parsed
        except ValueError as exc:
            record["error"] = str(exc)
        return record

    with patch.dict(module["BASE"], {"evaluate": fake_evaluate, "SCRATCH": tmp_path}):
        result = module["evaluate_prompt"](
            STUDY, arm, "question", "甲 **乙。** {inputs}", fake_transport
        )
    assert calls == 1 and result["transport"]["answer"] == raw
    assert result["transport"]["usage"] == {"totalTokens": 5}
    assert original_root == ROOT and len(seen) == 1 and not seen[0].exists()
    assert seen[0].parent == tmp_path
    assert "validate" not in fake_evaluate.__globals__
    if failure:
        assert "diagnostic" not in result and "id_diagnostic" not in result
        assert result["error"] == "Unknown evidence ID"
    else:
        assert result["id_diagnostic"] == finding()
        assert result["diagnostic"]["findings"][0]["evidence"] == "甲 **乙。** {inputs}"


def test_frozen_semantic_guidance_and_old_failure_are_unchanged() -> None:
    module = runpy.run_path(str(SCRIPT))
    old = DIRECTORY / "openevals-contribution-v1"
    for name in ("guidance.txt", "revised-helpfulness.txt"):
        assert (STUDY / name).read_bytes() == (old / name).read_bytes()
    original = (DIRECTORY / "openevals-pilot-1/instructions.txt").read_bytes()
    expected = original.replace(
        "evidence 必须逐字引用待检查回答的一段连续原文".encode(),
        (
            "evidence 必须填写 evidence_catalog 中的一个段落编号"
            "\uff08如 P1\uff09\uff0c不要复写原文"
        ).encode(),
    )
    assert (STUDY / "id-instructions.txt").read_bytes() == expected
    jobs = json.loads((old / "jobs.json").read_text())
    assert json.loads((STUDY / "jobs.json").read_text()) == [
        job for job in jobs if job["stage"] == "transfer"
    ]
    failed = json.loads((old / "results/D06-A/revised.json").read_text())
    with pytest.raises(ValueError, match="Evidence absent from answer"):
        module["VALIDATE"](
            json.loads(failed["transport"]["answer"]), failed["answer_under_review"]
        )
    assert failed["error"] == "ValueError: Evidence absent from answer"
