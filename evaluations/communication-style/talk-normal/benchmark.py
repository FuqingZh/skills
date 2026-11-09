#!/usr/bin/env python3
"""Compare the complete pinned upstream prompt with a fresh concurrent baseline.

Reuse the parent runner, validator, and summary calculations without modifying
its frozen study. Only the in-memory case split is mapped to `benchmark`; the
original cases, prompts, criteria, and old results remain byte-identical.
"""

from __future__ import annotations

import argparse
import json
import runpy
from collections.abc import Callable
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
PARENT = ROOT.parent
TRACKED = (
    "benchmark.py",
    "protocol.json",
    "judge.txt",
    "prompts/baseline.txt",
    "prompts/talk-normal.txt",
    "upstream-LICENSE.txt",
    "../cases.json",
    "../run.py",
    "../summarize.py",
    "../execution-manifest.json",
)


def benchmark_loader(original: Callable[[Path], Any]) -> Callable[[Path], Any]:
    """Present all original cases to the shared engine as one fixed comparison."""

    def load(path: Path) -> Any:
        if path == ROOT / "cases.json":
            return [
                {**case, "split": "benchmark"}
                for case in original(PARENT / "cases.json")
            ]
        return original(path)

    return load


def engine() -> dict[str, Any]:
    core = runpy.run_path(str(PARENT / "run.py"))
    core["verify_sources"]()
    namespace = core["generate"].__globals__
    namespace["read_json"] = benchmark_loader(namespace["read_json"])
    namespace["ROOT"] = ROOT
    namespace["ARMS"] = ("baseline", "talk-normal")
    return core


def verify(core: dict[str, Any]) -> None:
    manifest = core["read_json"](ROOT / "execution-manifest.json")["sha256"]
    if set(manifest) != set(TRACKED):
        raise ValueError("Incomplete follow-up manifest")
    for name, expected in manifest.items():
        if core["digest"](ROOT / name) != expected:
            raise ValueError(f"Frozen follow-up source changed: {name}")


def summary() -> dict[str, Any]:
    module = runpy.run_path(str(PARENT / "summarize.py"))
    namespace = module["summarize"].__globals__
    namespace["load"] = benchmark_loader(namespace["load"])
    namespace["ROOT"] = ROOT
    return module["summarize"]("benchmark")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("freeze", "generate", "judge", "summarize"))
    args = parser.parse_args()
    core = engine()
    if args.mode == "freeze":
        core["save_new"](
            ROOT / "execution-manifest.json",
            {"sha256": {name: core["digest"](ROOT / name) for name in TRACKED}},
        )
        return
    verify(core)
    if args.mode == "generate":
        core["generate"](
            "benchmark", ["baseline", "talk-normal"], ROOT / "results/benchmark"
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
