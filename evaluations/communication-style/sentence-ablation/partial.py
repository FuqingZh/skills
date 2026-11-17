#!/usr/bin/env python3
"""Post-hoc diagnostics on complete cases; never claim the full study completed.

Both c1 replicates are excluded because one failed literal-evidence validation,
including its sole declared retry. The original full summary remains blocked.
No model calls, score repairs or original artifact changes occur here.
"""

from __future__ import annotations

import json
import runpy
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent


def summarize() -> dict[str, Any]:
    recovery = runpy.run_path(str(ROOT / "recovery.py"))
    module, core, _job = recovery["context"]()
    read = core["read_json"]
    retry_path = ROOT / "results/retries/c1-1-attempt2.json"
    retry = read(retry_path)
    if retry.get("error") != "Invalid judgment: Invalid quality evidence":
        raise ValueError("Partial analysis requires the documented failed retry")
    if retry["original_sha256"] != core["digest"](ROOT / "results/judgments/c1-1.json"):
        raise ValueError("Failed retry provenance mismatch")
    cases = read(ROOT / "cases.json")
    included = [c for c in cases if c["id"] != "c1"]
    if len(included) != 7:
        raise ValueError("Unexpected partial case selection")

    def selected(path: Path) -> Any:
        return included if path == ROOT / "cases.json" else read(path)

    core["read_json"] = selected
    result = module["summarize"](core)
    generation_cost = sum(
        read(p)["usage"]["cost"]["total"]
        for p in (ROOT / "results/benchmark").glob("*.json")
        if p.name != "run.json"
    )
    comparison_cost = sum(
        read(p)["usage"]["cost"]["total"]
        for p in (ROOT / "results/judgments").glob("*.json")
    )
    result["status"] = "incomplete study; post-hoc complete-case diagnostics only"
    result["full_study_scores"] = None
    result["included_cases"] = [c["id"] for c in included]
    result["excluded_cases"] = {
        "c1": "replicate 1 and its sole retry fail literal-quote validation"
    }
    result["analysis_responses"] = 140
    result["generation_responses"] = 160
    result["comparison_attempts"] = 17
    result["total_execution_cost"] = (
        generation_cost
        + comparison_cost
        + retry["usage"]["cost"]["total"]
        + result["control_cost"]
    )
    return result


if __name__ == "__main__":
    print(json.dumps(summarize(), ensure_ascii=False, indent=2))
