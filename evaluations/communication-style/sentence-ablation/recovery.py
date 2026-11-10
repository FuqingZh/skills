#!/usr/bin/env python3
"""One declared format-only judge retry; preserve frozen code and failed output."""

from __future__ import annotations

import argparse
import json
import runpy
import tempfile
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
ORIGINAL = ROOT / "results/judgments/c1-1.json"
RETRY = ROOT / "results/retries/c1-1-attempt2.json"
MANIFEST = ROOT / "recovery-manifest.json"


def context() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    module = runpy.run_path(str(ROOT / "benchmark.py"))
    core = module["engine"]()
    module["verify"](core)
    module["check_controls"](core)
    manifest = core["read_json"](MANIFEST)
    expected = {
        "recovery.py",
        "recovery-protocol.json",
        "execution-manifest.json",
        "results/judgments/c1-1.json",
    }
    if set(manifest["sha256"]) != expected:
        raise ValueError("Incomplete recovery manifest")
    for name, digest in manifest["sha256"].items():
        if core["digest"](ROOT / name) != digest:
            raise ValueError(f"Recovery source changed: {name}")
    old = core["read_json"](ORIGINAL)
    if old.get("error") != "Invalid judgment: Invalid quality evidence":
        raise ValueError("Retry is only authorized for the recorded format failure")
    job = next(
        j for j in module["packets"](core) if j["case"]["id"] == "c1" and j["rep"] == 1
    )
    if old["mapping"] != job["mapping"]:
        raise ValueError("Retry input mapping changed")
    return module, core, job


def retry() -> None:
    module, core, job = context()
    if RETRY.exists():
        raise FileExistsError("The single retry already exists")
    with tempfile.TemporaryDirectory(prefix="ablation-retry-") as cwd:
        result = module["judge_one"](core, job["case"], job["answers"], cwd)
    core["save_new"](
        RETRY,
        {
            "case": "c1",
            "rep": 1,
            "mapping": job["mapping"],
            "attempt": 2,
            "original_sha256": core["digest"](ORIGINAL),
            "recovery_manifest": core["read_json"](MANIFEST),
            **result,
        },
    )
    if "error" in result:
        raise ValueError(result["error"])


def summarize() -> dict[str, Any]:
    module, core, job = context()
    record = core["read_json"](RETRY)
    if (
        "error" in record
        or record["mapping"] != job["mapping"]
        or record["original_sha256"] != core["digest"](ORIGINAL)
        or record["recovery_manifest"] != core["read_json"](MANIFEST)
    ):
        raise ValueError("Invalid recovery record")
    module["validate"](core, job["case"], job["answers"], record)
    read = core["read_json"]

    def selected(path: Path) -> Any:
        return record if path == ORIGINAL else read(path)

    core["read_json"] = selected
    result = module["summarize"](core)
    result["recovery"] = {
        "invalid_original": str(ORIGINAL.relative_to(ROOT)),
        "accepted_retry": str(RETRY.relative_to(ROOT)),
        "failed_judge_cost": read(ORIGINAL)["usage"]["cost"]["total"],
        "comparison_attempts": 17,
        "reason": "Original quality quote omitted literal Markdown markers",
    }
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("retry", "summarize"))
    args = parser.parse_args()
    if args.mode == "retry":
        retry()
    else:
        print(json.dumps(summarize(), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
