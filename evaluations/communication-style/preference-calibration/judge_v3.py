#!/usr/bin/env python3
"""Run one frozen calibration batch; summarize offline without repairing records.

Human labels never enter judge requests. Results use exclusive writes and retain
invalid visible answers. Holdout execution is deliberately unavailable until the
calibration review chooses a final judge. Earlier packet versions stay unchanged.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import random
import runpy
import subprocess
import tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any, cast

ROOT = Path(__file__).resolve().parent
PACKET = runpy.run_path(str(ROOT / "packet.py"))
CORE = runpy.run_path(str(ROOT.parent / "run.py"))
OUTPUT = ROOT / "results-v3"
DIMENSIONS = {"response", "grounding", "progression", "naturalness", "self_defense"}
FILES = (
    "judge_v3.py",
    "packet.py",
    "pairs.json",
    "instructions.md",
    "admission-v3.json",
    "rubric-v3.md",
    "judge-v3.txt",
    "protocol-v3.json",
    "labels.round-1.json",
    "../run.py",
)


def read_json(name: str) -> Any:
    return json.loads((ROOT / name).read_text(encoding="utf-8"))


def hashes() -> dict[str, str]:
    return {
        name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() for name in FILES
    }


def verify() -> dict[str, Any]:
    manifest = read_json("manifest-v3.json")
    if manifest != {"sha256": hashes()}:
        raise ValueError("Frozen source mismatch")
    protocol = read_json("protocol-v3.json")
    if (
        protocol["phase"] != "calibration_only"
        or protocol["attempts_per_job"] != 1
        or protocol["orders"] != ["original", "swapped"]
        or protocol["max_calls"] != 24
    ):
        raise ValueError("Unsupported protocol")
    PACKET["_validate"]("calibration", read_json(protocol["human_labels"]))
    return protocol


def materials() -> dict[str, dict[str, Any]]:
    pairs = PACKET["_load"]()
    by_context = {pair["context"]: pair for pair in pairs}
    if len(by_context) != len(pairs):
        raise ValueError("Ambiguous source context")
    rows = read_json("admission-v3.json")["pairs"]
    admission = {row["id"]: row for row in rows}
    if len(rows) != len(admission) or set(admission) != {p["id"] for p in pairs}:
        raise ValueError("Incomplete or duplicate admission")
    for row in rows:
        if row["category"] not in {"style", "mixed", "correctness"}:
            raise ValueError("Unknown admission category")
        if not isinstance(row["reason"], str) or not row["reason"].strip():
            raise ValueError("Missing admission reason")
    result: dict[str, dict[str, Any]] = {}
    for split in ("calibration", "holdout"):
        for item in PACKET["_items"](split):
            source = by_context[item["context"]]
            result[item["id"]] = {
                "item": item,
                "source": source["id"],
                "family": source["family"],
                "category": admission[source["id"]]["category"],
                "split": split,
            }
    return result


def swapped(item: dict[str, Any]) -> dict[str, Any]:
    result = copy.deepcopy(item)
    result["answers"] = {
        side: {
            f"{side}{i}": text
            for i, text in enumerate(item["answers"][other].values(), 1)
        }
        for side, other in (("A", "B"), ("B", "A"))
    }
    return result


def jobs() -> list[dict[str, Any]]:
    selected = [
        row["item"]
        for row in materials().values()
        if row["split"] == "calibration" and row["category"] != "correctness"
    ]
    control = {
        "id": "I01",
        "context": "用户问: 明天什么时候见面?",
        "answers": {"A": {"A1": "明天下午三点见。"}, "B": {"B1": "明天下午三点见。"}},
    }
    result: list[dict[str, Any]] = []
    for item in [*selected, control]:
        for order in ("original", "swapped"):
            shown = item if order == "original" else swapped(item)
            result.append(
                {
                    "id": item["id"],
                    "order": order,
                    "payload": {
                        "context": shown["context"],
                        "answers": shown["answers"],
                    },
                }
            )
    if len(result) != 24:
        raise ValueError("Unexpected call count")
    random.Random(73).shuffle(result)
    return result


def require_object(value: Any, fields: set[str]) -> None:
    if not isinstance(value, dict) or set(cast(dict[str, Any], value)) != fields:
        raise ValueError("Unexpected object fields")


def require_text(value: Any) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError("Empty judgment text")


def evidence(
    refs: Any, payload: dict[str, Any], sides: set[str], *, required: bool = True
) -> dict[str, str]:
    if not isinstance(refs, list) or (required and not refs):
        raise ValueError("Missing evidence")
    resolved = PACKET["_evidence"](payload, refs)
    if any(ref[0] not in sides for ref in resolved):
        raise ValueError("Cross-answer evidence")
    if len(sides) == 2 and {ref[0] for ref in resolved} != sides:
        raise ValueError("Shared issue needs both answers")
    return resolved


def validate(value: Any, payload: dict[str, Any]) -> dict[str, str]:
    require_object(
        value,
        {
            "choice",
            "reason",
            "issues",
            "shared_issues",
            "strengths",
            "content_issues",
            "self_defense",
        },
    )
    if value["choice"] not in ("A", "B", "tie", "uncertain"):
        raise ValueError("Unknown choice")
    require_text(value["reason"])
    extracted: dict[str, str] = {}
    for field in ("issues", "strengths", "content_issues"):
        require_object(value[field], {"A", "B"})
        for side in ("A", "B"):
            findings = value[field][side]
            if not isinstance(findings, list):
                raise ValueError("Expected findings list")
            for finding in cast(list[Any], findings):
                keys = {"reason", "evidence"}
                if field == "issues":
                    keys.add("dimension")
                require_object(finding, keys)
                if field == "issues" and finding["dimension"] not in DIMENSIONS:
                    raise ValueError("Unknown dimension")
                require_text(finding["reason"])
                extracted.update(evidence(finding["evidence"], payload, {side}))
    if not isinstance(value["shared_issues"], list):
        raise ValueError("Expected shared issues list")
    for finding in value["shared_issues"]:
        require_object(finding, {"reason", "evidence"})
        require_text(finding["reason"])
        extracted.update(evidence(finding["evidence"], payload, {"A", "B"}))
    require_object(value["self_defense"], {"A", "B"})
    for side, finding in value["self_defense"].items():
        require_object(
            finding,
            {
                "status",
                "target",
                "increment",
                "deletion",
                "evidence",
            },
        )
        if finding["status"] not in ("present", "absent", "uncertain"):
            raise ValueError("Unknown self-defense status")
        for field in ("target", "increment", "deletion"):
            require_text(finding[field])
        extracted.update(
            evidence(
                finding["evidence"],
                payload,
                {side},
                required=finding["status"] == "present",
            )
        )
    return extracted


def normalize(choice: str, order: str) -> str:
    if order == "swapped" and choice in ("A", "B"):
        return "B" if choice == "A" else "A"
    return choice


def execute() -> None:
    protocol = verify()
    batch = jobs()
    OUTPUT.mkdir(exist_ok=False)
    CORE["save_new"](
        OUTPUT / "run.json",
        {
            "protocol": protocol,
            "manifest": read_json("manifest-v3.json"),
            "jobs": [{"id": job["id"], "order": job["order"]} for job in batch],
            "pi_version": subprocess.check_output(
                ["pi", "--version"], text=True
            ).strip(),
            "isolation": CORE["ISOLATION"],
        },
    )
    system = (ROOT / "judge-v3.txt").read_text(encoding="utf-8")
    with tempfile.TemporaryDirectory(prefix="preference-empty-") as cwd:

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
            list(pool.map(one, batch))


def summarize() -> dict[str, Any]:
    verify()
    labels = {row["id"]: row for row in read_json("labels.round-1.json")["ratings"]}
    meta = materials()
    collected: dict[str, dict[str, Any]] = {}
    usage: list[dict[str, Any]] = []
    for job in jobs():
        key, order = job["id"], job["order"]
        path = OUTPUT / f"{key}-{order}.json"
        row: dict[str, Any] = {"state": "missing"}
        if path.exists():
            record = json.loads(path.read_text())
            if any(record.get(k) != job[k] for k in ("id", "order", "payload")):
                raise ValueError("Record input mismatch")
            usage.append(record.get("usage", {}))
            row = {"state": "invalid", "error": record.get("error")}
            if "error" not in record:
                parsed = json.loads(record["answer"])
                quotes = validate(parsed, job["payload"])
                if parsed != record["judgment"] or quotes != record["evidence_text"]:
                    raise ValueError("Record derived evidence mismatch")
                row = {
                    "state": "valid",
                    "choice": normalize(parsed["choice"], order),
                    "reason": parsed["reason"],
                }
        collected.setdefault(key, {})[order] = row
    rows: list[dict[str, Any]] = []
    counts = {
        "eligible": 0,
        "agree": 0,
        "disagree": 0,
        "conflict": 0,
        "unavailable": 0,
        "uncertain": 0,
    }
    families: dict[str, dict[str, int]] = {}
    for key, orders in sorted(collected.items()):
        group = meta.get(key, {"category": "identity", "family": "identity"})
        human = labels.get(key, {}).get("choice")
        valid = all(row["state"] == "valid" for row in orders.values())
        choices = [row.get("choice") for row in orders.values()]
        consistent = valid and choices[0] == choices[1]
        status = "unavailable"
        if valid:
            status = "consistent" if consistent else "conflict"
        prediction = choices[0] if consistent else None
        eligible = group["category"] == "style" and human is not None
        agreement = None
        if eligible:
            counts["eligible"] += 1
            family = families.setdefault(group["family"], {"eligible": 0, "agree": 0})
            family["eligible"] += 1
            if not valid:
                counts["unavailable"] += 1
            elif not consistent:
                counts["conflict"] += 1
            elif prediction == "uncertain" and human != "uncertain":
                counts["uncertain"] += 1
            else:
                agreement = prediction == human
                counts["agree" if agreement else "disagree"] += 1
                family["agree"] += int(agreement)
        rows.append(
            {
                "id": key,
                "category": group["category"],
                "family": group["family"],
                "human": human,
                "status": status,
                "prediction": prediction,
                "primary_agreement": agreement,
                "orders": orders,
            }
        )
    return {
        "phase": "calibration_only",
        "primary": counts,
        "families": families,
        "attempts_present": len(usage),
        "expected_attempts": 24,
        "estimated_cost": sum(u.get("cost", {}).get("total", 0) for u in usage),
        "total_tokens": sum(u.get("totalTokens", 0) for u in usage),
        "rows": rows,
        "promotion": "requires qualitative review; no automatic threshold",
    }


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
