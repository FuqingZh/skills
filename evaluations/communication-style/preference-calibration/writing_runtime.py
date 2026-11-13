"""Run a literal-substitution study on an explicitly frozen Pi 1.5.2 executable.

Usage: writing_runtime.py STUDY_DIRECTORY check|generation

The protocol must bind this adapter and a runtime object containing version,
executable (an absolute path to pi), and sha256. Historical evaluators remain
unchanged. Their source/dependency checks are preserved here; the runtime check
uses the new pin. Request isolation, parsing, reservations and failure retention
remain owned by the existing substitution adapter and serial runner.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import os
import re
import runpy
import shutil
import subprocess
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parent
SUBSTITUTION = runpy.run_path(str(ROOT / "writing_substitution.py"))
ENGINE = SUBSTITUTION["ENGINE"]
CHECKER = ENGINE["CHECKER"]
BASE = ENGINE["BASE"]
SUPPORTED_VERSION = "1.5.2"


def _runtime(study: Path) -> Path:
    protocol = BASE["load"](study / "protocol.json")
    frozen = {(study / name).resolve() for name in protocol["frozen_files"]}
    if not {Path(__file__).resolve(), study / "protocol.json"}.issubset(frozen):
        raise ValueError("Missing runtime freeze")
    if ENGINE["hashes"](study) != BASE["load"](study / "manifest.json"):
        raise ValueError("Runtime study freeze changed")
    runtime = protocol["runtime"]
    if runtime.get("version") != SUPPORTED_VERSION:
        raise ValueError("Unsupported Pi runtime")
    executable, digest = runtime.get("executable"), runtime.get("sha256")
    if not isinstance(executable, str) or not isinstance(digest, str):
        raise ValueError("Invalid runtime pin")
    binary = Path(executable)
    if (
        not binary.is_absolute()
        or binary.name != "pi"
        or not binary.is_file()
        or not os.access(binary, os.X_OK)
        or not re.fullmatch(r"[0-9a-f]{64}", digest)
    ):
        raise ValueError("Invalid runtime pin")
    with binary.open("rb") as handle:
        if hashlib.file_digest(handle, "sha256").hexdigest() != digest:
            raise ValueError("Pi executable changed")
    return binary.resolve()


def _verify_environment(study: Path) -> None:
    # Mirror the frozen checker's non-runtime guards without editing its 1.5.0
    # contract or falsifying a subprocess result to make that check pass.
    if BASE["hashes"]() != BASE["load"](ENGINE["BASE_ROOT"] / "manifest.json"):
        raise ValueError("First-pilot judge changed")
    if CHECKER["hashes"]() != BASE["load"](CHECKER["ROOT"] / "manifest.json"):
        raise ValueError("Second-pilot sources changed")
    packages = {
        d.metadata["Name"]: d.version for d in importlib.metadata.distributions()
    }
    if packages != BASE["load"](ENGINE["BASE_ROOT"] / "preflight.json")["packages"]:
        raise ValueError("Installed dependencies changed")
    binary = _runtime(study)
    found = shutil.which("pi")
    if found is None or Path(found).resolve() != binary:
        raise ValueError("Pi executable selection changed")
    with BASE["agent"]() as directory:
        version = subprocess.run(
            ["pi", *BASE["CORE"]["ISOLATION"], "--version"],
            cwd=directory,
            capture_output=True,
            text=True,
            timeout=20,
            check=True,
        ).stdout.strip()
    if version != SUPPORTED_VERSION:
        raise ValueError("Pi version changed")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("study", type=Path)
    parser.add_argument("stage", choices=("check", "generation"))
    args = parser.parse_args()
    study = args.study.resolve()
    if study.parent != ROOT:
        raise ValueError("Study must be a direct child of the calibration directory")
    binary = _runtime(study)
    with patch.dict(
        CHECKER,
        {"PI_DIR": binary.parent, "verify": lambda: _verify_environment(study)},
    ):
        SUBSTITUTION["main"]()


if __name__ == "__main__":
    main()
