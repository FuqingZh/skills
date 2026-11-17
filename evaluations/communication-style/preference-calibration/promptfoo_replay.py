#!/usr/bin/env python3
"""Replay retained v3/v4 records in Promptfoo without invoking a model.

The generated table reports artifact validity, not preference agreement. The
versioned pair summaries remain the statistical authority. Provider errors keep
the original visible answer alongside the error; source JSON is never changed.
Each invocation writes an exclusive receipt, so a repeated job fails visibly.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import runpy
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent


def call_api(
    prompt: str, options: dict[str, Any], context: dict[str, Any]
) -> dict[str, Any]:
    config = options["config"]
    version = config["version"]
    if version not in (3, 4):
        raise ValueError("Unsupported replay version")
    name = context["vars"]["case"]
    order = context["vars"]["order"]
    if name not in {f"D{i:02}" for i in range(1, 13)} | {"I01"} or order not in (
        "original",
        "swapped",
    ):
        raise ValueError("Unsupported replay record")
    path = ROOT / f"results-v{version}" / f"{name}-{order}.json"
    raw = path.read_bytes()
    record = json.loads(raw)
    receipt = Path(config["receipts"]) / f"v{version}-{name}-{order}.json"
    provenance = {
        "source": str(path.relative_to(ROOT)),
        "sha256": hashlib.sha256(raw).hexdigest(),
        "mode": "saved-output-replay",
    }
    with receipt.open("x", encoding="utf-8") as stream:
        json.dump(provenance, stream, indent=2)
    result = {"output": record.get("answer", ""), "metadata": provenance}
    if "error" in record:
        result["error"] = record["error"]
    return result


def get_assert(output: str, context: dict[str, Any]) -> dict[str, Any]:
    value = json.loads(output)
    return {
        "pass": value["choice"] in ("A", "B", "tie", "uncertain"),
        "score": 1,
        "reason": "Retained valid artifact; not a preference-agreement score.",
    }


def prepare(destination: Path) -> None:
    versions = {
        version: runpy.run_path(str(ROOT / f"judge_v{version}.py"))
        for version in (3, 4)
    }
    summaries = {str(v): module["summarize"]() for v, module in versions.items()}
    destination.mkdir(exist_ok=False)
    receipts = destination / "receipts"
    receipts.mkdir()
    adapter = f"file://{Path(__file__).resolve()}"
    config = {
        "description": (
            "OFFLINE REPLAY v3/v4 — artifact validity only; "
            "use summary-vN.json for pair agreement"
        ),
        "prompts": ["{{case}} {{order}}"],
        "providers": [
            {
                "id": adapter,
                "label": f"v{v} saved outputs",
                "config": {
                    "version": v,
                    "receipts": str(receipts),
                    "pythonExecutable": sys.executable,
                    "workers": 3,
                    "timeout": 360000,
                    "maxRetries": 0,
                },
            }
            for v in (3, 4)
        ],
        "tests": [
            {"vars": {"case": job["id"], "order": job["order"]}}
            for job in versions[3]["jobs"]()
        ],
        "defaultTest": {"assert": [{"type": "python", "value": adapter}]},
        "evaluateOptions": {"cache": False, "maxConcurrency": 3},
    }
    for name, value in (
        ("promptfooconfig.json", config),
        ("source-summaries.json", summaries),
    ):
        with (destination / name).open("x", encoding="utf-8") as stream:
            json.dump(value, stream, ensure_ascii=False, indent=2)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("destination", type=Path)
    args = parser.parse_args()
    prepare(args.destination.resolve())


if __name__ == "__main__":
    main()
