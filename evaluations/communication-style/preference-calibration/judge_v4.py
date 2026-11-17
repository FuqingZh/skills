#!/usr/bin/env python3
"""Run a bounded v4 calibration while reusing the frozen v3 data and aggregator.

Only the judge and output validator change. The original runner, labels, admission
and jobs remain byte-identical. The aggregator runs in its own loaded namespace;
its three injected dependencies select v4 verification, validation and outputs.
No history files are edited and no holdout execution is exposed.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import runpy
import subprocess
import tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any, cast

ROOT = Path(__file__).resolve().parent
BASE = runpy.run_path(str(ROOT / "judge_v3.py"))
CORE = BASE["CORE"]
V3_VERIFY = BASE["verify"]
V3_VALIDATE = BASE["validate"]
OUTPUT = ROOT / "results-v4"
FILES = (
    *BASE["FILES"],
    "manifest-v3.json",
    "judge_v4.py",
    "judge-v4.txt",
    "protocol-v4.json",
)
FIELDS = {
    "choice",
    "reason",
    "issues",
    "shared_issues",
    "strengths",
    "content_issues",
    "self_defense",
}


def hashes() -> dict[str, str]:
    return {
        name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() for name in FILES
    }


def verify() -> dict[str, Any]:
    V3_VERIFY()
    if BASE["read_json"]("manifest-v4.json") != {"sha256": hashes()}:
        raise ValueError("Frozen v4 source mismatch")
    protocol = BASE["read_json"]("protocol-v4.json")
    if protocol["version"] != 4 or protocol["max_calls"] != len(BASE["jobs"]()):
        raise ValueError("Unexpected v4 protocol")
    if protocol["phase"] != "calibration_only" or protocol["attempts_per_job"] != 1:
        raise ValueError("Unsupported v4 execution")
    return protocol


def validate(value: Any, payload: dict[str, Any]) -> dict[str, str]:
    BASE["require_object"](value, FIELDS | {"checks", "deletion_audit"})
    quotes: dict[str, str] = V3_VALIDATE({k: value[k] for k in FIELDS}, payload)
    BASE["require_object"](value["checks"], {"A", "B"})
    BASE["require_object"](value["deletion_audit"], {"A", "B"})
    for side in ("A", "B"):
        checks = value["checks"][side]
        BASE["require_object"](checks, BASE["DIMENSIONS"])
        dimensions = {item["dimension"] for item in value["issues"][side]}
        for dimension, check in checks.items():
            BASE["require_object"](check, {"status", "reason", "evidence"})
            status = check["status"]
            if status not in ("issue", "clear", "uncertain", "not_applicable"):
                raise ValueError("Unknown check status")
            BASE["require_text"](check["reason"])
            quotes.update(
                BASE["evidence"](
                    check["evidence"], payload, {side}, required=status == "issue"
                )
            )
            if (status == "issue") != (dimension in dimensions):
                raise ValueError("Checks and issues disagree")
        status = checks["self_defense"]["status"]
        expected = {"issue": "present", "uncertain": "uncertain"}.get(status, "absent")
        if value["self_defense"][side]["status"] != expected:
            raise ValueError("Self-defense fields disagree")
        audits = value["deletion_audit"][side]
        if not isinstance(audits, list):
            raise ValueError("Expected deletion audit list")
        for audit in cast(list[Any], audits):
            BASE["require_object"](
                audit,
                {
                    "evidence",
                    "target",
                    "already_known",
                    "increment",
                    "lost_if_deleted",
                    "verdict",
                },
            )
            if audit["verdict"] not in ("keep", "remove", "uncertain"):
                raise ValueError("Unknown deletion verdict")
            for key in ("target", "already_known", "increment", "lost_if_deleted"):
                BASE["require_text"](audit[key])
            quotes.update(BASE["evidence"](audit["evidence"], payload, {side}))
    for shared in value["shared_issues"]:
        for side in ("A", "B"):
            refs = {r for r in shared["evidence"] if r.startswith(side)}
            if not any(
                refs & set(issue["evidence"]) for issue in value["issues"][side]
            ):
                raise ValueError("Shared issue absent from per-answer issues")
    return quotes


def execute() -> None:
    protocol = verify()
    jobs = BASE["jobs"]()
    OUTPUT.mkdir(exist_ok=False)
    CORE["save_new"](
        OUTPUT / "run.json",
        {
            "protocol": protocol,
            "manifest": BASE["read_json"]("manifest-v4.json"),
            "jobs": [{"id": j["id"], "order": j["order"]} for j in jobs],
            "pi_version": subprocess.check_output(
                ["pi", "--version"], text=True
            ).strip(),
            "isolation": CORE["ISOLATION"],
        },
    )
    system = (ROOT / "judge-v4.txt").read_text(encoding="utf-8")
    with tempfile.TemporaryDirectory(prefix="preference-v4-empty-") as cwd:

        def one(job: dict[str, Any]) -> None:
            try:
                result = CORE["invoke"](
                    system,
                    json.dumps(job["payload"], ensure_ascii=False),
                    protocol["judge"],
                    cwd,
                    protocol["timeout_seconds"],
                )
            except (OSError, ValueError, TypeError) as exc:
                result = {"error": f"Invocation failure: {type(exc).__name__}"}
            record = {**job, **result}
            if "error" not in record:
                try:
                    parsed = json.loads(record["answer"])
                    record["evidence_text"] = validate(parsed, job["payload"])
                    record["judgment"] = parsed
                except (ValueError, KeyError, TypeError) as exc:
                    record["error"] = f"Invalid judgment: {exc}"
            CORE["save_new"](OUTPUT / f"{job['id']}-{job['order']}.json", record)
            print(job["id"], job["order"], record.get("error", "ok"), flush=True)

        with ThreadPoolExecutor(max_workers=protocol["workers"]) as pool:
            list(pool.map(one, jobs))


def summarize() -> dict[str, Any]:
    namespace = BASE["summarize"].__globals__
    before = {key: namespace[key] for key in ("verify", "validate", "OUTPUT")}
    namespace.update(verify=verify, validate=validate, OUTPUT=OUTPUT)
    try:
        result = BASE["summarize"]()
    finally:
        namespace.update(before)
    result["version"] = 4
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("run", "summarize"))
    args = parser.parse_args()
    if args.mode == "run":
        execute()
    else:
        print(json.dumps(summarize(), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
