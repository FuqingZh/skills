#!/usr/bin/env python3
"""Apply explicit continuation authorization without rewriting the frozen stop.

Only the runner's P01 gate read is redirected. Prompts, schema, evaluation,
network guard and attempt reservations remain in the unchanged frozen runner.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import os
import runpy
import subprocess
import sys
from pathlib import Path
from typing import Any
from unittest.mock import patch

ROOT = Path(__file__).resolve().parent
PI_DIR = Path.home() / ".local/share/mise/installs/pi/1.5.0/pi"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("check", "run"))
    args = parser.parse_args()
    module = runpy.run_path(str(ROOT / "probe.py"))
    original_load = module["load"]
    approval = original_load(ROOT / "continuation-1.json")
    if (
        approval["decision"] != "continue"
        or approval["authorized_case"] != "P02"
        or approval["max_additional_invocations"] != 2
    ):
        raise ValueError("Unsupported continuation")
    for name, expected in approval["preserve"].items():
        if hashlib.sha256((ROOT / name).read_bytes()).hexdigest() != expected:
            raise ValueError(f"Historical record changed: {name}")
    if module["hashes"]() != original_load(ROOT / "manifest.json"):
        raise ValueError("Frozen source changed")
    packages = {
        d.metadata["Name"]: d.version for d in importlib.metadata.distributions()
    }
    if packages != original_load(ROOT / "preflight.json")["packages"]:
        raise ValueError("Installed dependencies changed")
    if (ROOT / "results/P02").exists():
        raise FileExistsError("P02 already reserved; no rerun")

    def read_with_continuation(path: Path) -> Any:
        if path == ROOT / "review-P01.json":
            return approval
        return original_load(path)

    if original_load(ROOT / "review-P01.json")["decision"] != "stop":
        raise ValueError("Historical stop was replaced")
    if read_with_continuation(ROOT / "review-P01.json")["decision"] != "continue":
        raise ValueError("Continuation gate not active")
    with patch.dict(
        os.environ, {"PATH": str(PI_DIR) + os.pathsep + os.environ["PATH"]}
    ):
        with module["agent"]() as directory:
            version = subprocess.run(
                ["pi", *module["CORE"]["ISOLATION"], "--version"],
                cwd=directory,
                capture_output=True,
                text=True,
                timeout=20,
                check=True,
            ).stdout.strip()
        if version != "1.5.0":
            raise ValueError("Pi runtime changed")
        if args.mode == "run":
            with (
                patch.dict(
                    module["main"].__globals__, {"load": read_with_continuation}
                ),
                patch.object(sys, "argv", [str(ROOT / "probe.py"), "P02"]),
            ):
                module["main"]()
        else:
            print("Continuation checks passed; zero model calls; Pi 1.5.0 pinned")


if __name__ == "__main__":
    main()
