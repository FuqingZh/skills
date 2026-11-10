#!/usr/bin/env python3
"""Run the frozen cross-domain comparison with pre-generation judge controls."""

from __future__ import annotations

import argparse
import json
import runpy
import tempfile
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
PARENT = ROOT.parent
TRACKED = (
    "benchmark.py",
    "protocol.json",
    "cases.json",
    "controls.json",
    "judge.txt",
    "prompts/baseline.txt",
    "prompts/revised.txt",
    "../run.py",
    "../summarize.py",
    "../execution-manifest.json",
)


def engine() -> dict[str, Any]:
    core = runpy.run_path(str(PARENT / "run.py"))
    core["verify_sources"]()
    namespace = core["generate"].__globals__
    namespace["ROOT"] = ROOT
    namespace["ARMS"] = ("baseline", "revised")
    return core


def verify(core: dict[str, Any]) -> None:
    manifest = core["read_json"](ROOT / "execution-manifest.json")["sha256"]
    if set(manifest) != set(TRACKED):
        raise ValueError("Incomplete study manifest")
    for name, expected in manifest.items():
        if core["digest"](ROOT / name) != expected:
            raise ValueError(f"Frozen study source changed: {name}")


def control_matches(
    core: dict[str, Any], fixture: dict[str, Any], record: dict[str, Any]
) -> bool:
    core["validate_ratings"](record, fixture["answers"], len(fixture["required"]))
    return all(
        {s["kind"] for s in r["style"]} == set(fixture["expected"][r["id"]])
        and not r["critical"]
        and all(item["met"] for item in r["content"])
        and r["clarity"] == "clear"
        for r in record["ratings"]
    )


def check_controls(core: dict[str, Any]) -> None:
    manifest = core["read_json"](ROOT / "execution-manifest.json")
    for fixture in core["read_json"](ROOT / "controls.json"):
        record = core["read_json"](ROOT / "results/controls" / f"{fixture['id']}.json")
        if (
            "error" in record
            or record.get("source_manifest") != manifest
            or not control_matches(core, fixture, record)
        ):
            raise ValueError(f"Judge control failed: {fixture['id']}")


def calibrate(core: dict[str, Any]) -> None:
    fixtures = core["read_json"](ROOT / "controls.json")
    output = ROOT / "results/controls"
    if any((output / f"{f['id']}.json").exists() for f in fixtures):
        raise FileExistsError("Control attempts already exist")
    protocol = core["read_json"](ROOT / "protocol.json")
    manifest = core["read_json"](ROOT / "execution-manifest.json")
    with tempfile.TemporaryDirectory(prefix="style-control-") as cwd:
        for fixture in fixtures:
            prompt = json.dumps(
                {
                    "task": fixture["prompt"],
                    "required": fixture["required"],
                    "critical_examples": fixture["critical"],
                    "answers": fixture["answers"],
                },
                ensure_ascii=False,
            )
            result = core["invoke"](
                (ROOT / "judge.txt").read_text(encoding="utf-8"),
                prompt,
                protocol["judge"],
                cwd,
                protocol["timeout_seconds"],
            )
            if "error" not in result:
                try:
                    parsed = json.loads(result["answer"])
                    result["ratings"] = parsed["ratings"]
                    result["matches_expected"] = control_matches(core, fixture, result)
                except (ValueError, KeyError, TypeError) as exc:
                    result["error"] = f"Invalid control judgment: {exc}"
            core["save_new"](
                output / f"{fixture['id']}.json",
                {"control": fixture["id"], "source_manifest": manifest, **result},
            )
            print(
                "control",
                fixture["id"],
                result.get("matches_expected", False),
                flush=True,
            )
    check_controls(core)


def summary() -> dict[str, Any]:
    module = runpy.run_path(str(PARENT / "summarize.py"))
    module["summarize"].__globals__["ROOT"] = ROOT
    return module["summarize"]("benchmark")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "mode", choices=("freeze", "calibrate", "generate", "judge", "summarize")
    )
    args = parser.parse_args()
    core = engine()
    if args.mode == "freeze":
        core["save_new"](
            ROOT / "execution-manifest.json",
            {"sha256": {name: core["digest"](ROOT / name) for name in TRACKED}},
        )
        return
    verify(core)
    if args.mode == "calibrate":
        calibrate(core)
        return
    check_controls(core)
    if args.mode == "generate":
        core["generate"](
            "benchmark", ["baseline", "revised"], ROOT / "results/benchmark"
        )
    elif args.mode == "judge":
        core["judge"](
            "benchmark",
            ROOT / "results/benchmark",
            ROOT / "results/benchmark-judgments",
        )
    else:
        print(json.dumps(summary(), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
