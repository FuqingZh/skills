#!/usr/bin/env python3
"""Run only the second human-labeled batch using the unchanged first-pilot judge.

Feedback files are hash-bound for audit, never supplied to the model. Each case
is reserved once; malformed output stops execution without repair or retry.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import os
import runpy
import socket
import subprocess
from pathlib import Path
from typing import Any
from unittest.mock import patch

ROOT = Path(__file__).resolve().parent
BASE_ROOT = ROOT.parent / "openevals-pilot-1"
BASE = runpy.run_path(str(BASE_ROOT / "probe.py"))
PI_DIR = Path.home() / ".local/share/mise/installs/pi/1.5.0/pi"
FILES = (
    "run.py",
    "protocol.json",
    "../deletion-pilot-2.json",
    "../deletion-pilot-2-feedback.json",
    "../deletion-pilot-2-feedback-supplement-1.json",
    "../openevals-pilot-1/manifest.json",
    "../openevals-pilot-1/preflight.json",
)


def hashes() -> dict[str, str]:
    return {
        name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() for name in FILES
    }


def verify() -> None:
    if BASE["hashes"]() != BASE["load"](BASE_ROOT / "manifest.json"):
        raise ValueError("First-pilot judge changed")
    if hashes() != BASE["load"](ROOT / "manifest.json"):
        raise ValueError("Second-pilot sources changed")
    packages = {
        d.metadata["Name"]: d.version for d in importlib.metadata.distributions()
    }
    if packages != BASE["load"](BASE_ROOT / "preflight.json")["packages"]:
        raise ValueError("Installed dependencies changed")
    with BASE["agent"]() as directory:
        version = subprocess.run(
            ["pi", *BASE["CORE"]["ISOLATION"], "--version"],
            cwd=directory,
            capture_output=True,
            text=True,
            timeout=20,
            check=True,
        ).stdout.strip()
    if version != "1.5.0":
        raise ValueError("Pi version changed")


def execute(case_id: str) -> None:
    if case_id == "P04":
        review = BASE["load"](ROOT / "review-P03.json")
        if review["decision"] != "continue":
            raise ValueError("P03 has not passed the continuation gate")
    output = ROOT / "results" / case_id
    output.mkdir(parents=True, exist_ok=False)
    cases = BASE["load"](ROOT.parent / "deletion-pilot-2.json")["cases"]
    case = next(row for row in cases if row["id"] == case_id)
    for side in ("A", "B"):
        BASE["save"](
            output / f"{side}.started.json",
            {"case": case_id, "side": side, "attempt": 1},
        )
        record = BASE["evaluate"](case["context"], case["answers"][side], BASE["live"])
        BASE["save"](output / f"{side}.json", record)
        if "error" in record:
            raise RuntimeError("Failed output retained; no retry or next case")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("freeze", "check", "P03", "P04"))
    args = parser.parse_args()
    blocked: list[str] = []

    def deny(*_args: Any, **_kwargs: Any) -> Any:
        blocked.append("blocked")
        raise RuntimeError("In-process networking prohibited")

    environment = {
        "PATH": str(PI_DIR) + os.pathsep + os.environ["PATH"],
        "LANGSMITH_TRACING": "false",
        "LANGCHAIN_TRACING_V2": "false",
        "LANGCHAIN_TRACING": "false",
    }
    with (
        patch.dict(os.environ, environment),
        patch.object(socket.socket, "connect", deny),
        patch.object(socket.socket, "connect_ex", deny),
        patch.object(socket, "getaddrinfo", deny),
    ):
        if args.mode == "freeze":
            BASE["save"](ROOT / "manifest.json", hashes())
        else:
            verify()
            if args.mode != "check":
                execute(args.mode)
        if blocked:
            raise RuntimeError("Unexpected networking; stop")
    print(json.dumps({"mode": args.mode, "in_process_network_attempts": len(blocked)}))


if __name__ == "__main__":
    main()
