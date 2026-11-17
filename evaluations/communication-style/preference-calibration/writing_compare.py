"""Generate answers with frozen writing prompts through the existing serial runner.

Usage: writing_compare.py STUDY_DIRECTORY check|generation

Only the request adapter changes: no judge, reference answer or output schema is
sent. Existing isolation, reservations, failure retention and no-retry behavior
remain owned by openevals_compare. Results retain the exact generator request.
"""

from __future__ import annotations

import hashlib
import re
import runpy
from collections.abc import Callable
from pathlib import Path
from typing import Any
from unittest.mock import patch

ROOT = Path(__file__).resolve().parent
ENGINE = runpy.run_path(str(ROOT / "openevals_compare.py"))
BASE = ENGINE["BASE"]


def prompt(study: Path, arm: str) -> str:
    if arm not in ("baseline", "revised"):
        raise ValueError("Unknown writing arm")
    return (study / f"{arm}.txt").read_text(encoding="utf-8")


def verify(study: Path) -> None:
    ENGINE["CHECKER"]["verify"]()
    if ENGINE["hashes"](study) != BASE["load"](study / "manifest.json"):
        raise ValueError("Writing freeze changed")
    protocol = BASE["load"](study / "protocol.json")
    jobs = BASE["load"](study / "jobs.json")
    if protocol["generator"] != BASE["CONFIG"]:
        raise ValueError("Generator configuration changed")
    if protocol["stages"] != ["generation"] or len(jobs) * 2 != protocol["max_calls"]:
        raise ValueError("Writing stage or budget mismatch")
    if not jobs or len({job["id"] for job in jobs}) != len(jobs):
        raise ValueError("Empty or duplicate writing jobs")
    for job in jobs:
        if (
            not re.fullmatch(r"[A-Za-z0-9_-]+", job["id"])
            or job["stage"] != "generation"
            or sorted(job["order"]) != ["baseline", "revised"]
            or not job["context"].strip()
            or job["answer"] != ""
        ):
            raise ValueError("Invalid writing job")
    baseline = (ROOT.parent / "prompts/baseline.txt").read_text(encoding="utf-8")
    delta = (study / "guidance.txt").read_text(encoding="utf-8")
    if prompt(study, "baseline") != baseline or not delta.strip():
        raise ValueError("Invalid writing baseline or guidance")
    if prompt(study, "revised") != baseline.rstrip() + "\n\n" + delta:
        raise ValueError("Unexpected writing prompt change")


def generate(
    study: Path,
    arm: str,
    context: str,
    answer: str,
    invoke: Callable[[str, str], dict[str, Any]],
) -> dict[str, Any]:
    if answer:
        raise ValueError("Reference answers prohibited")
    system = prompt(study, arm)
    try:
        result = invoke(system, context)
    except Exception as exc:
        result = {"error": f"Invocation raised {type(exc).__name__}; details withheld"}
    record = {
        "task": "answer_generation",
        "request": {
            "system": system,
            "messages": [{"role": "user", "content": context}],
        },
        "generator": BASE["CONFIG"],
        "invocations": 1,
        "transport": result,
    }
    if "error" in result:
        record["error"] = result["error"]
    return record


def preflight(study: Path) -> dict[str, Any]:
    calls: list[tuple[str, str]] = []

    def fake(system: str, context: str) -> dict[str, Any]:
        calls.append((system, context))
        return {"answer": "fixture"}

    for job in BASE["load"](study / "jobs.json"):
        for arm in job["order"]:
            record = generate(study, arm, job["context"], job["answer"], fake)
            if record["transport"]["answer"] != "fixture":
                raise ValueError("Writing fixture failed")
    return {
        "status": "passed",
        "manifest_sha256": hashlib.sha256(
            (study / "manifest.json").read_bytes()
        ).hexdigest(),
        "synthetic_calls": len(calls),
        "model_calls": 0,
        "task": "answer_generation_without_judge",
    }


def main() -> None:
    with patch.dict(
        ENGINE["main"].__globals__,
        {"verify": verify, "preflight": preflight, "evaluate_prompt": generate},
    ):
        ENGINE["main"]()


if __name__ == "__main__":
    main()
