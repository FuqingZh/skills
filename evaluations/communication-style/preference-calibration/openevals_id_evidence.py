"""Opt-in paragraph-ID evidence contract for the existing comparison runner.

Model evidence is an exact catalog ID. Resolved evidence is a program-owned
slice of the original answer, not a model quotation or repaired output. Keep
both forms; a valid ID proves source location, not relevance or correct judgment.
Historical literal-quotation runs and validators are unchanged.
"""

from __future__ import annotations

import hashlib
import json
import re
import runpy
import tempfile
from collections.abc import Callable
from pathlib import Path
from typing import Any, TypedDict
from unittest.mock import patch

ROOT = Path(__file__).resolve().parent
ENGINE = runpy.run_path(str(ROOT / "openevals_compare.py"))
BASE = ENGINE["BASE"]
BASE_ROOT = ENGINE["BASE_ROOT"]
VALIDATE = BASE["validate"]


class Span(TypedDict):
    """Exact source slice; offsets are Python Unicode code points, end-exclusive."""

    start: int
    end: int
    text: str


def catalog(answer: str) -> dict[str, Span]:
    """Number nonblank paragraphs without normalizing their contents or Markdown."""
    result: dict[str, Span] = {}
    start = 0
    boundaries = [
        (m.start(), m.end()) for m in re.finditer(r"\r?\n(?:[ \t]*\r?\n)+", answer)
    ]
    for end, following in [*boundaries, (len(answer), len(answer))]:
        text = answer[start:end]
        if text.strip():
            result[f"P{len(result) + 1}"] = {"start": start, "end": end, "text": text}
        start = following
    if not result:
        raise ValueError("No nonblank source paragraph")
    return result


def schema_for(spans: dict[str, Span]) -> dict[str, Any]:
    schema = BASE["load"](BASE_ROOT / "schema.json")
    evidence = schema["properties"]["findings"]["items"]["properties"]["evidence"]
    evidence["enum"] = list(spans)
    return schema


def template(study: Path, arm: str, spans: dict[str, Span]) -> str:
    text = json.dumps(
        {key: span["text"] for key, span in spans.items()}, ensure_ascii=False
    )
    escaped = text.replace("{", "{{").replace("}", "}}")
    return (
        ENGINE["prompt"](study, arm)
        + "\n<evidence_catalog>\n"
        + escaped
        + "\n</evidence_catalog>\n"
    )


def resolve(value: Any, spans: dict[str, Span], answer: str) -> dict[str, Any]:
    """Validate the raw ID result, then validate exact source slices separately.

    No fuzzy match, trimming, ID guessing, quote reconstruction or partial rescue
    is permitted. Paragraph-level references intentionally trade finer granularity
    for deterministic source location; reasons still require semantic review.
    """
    try:
        VALIDATE(value, "\n".join(spans))
    except ValueError as exc:
        if str(exc) == "Evidence absent from answer":
            raise ValueError("Unknown evidence ID") from exc
        raise
    findings: list[dict[str, Any]] = []
    for finding in value["findings"]:
        identifier = finding["evidence"]
        if identifier not in spans:
            raise ValueError("Unknown evidence ID")
        span = spans[identifier]
        if answer[span["start"] : span["end"]] != span["text"]:
            raise ValueError("Source catalog mismatch")
        findings.append({**finding, "evidence": span["text"]})
    result = {"findings": findings}
    VALIDATE(result, answer)
    return result


def evaluate_prompt(
    study: Path,
    arm: str,
    context: str,
    answer: str,
    invoke: Callable[[str, str], dict[str, Any]],
) -> dict[str, Any]:
    spans = catalog(answer)

    def validate_ids(value: Any, _answer: str) -> None:
        resolve(value, spans, answer)

    with tempfile.TemporaryDirectory(
        prefix="id-prompt-", dir=BASE["SCRATCH"]
    ) as directory:
        bundle = Path(directory)
        (bundle / "schema.json").write_text(
            json.dumps(schema_for(spans)), encoding="utf-8"
        )
        (bundle / "instructions.txt").write_bytes(
            (study / "id-instructions.txt").read_bytes()
        )
        (bundle / "upstream-helpfulness.txt").write_text(
            template(study, arm, spans), encoding="utf-8"
        )
        with patch.dict(
            BASE["evaluate"].__globals__, {"ROOT": bundle, "validate": validate_ids}
        ):
            record = BASE["evaluate"](context, answer, invoke)
    record["evidence_contract"] = "paragraph-id-v1"
    record["evidence_catalog"] = spans
    record["answer_sha256"] = hashlib.sha256(answer.encode("utf-8")).hexdigest()
    if "diagnostic" in record:
        record["id_diagnostic"] = record.pop("diagnostic")
        record["diagnostic"] = resolve(record["id_diagnostic"], spans, answer)
    return record


def preflight(study: Path) -> dict[str, Any]:
    answer = "甲 **乙。** 丙。\n\n含 {inputs} 的第二段。"
    spans = catalog(answer)
    good = {"findings": [{"kind": "strength", "evidence": "P1", "reason": "fixture"}]}
    fixtures: list[tuple[dict[str, Any], bool]] = [
        (good, True),
        ({"findings": []}, True),
        (
            {"findings": [{"kind": "issue", "evidence": "P99", "reason": "fixture"}]},
            False,
        ),
        (
            {"findings": [{"kind": "issue", "evidence": "甲", "reason": "fixture"}]},
            False,
        ),
    ]
    calls = 0
    for arm in ("baseline", "revised"):
        for value, valid in fixtures:
            expected = template(study, arm, spans).format(
                inputs="fixture", outputs=answer
            )
            raw = json.dumps(value, ensure_ascii=False)

            def fake(
                system: str,
                message: str,
                expected_message: str = expected,
                raw_answer: str = raw,
            ) -> dict[str, Any]:
                nonlocal calls
                calls += 1
                expected_system = (study / "id-instructions.txt").read_text() + "\n"
                expected_system += json.dumps(schema_for(spans), ensure_ascii=False)
                if system != expected_system or json.loads(message) != [
                    {"role": "user", "content": expected_message}
                ]:
                    raise ValueError("Unexpected request")
                return {"answer": raw_answer}

            record = evaluate_prompt(study, arm, "fixture", answer, fake)
            if ("error" not in record) != valid or record["invocations"] != 1:
                raise ValueError("ID contract fixture failed")
            if record["transport"]["answer"] != raw:
                raise ValueError("Raw output changed")
            if valid:
                if record["id_diagnostic"] != value:
                    raise ValueError("Raw parsed result changed")
                VALIDATE(record["diagnostic"], answer)
    return {
        "status": "passed",
        "manifest_sha256": hashlib.sha256(
            (study / "manifest.json").read_bytes()
        ).hexdigest(),
        "synthetic_calls": calls,
        "model_calls": 0,
        "evidence_contract": "paragraph-id-v1",
    }


def main() -> None:
    with patch.dict(
        ENGINE["main"].__globals__,
        {"evaluate_prompt": evaluate_prompt, "preflight": preflight},
    ):
        ENGINE["main"]()


if __name__ == "__main__":
    main()
