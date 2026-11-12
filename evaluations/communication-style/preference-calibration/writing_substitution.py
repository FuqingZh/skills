"""Compare one literal prompt replacement with the unchanged expression baseline.

Run ``python writing_substitution.py STUDY check`` before ``generation``.
Only validation differs from the append-only writing adapter: generation,
preflight, isolation, reservations, failure retention, and no-retry behavior
are reused. Keep the historical adapter unchanged because its source is frozen
by earlier studies. A substitution must match once and leave every other character
of the decoded prompt unchanged.
"""

from __future__ import annotations

import re
import runpy
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parent
WRITING = runpy.run_path(str(ROOT / "writing_compare.py"))
ENGINE = WRITING["ENGINE"]
BASE = WRITING["BASE"]


def verify(study: Path) -> None:
    ENGINE["CHECKER"]["verify"]()
    if ENGINE["hashes"](study) != BASE["load"](study / "manifest.json"):
        raise ValueError("Substitution freeze changed")
    protocol = BASE["load"](study / "protocol.json")
    jobs = BASE["load"](study / "jobs.json")
    required = {"protocol.json", "jobs.json", "baseline.txt", "revised.txt"}
    if not required.issubset(protocol["frozen_files"]):
        raise ValueError("Incomplete substitution freeze")
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
    replacement = protocol["replacement"]
    if (
        set(replacement) != {"old", "new"}
        or not isinstance(replacement["old"], str)
        or not isinstance(replacement["new"], str)
        or not replacement["old"].strip()
        or not replacement["new"].strip()
        or replacement["old"] == replacement["new"]
    ):
        raise ValueError("Invalid replacement fields")
    baseline = (ROOT.parent / "prompts/baseline.txt").read_text(encoding="utf-8")
    if WRITING["prompt"](study, "baseline") != baseline:
        raise ValueError("Writing baseline changed")
    if baseline.count(replacement["old"]) != 1:
        raise ValueError("Replacement must match exactly once")
    expected = baseline.replace(replacement["old"], replacement["new"], 1)
    if WRITING["prompt"](study, "revised") != expected:
        raise ValueError("Unexpected change outside the replacement")


def main() -> None:
    with patch.dict(
        ENGINE["main"].__globals__,
        {
            "verify": verify,
            "preflight": WRITING["preflight"],
            "evaluate_prompt": WRITING["generate"],
        },
    ):
        ENGINE["main"]()


if __name__ == "__main__":
    main()
