#!/usr/bin/env python3
"""Frozen sentence-deletion study; reuse isolated transport and evidence checks."""

from __future__ import annotations

import argparse
import json
import random
import runpy
import statistics
import tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any, TypeGuard

ROOT = Path(__file__).resolve().parent
PARENT = ROOT.parent
DIMENSIONS = (
    "plain_depth",
    "focus_coherence",
    "substantive_distinctions",
    "local_qualification",
    "progression",
    "no_self_defense",
    "requested_meta",
)


def engine() -> dict[str, Any]:
    core = runpy.run_path(str(PARENT / "run.py"))
    core["verify_sources"]()
    core["generate"].__globals__["ROOT"] = ROOT
    return core


def tracked(core: dict[str, Any]) -> list[str]:
    return [
        "benchmark.py",
        "protocol.json",
        "cases.json",
        "controls.json",
        "sentences.json",
        "judge.txt",
        "../run.py",
        "../execution-manifest.json",
        "../cross-domain/prompts/revised.txt",
        *[
            f"prompts/{arm}.txt"
            for arm in core["read_json"](ROOT / "protocol.json")["arms"]
        ],
    ]


def verify(core: dict[str, Any]) -> None:
    manifest = core["read_json"](ROOT / "execution-manifest.json")["sha256"]
    if set(manifest) != set(tracked(core)):
        raise ValueError("Incomplete manifest")
    for name, expected in manifest.items():
        if core["digest"](ROOT / name) != expected:
            raise ValueError(f"Frozen source changed: {name}")


def is_record(value: object) -> TypeGuard[dict[object, object]]:
    """Narrow untrusted JSON dictionaries before validating their fields."""
    return isinstance(value, dict)


def validate(
    core: dict[str, Any],
    case: dict[str, Any],
    answers: list[dict[str, str]],
    record: dict[str, Any],
) -> None:
    core["validate_ratings"](record, answers, len(case["required"]))
    texts = {a["id"]: a["answer"] for a in answers}
    for rating in record["ratings"]:
        quality = rating["quality"]
        if not is_record(quality) or set(quality) != set(case["dimensions"]):
            raise ValueError("Incomplete quality dimensions")
        for item in quality.values():
            if not is_record(item):
                raise ValueError("Invalid quality item")
            score, quote, reason = (
                item.get("score"),
                item.get("quote"),
                item.get("reason"),
            )
            if (
                type(score) is not int
                or score not in range(5)
                or not isinstance(quote, str)
                or not isinstance(reason, str)
                or not reason.strip()
                or (score < 4 and not quote.strip())
                or (quote and quote not in texts[rating["id"]])
            ):
                raise ValueError("Invalid quality evidence")


def judge_one(
    core: dict[str, Any],
    case: dict[str, Any],
    answers: list[dict[str, str]],
    cwd: str,
) -> dict[str, Any]:
    protocol = core["read_json"](ROOT / "protocol.json")
    packet = {
        "task": case["prompt"],
        "required": case["required"],
        "critical_examples": case["critical"],
        "dimensions": case["dimensions"],
        "answers": answers,
    }
    result = core["invoke"](
        (ROOT / "judge.txt").read_text(),
        json.dumps(packet, ensure_ascii=False),
        protocol["judge"],
        cwd,
        protocol["timeout_seconds"],
    )
    if "error" not in result:
        try:
            parsed = json.loads(result["answer"])
            validate(core, case, answers, parsed)
            result["ratings"] = parsed["ratings"]
        except (ValueError, KeyError, TypeError) as exc:
            result["error"] = f"Invalid judgment: {exc}"
    return result


def check_controls(core: dict[str, Any]) -> None:
    for case in core["read_json"](ROOT / "controls.json"):
        record = core["read_json"](ROOT / "results/controls" / f"{case['id']}.json")
        if "error" in record or record["source_manifest"] != core["read_json"](
            ROOT / "execution-manifest.json"
        ):
            raise ValueError(f"Invalid control: {case['id']}")
        validate(core, case, case["answers"], record)
        ratings = {r["id"]: r for r in record["ratings"]}
        for expected in case["expectations"]:
            score = ratings[expected["id"]]["quality"][expected["dimension"]]["score"]
            if not expected["min"] <= score <= expected["max"]:
                raise ValueError(f"Control expectation failed: {case['id']} {expected}")
        for key in case.get("critical_required", []):
            if not ratings[key]["critical"]:
                raise ValueError("Control missed critical error")
        for key in case.get("clean_required", []):
            rating = ratings[key]
            if (
                rating["critical"]
                or rating["style"]
                or not all(c["met"] for c in rating["content"])
            ):
                raise ValueError("Control rejected necessary correction/clarification")


def calibrate(core: dict[str, Any]) -> None:
    cases = core["read_json"](ROOT / "controls.json")
    output = ROOT / "results/controls"
    if any(output.glob("*.json")):
        raise FileExistsError("Control attempts already exist")
    with tempfile.TemporaryDirectory(prefix="ablation-control-") as cwd:
        for case in cases:
            result = judge_one(core, case, case["answers"], cwd)
            core["save_new"](
                output / f"{case['id']}.json",
                {
                    "case": case["id"],
                    "source_manifest": core["read_json"](
                        ROOT / "execution-manifest.json"
                    ),
                    **result,
                },
            )
            print("control", case["id"], result.get("error", "valid"), flush=True)
    check_controls(core)


def packets(core: dict[str, Any]) -> list[dict[str, Any]]:
    protocol = core["read_json"](ROOT / "protocol.json")
    metadata = core["read_json"](ROOT / "results/benchmark/run.json")
    if metadata["source_manifest"] != core["read_json"](
        ROOT / "execution-manifest.json"
    ):
        raise ValueError("Generation manifest mismatch")
    if metadata["arms"] != protocol["arms"] or metadata["jobs"] != 160:
        raise ValueError("Generation arms/count mismatch")
    result: list[dict[str, Any]] = []
    for case in core["read_json"](ROOT / "cases.json"):
        for rep in range(1, protocol["repetitions"] + 1):
            rows: list[tuple[str, str]] = []
            for arm in protocol["arms"]:
                key = f"{case['id']}-{arm}-{rep}"
                record = core["read_json"](ROOT / "results/benchmark" / f"{key}.json")
                if "error" in record or (
                    record["case"],
                    record["arm"],
                    record["rep"],
                    record["model"],
                    record["provider"],
                ) != (case["id"], arm, rep, protocol["generator"]["model"], "openai"):
                    raise ValueError(f"Invalid generation: {key}")
                rows.append((key, record["answer"]))
            random.Random(f"{protocol['order_seed']}:{case['id']}:{rep}").shuffle(rows)
            result.append(
                {
                    "case": case,
                    "rep": rep,
                    "mapping": {f"R{i + 1}": row[0] for i, row in enumerate(rows)},
                    "answers": [
                        {"id": f"R{i + 1}", "answer": row[1]}
                        for i, row in enumerate(rows)
                    ],
                }
            )
    return result


def judge(core: dict[str, Any]) -> None:
    jobs = packets(core)
    output = ROOT / "results/judgments"
    if any(output.glob("*.json")):
        raise FileExistsError("Judgment attempts already exist")
    with tempfile.TemporaryDirectory(prefix="ablation-judge-") as cwd:

        def one(job: dict[str, Any]) -> None:
            result = judge_one(core, job["case"], job["answers"], cwd)
            key = f"{job['case']['id']}-{job['rep']}"
            core["save_new"](
                output / f"{key}.json",
                {
                    "case": job["case"]["id"],
                    "rep": job["rep"],
                    "mapping": job["mapping"],
                    **result,
                },
            )
            print("judge", key, result.get("error", "ok"), flush=True)

        with ThreadPoolExecutor(max_workers=3) as pool:
            list(pool.map(one, jobs))


def interval(values: list[float]) -> list[float]:
    rng = random.Random(71)
    samples = sorted(
        statistics.mean(rng.choices(values, k=len(values))) for _ in range(20000)
    )
    return [round(samples[499], 4), round(samples[19499], 4)]


def summarize(core: dict[str, Any]) -> dict[str, Any]:
    scores: dict[str, dict[str, Any]] = {}
    judge_cost = 0.0
    flagged: list[str] = []
    for job in packets(core):
        key = f"{job['case']['id']}-{job['rep']}"
        record = core["read_json"](ROOT / "results/judgments" / f"{key}.json")
        if "error" in record or record["mapping"] != job["mapping"]:
            raise ValueError(f"Invalid judgment: {key}")
        validate(core, job["case"], job["answers"], record)
        if json.loads(record["answer"])["ratings"] != record["ratings"]:
            raise ValueError("Stored scores differ from raw judgment")
        judge_cost += record["usage"]["cost"]["total"]
        for rating in record["ratings"]:
            answer_id = record["mapping"][rating["id"]]
            quality = {d: item["score"] for d, item in rating["quality"].items()}
            scores[answer_id] = {
                "overall": 25 * statistics.mean(quality.values()),
                "dimensions": {d: 25 * score for d, score in quality.items()},
                "missing": sum(not c["met"] for c in rating["content"]),
                "critical": len(rating["critical"]),
                "style": len(rating["style"]),
            }
            if (
                rating["critical"]
                or rating["style"]
                or any(v < 4 for v in quality.values())
                or any(not c["met"] for c in rating["content"])
            ):
                flagged.append(answer_id)
    protocol = core["read_json"](ROOT / "protocol.json")
    cases = core["read_json"](ROOT / "cases.json")
    arms: dict[str, dict[str, Any]] = {}
    for arm in protocol["arms"]:
        keys = [f"{c['id']}-{arm}-{rep}" for c in cases for rep in (1, 2)]
        rows = [
            core["read_json"](ROOT / "results/benchmark" / f"{k}.json") for k in keys
        ]
        arms[arm] = {
            "score": statistics.mean(scores[k]["overall"] for k in keys),
            "missing": sum(scores[k]["missing"] for k in keys),
            "critical": sum(scores[k]["critical"] for k in keys),
            "style": sum(scores[k]["style"] for k in keys),
            "characters": sum(r["characters"] for r in rows),
            "cost": sum(r["usage"]["cost"]["total"] for r in rows),
        }

    def contrast(
        coefficients: dict[str, int], dimension: str | None = None
    ) -> dict[str, Any]:
        deltas: dict[str, float] = {}
        for case in cases:
            if dimension and dimension not in case["dimensions"]:
                continue

            def value(arm: str, rep: int, case_id: str = case["id"]) -> float:
                row = scores[f"{case_id}-{arm}-{rep}"]
                return row["dimensions"][dimension] if dimension else row["overall"]

            deltas[case["id"]] = statistics.mean(
                sum(weight * value(arm, rep) for arm, weight in coefficients.items())
                for rep in (1, 2)
            )
        return {
            "mean": statistics.mean(deltas.values()),
            "task_deltas": deltas,
            "cluster_bootstrap_95_unadjusted": interval(list(deltas.values())),
        }

    effects = {
        f"S{i}": {
            "overall": contrast({"full": 1, f"drop{i}": -1}),
            "target_dimension": DIMENSIONS[i - 1],
            "target": contrast({"full": 1, f"drop{i}": -1}, DIMENSIONS[i - 1]),
        }
        for i in range(1, 8)
    }
    return {
        "arms": arms,
        "effects": effects,
        "paragraph_net": contrast({"full": 1, "minimal": -1}),
        "interaction67": contrast({"full": 1, "drop6": -1, "drop7": -1, "drop67": 1}),
        "flagged": sorted(flagged),
        "scores": scores,
        "judge_cost": judge_cost,
        "control_cost": sum(
            core["read_json"](ROOT / "results/controls" / f"{c['id']}.json")["usage"][
                "cost"
            ]["total"]
            for c in core["read_json"](ROOT / "controls.json")
        ),
    }


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
            {
                "sha256": {name: core["digest"](ROOT / name) for name in tracked(core)},
            },
        )
        return
    verify(core)
    if args.mode == "calibrate":
        calibrate(core)
        return
    check_controls(core)
    if args.mode == "generate":
        core["generate"](
            "benchmark",
            core["read_json"](ROOT / "protocol.json")["arms"],
            ROOT / "results/benchmark",
        )
    elif args.mode == "judge":
        judge(core)
    else:
        print(json.dumps(summarize(core), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
