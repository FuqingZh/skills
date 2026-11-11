"""Serial, manifest-bound comparison of judge prompts using the frozen evaluator.

Usage: openevals_compare.py STUDY_DIRECTORY check|STAGE

Study data and arm order are fixed before calls. Each stage reserves itself once,
requires the preceding review, and stops on any failed output. Prompt selection
uses a temporary bundle in a private evaluator namespace; schema, system
instructions, model, isolation and parsing stay unchanged. No component fork,
concurrent namespace mutation, automatic winner, repair or retry is introduced.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import runpy
import shutil
import socket
import tempfile
from collections.abc import Callable
from pathlib import Path
from typing import Any
from unittest.mock import patch

ROOT = Path(__file__).resolve().parent
CHECKER = runpy.run_path(str(ROOT / "openevals-pilot-2/run.py"))
BASE = CHECKER["BASE"]
BASE_ROOT = ROOT / "openevals-pilot-1"
DIAGNOSTICS = runpy.run_path(str(ROOT / "openevals-pilot-2/diagnostic_transport.py"))


def hashes(study: Path) -> dict[str, str]:
    return {
        name: hashlib.sha256((study / name).read_bytes()).hexdigest()
        for name in BASE["load"](study / "protocol.json")["frozen_files"]
    }


def prompt(study: Path, arm: str) -> str:
    if arm == "baseline":
        return (BASE_ROOT / "upstream-helpfulness.txt").read_text(encoding="utf-8")
    if arm == "revised":
        return (study / "revised-helpfulness.txt").read_text(encoding="utf-8")
    raise ValueError("Unknown arm")


def verify(study: Path) -> None:
    CHECKER["verify"]()
    if hashes(study) != BASE["load"](study / "manifest.json"):
        raise ValueError("Comparison freeze changed")
    protocol = BASE["load"](study / "protocol.json")
    jobs = BASE["load"](study / "jobs.json")
    if len(jobs) * 2 != protocol["max_calls"]:
        raise ValueError("Call budget mismatch")
    if len({job["id"] for job in jobs}) != len(jobs):
        raise ValueError("Duplicate job")
    for job in jobs:
        if (
            not re.fullmatch(r"[A-Za-z0-9_-]+", job["id"])
            or job["stage"] not in protocol["stages"]
            or sorted(job["order"]) != ["baseline", "revised"]
        ):
            raise ValueError("Invalid job identity, stage or arms")
    guidance = (study / "guidance.txt").read_text(encoding="utf-8").rstrip()
    expected = prompt(study, "baseline").replace("<inputs>", guidance + "\n\n<inputs>")
    if prompt(study, "revised") != expected:
        raise ValueError("Unexpected change outside the added guidance")


def evaluate_prompt(
    study: Path,
    arm: str,
    context: str,
    answer: str,
    invoke: Callable[[str, str], dict[str, Any]],
) -> dict[str, Any]:
    """Select a prompt for the unchanged evaluator, restoring its root on return.

    This is serial-only. Both arms use byte-identical schema and system files;
    the selected template is the only changed model input. The frozen Client
    records the actual rendered request, including the selected prompt.
    """
    with tempfile.TemporaryDirectory(
        prefix="prompt-", dir=BASE["SCRATCH"]
    ) as directory:
        bundle = Path(directory)
        for name in ("schema.json", "instructions.txt"):
            shutil.copyfile(BASE_ROOT / name, bundle / name)
        (bundle / "upstream-helpfulness.txt").write_text(
            prompt(study, arm), encoding="utf-8"
        )
        with patch.dict(BASE["evaluate"].__globals__, {"ROOT": bundle}):
            return BASE["evaluate"](context, answer, invoke)


def preflight(study: Path) -> dict[str, Any]:
    calls = 0
    for arm in ("baseline", "revised"):
        expected = prompt(study, arm).format(inputs="fixture", outputs="甲")

        def fake(
            system: str, message: str, expected_message: str = expected
        ) -> dict[str, Any]:
            nonlocal calls
            calls += 1
            original_system = (BASE_ROOT / "instructions.txt").read_text() + "\n"
            original_system += json.dumps(
                BASE["load"](BASE_ROOT / "schema.json"), ensure_ascii=False
            )
            if system != original_system or json.loads(message) != [
                {"role": "user", "content": expected_message}
            ]:
                raise ValueError("Prompt selection changed other request fields")
            return {"answer": '{"findings": []}'}

        record = evaluate_prompt(study, arm, "fixture", "甲", fake)
        if "error" in record or record["invocations"] != 1:
            raise ValueError("Prompt selection fixture failed")
    return {
        "status": "passed",
        "manifest_sha256": hashlib.sha256(
            (study / "manifest.json").read_bytes()
        ).hexdigest(),
        "synthetic_calls": calls,
        "model_calls": 0,
    }


def execute(study: Path, stage: str) -> None:
    stages = BASE["load"](study / "protocol.json")["stages"]
    index = stages.index(stage)
    checked = BASE["load"](study / "preflight.json")
    digest = hashlib.sha256((study / "manifest.json").read_bytes()).hexdigest()
    if checked["status"] != "passed" or checked["manifest_sha256"] != digest:
        raise ValueError("Matching preflight required")
    if index:
        review = BASE["load"](study / f"review-{stages[index - 1]}.json")
        if review["decision"] != "continue":
            raise ValueError("Previous stage not approved")
    jobs = [job for job in BASE["load"](study / "jobs.json") if job["stage"] == stage]
    BASE["save"](study / "results" / f"{stage}.started.json", {"stage": stage})
    for job in jobs:
        output = study / "results" / job["id"]
        output.mkdir(exist_ok=False)
        for arm in job["order"]:
            BASE["save"](
                output / f"{arm}.started.json",
                {"job": job["id"], "arm": arm, "attempt": 1},
            )
            record = evaluate_prompt(
                study, arm, job["context"], job["answer"], BASE["live"]
            )
            BASE["save"](output / f"{arm}.json", record)
            if "error" in record:
                raise RuntimeError("Failed output retained; stop without retry")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("study", type=Path)
    parser.add_argument("stage")
    args = parser.parse_args()
    study = args.study.resolve()
    if study.parent != ROOT:
        raise ValueError("Study must be a direct child of the calibration directory")
    if args.stage not in ["check", *BASE["load"](study / "protocol.json")["stages"]]:
        raise ValueError("Unknown stage")
    blocked: list[str] = []

    def deny(*_args: Any, **_kwargs: Any) -> Any:
        blocked.append("blocked")
        raise RuntimeError("In-process networking prohibited")

    environment = {
        "PATH": str(CHECKER["PI_DIR"]) + os.pathsep + os.environ["PATH"],
        "LANGSMITH_TRACING": "false",
        "LANGCHAIN_TRACING_V2": "false",
        "LANGCHAIN_TRACING": "false",
    }
    BASE["live"].__globals__["CORE"]["invoke"] = DIAGNOSTICS["invoke"]
    with (
        patch.dict(os.environ, environment),
        patch.object(socket.socket, "connect", deny),
        patch.object(socket.socket, "connect_ex", deny),
        patch.object(socket, "getaddrinfo", deny),
    ):
        verify(study)
        report = preflight(study) if args.stage == "check" else None
        if report is None:
            execute(study, args.stage)
            report = {"stage": args.stage}
        if blocked:
            raise RuntimeError("Unexpected networking; stop")
        print(json.dumps({**report, "in_process_network_attempts": len(blocked)}))


if __name__ == "__main__":
    main()
