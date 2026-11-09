#!/usr/bin/env python3
"""Summarize complete raw model judgments without applying author overrides.

Run with development or holdout as the argument. Output is JSON on stdout;
missing attempts, incomplete judging, or duplicate ratings stop the calculation.
Character-normalized style frequency is descriptive, not a quality ranking.
"""

from __future__ import annotations

import json
import statistics
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent


def load(path: Path) -> Any:
    """Name a missing or malformed artifact instead of producing a partial table."""
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise ValueError(f"Invalid or missing artifact: {path}") from exc


def metrics(rows: list[dict[str, Any]]) -> dict[str, Any]:
    content = [c for row in rows for c in row["rating"]["content"]]
    style = [s for row in rows for s in row["rating"]["style"]]
    chars = sum(row["characters"] for row in rows)
    return {
        "responses": len(rows),
        "requirements": len(content),
        "missing_requirements": sum(not c["met"] for c in content),
        "responses_with_omissions": sum(
            any(not c["met"] for c in row["rating"]["content"]) for row in rows
        ),
        "critical_findings": sum(len(row["rating"]["critical"]) for row in rows),
        "responses_with_style_issues": sum(
            bool(row["rating"]["style"]) for row in rows
        ),
        "style_findings": len(style),
        "style_by_kind": dict(Counter(s["kind"] for s in style)),
        "style_by_region": dict(Counter(s["region"] for s in style)),
        "style_per_1000_characters": round(len(style) * 1000 / chars, 4),
        "clarity": dict(Counter(row["rating"]["clarity"] for row in rows)),
        "characters": chars,
        "median_characters": statistics.median(row["characters"] for row in rows),
        "mean_seconds": round(statistics.mean(row["seconds"] for row in rows), 3),
        "usage": {
            key: sum(row["usage"].get(key, 0) for row in rows)
            for key in ("input", "output", "cacheRead", "reasoning", "totalTokens")
        },
        "estimated_cost_usd": round(
            sum(row["usage"]["cost"]["total"] for row in rows), 6
        ),
    }


def summarize(split: str) -> dict[str, Any]:
    responses = ROOT / "results" / split
    judgments = ROOT / "results" / f"{split}-judgments"
    cases = load(ROOT / "cases.json")
    protocol = load(ROOT / "protocol.json")
    run = load(responses / "run.json")
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    flagged: list[dict[str, Any]] = []
    judge_cost = 0.0
    for case in (c for c in cases if c["split"] == split):
        judge = load(judgments / f"{case['id']}.json")
        if "error" in judge:
            raise ValueError(f"Failed judge: {case['id']}")
        expected = {
            f"{case['id']}-{arm}-{rep}"
            for arm in run["arms"]
            for rep in range(1, protocol["repetitions"] + 1)
        }
        actual = [judge["mapping"][r["id"]] for r in judge["ratings"]]
        if set(actual) != expected or len(actual) != len(expected):
            raise ValueError(f"Incomplete/duplicate ratings: {case['id']}")
        judge_cost += judge["usage"]["cost"]["total"]
        for rating in judge["ratings"]:
            key = judge["mapping"][rating["id"]]
            row = load(responses / f"{key}.json")
            if "error" in row:
                raise ValueError(f"Failed generation: {key}")
            row["rating"] = rating
            groups[f"{row['arm']}/{row['length']}"].append(row)
            groups[f"{row['arm']}/all"].append(row)
            omissions = [c for c in rating["content"] if not c["met"]]
            if omissions or rating["critical"] or rating["style"]:
                flagged.append(
                    {
                        "response": key,
                        "omissions": omissions,
                        "critical": rating["critical"],
                        "style": rating["style"],
                    }
                )
    return {
        "split": split,
        "metrics": {key: metrics(rows) for key, rows in sorted(groups.items())},
        "flagged": flagged,
        "estimated_judge_cost_usd": round(judge_cost, 6),
        "status": "raw model judgments; see separate author audit",
    }


if __name__ == "__main__":
    if len(sys.argv) != 2 or sys.argv[1] not in {"development", "holdout"}:
        sys.exit("usage: summarize.py development|holdout")
    print(json.dumps(summarize(sys.argv[1]), ensure_ascii=False, indent=2))
