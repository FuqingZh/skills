"""Run two already human-labeled D cases with the unchanged OpenEvals judge.

The original packet fixes context, paragraph text and A/B order. Only those
fields reach evaluate; feedback and selection reasons are audit-only. Exclusive
case reservations prohibit retries, including after a partially completed case.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import runpy
import socket
from pathlib import Path
from typing import Any
from unittest.mock import patch

ROOT = Path(__file__).resolve().parent
CHECKER = runpy.run_path(str(ROOT.parent / "openevals-pilot-2/run.py"))
BASE = CHECKER["BASE"]
DIAGNOSTICS = runpy.run_path(
    str(ROOT.parent / "openevals-pilot-2/diagnostic_transport.py")
)
FILES = (
    "run.py",
    "protocol.json",
    "cases.json",
    "../packet.py",
    "../pairs.json",
    "../instructions.md",
    "../labels.round-1.json",
    "../feedback.round-1.json",
    "../openevals-pilot-2/manifest.json",
    "../openevals-pilot-2/transport-repair.json",
    "../openevals-pilot-2/diagnostic_transport.py",
    "../openevals-pilot-2-recovery-1/feedback-1.json",
)


def hashes() -> dict[str, str]:
    return {
        name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() for name in FILES
    }


def verify() -> None:
    CHECKER["verify"]()
    if hashes() != BASE["load"](ROOT / "manifest.json"):
        raise ValueError("Third-pilot freeze changed")
    packet = runpy.run_path(str(ROOT.parent / "packet.py"))
    cases = BASE["load"](ROOT / "cases.json")
    labels = BASE["load"](ROOT.parent / "labels.round-1.json")
    digest = packet["_materials"]("calibration")["form"]["packet_sha256"]
    if digest != cases["source_packet_sha256"] or digest != labels["packet_sha256"]:
        raise ValueError("Human packet identity changed")
    order = BASE["load"](ROOT / "protocol.json")["cases"]
    expected = [
        {
            "id": row["id"],
            "context": row["context"],
            "answers": {
                side: "\n\n".join(paragraphs.values())
                for side, paragraphs in row["answers"].items()
            },
        }
        for row in packet["_items"]("calibration")
        if row["id"] in order
    ]
    if cases["cases"] != expected or [row["id"] for row in expected] != order:
        raise ValueError("Selected answers differ from the human packet")


def execute(case_id: str) -> None:
    order = BASE["load"](ROOT / "protocol.json")["cases"]
    index = order.index(case_id)
    if index:
        review = BASE["load"](ROOT / f"review-{order[index - 1]}.json")
        if review["decision"] != "continue":
            raise ValueError("Previous case not approved")
    output = ROOT / "results" / case_id
    output.mkdir(parents=True, exist_ok=False)
    case = next(
        row
        for row in BASE["load"](ROOT / "cases.json")["cases"]
        if row["id"] == case_id
    )
    for side in ("A", "B"):
        BASE["save"](
            output / f"{side}.started.json",
            {"case": case_id, "side": side, "attempt": 1},
        )
        record = BASE["evaluate"](case["context"], case["answers"][side], BASE["live"])
        BASE["save"](output / f"{side}.json", record)
        if "error" in record:
            raise RuntimeError("Failed output retained; stop without retry")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("check", "D02", "D05"))
    args = parser.parse_args()
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
        verify()
        if args.mode != "check":
            execute(args.mode)
        if blocked:
            raise RuntimeError("Unexpected networking; stop")
    print(json.dumps({"mode": args.mode, "in_process_network_attempts": len(blocked)}))


if __name__ == "__main__":
    main()
