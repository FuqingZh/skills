"""Resume the authorized two-case batch with additive failure diagnostics.

Reuse the frozen controller's runtime checks, network guard and case gates.
Only the output root, P03-A attempt number and transport adapter change.
Historical results and prompts remain untouched; existing output directories
still refuse reruns. Each new answer has one invocation with no automatic retry.
"""

from __future__ import annotations

import hashlib
import runpy
import sys
from pathlib import Path
from typing import Any
from unittest.mock import patch

ROOT = Path(__file__).resolve().parent
PRIOR = ROOT.parent / "openevals-pilot-2"
PILOT = runpy.run_path(str(PRIOR / "run.py"))
DIAGNOSTICS = runpy.run_path(str(PRIOR / "diagnostic_transport.py"))
VERIFY = PILOT["verify"]
EXECUTE = PILOT["execute"]
FILES = (
    "resume.py",
    "protocol.json",
    "../openevals-pilot-2/manifest.json",
    "../openevals-pilot-2/transport-repair.json",
    "../openevals-pilot-2/diagnostic_transport.py",
    "../openevals-pilot-2/results/P03/A.json",
    "../openevals-pilot-2/review-P03.json",
)


def hashes() -> dict[str, str]:
    return {
        name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() for name in FILES
    }


def verify() -> None:
    VERIFY()
    if hashes() != PILOT["BASE"]["load"](ROOT / "manifest.json"):
        raise ValueError("Recovery freeze changed")
    repair = PILOT["BASE"]["load"](PRIOR / "transport-repair.json")
    for key in ("adapter", "frozen_transport", "original_failure"):
        actual = hashlib.sha256((PRIOR / repair[key]).read_bytes()).hexdigest()
        if actual != repair[key + "_sha256"]:
            raise ValueError("Repair or historical evidence changed")


def execute(case_id: str) -> None:
    save_original = PILOT["BASE"]["save"]

    def save(path: Path, value: Any) -> None:
        if path == ROOT / "results/P03/A.started.json":
            value = {**value, "attempt": 2}
        save_original(path, value)

    with (
        patch.dict(EXECUTE.__globals__, {"ROOT": ROOT}),
        patch.dict(PILOT["BASE"], {"save": save}),
    ):
        EXECUTE(case_id)


def main() -> None:
    if len(sys.argv) != 2 or sys.argv[1] not in ("check", "P03", "P04"):
        raise SystemExit("Usage: resume.py check|P03|P04")
    PILOT["BASE"]["live"].__globals__["CORE"]["invoke"] = DIAGNOSTICS["invoke"]
    with patch.dict(PILOT["main"].__globals__, {"verify": verify, "execute": execute}):
        PILOT["main"]()


if __name__ == "__main__":
    main()
