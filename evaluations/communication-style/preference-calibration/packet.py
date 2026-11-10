#!/usr/bin/env python3
"""Prepare human preference packets without model calls or inferred labels.

The CLI emits JSON to stdout; it never writes over an annotation file. Paragraph
IDs address the exact text shown in a packet, including Markdown. A packet hash
binds labels to both the instructions and the displayed answer order.

Examples:
    python packet.py render calibration
    python packet.py validate calibration /path/to/completed-labels.json
"""

from __future__ import annotations

import argparse
import hashlib
import json
import random
from pathlib import Path
from typing import Any, TypeGuard, cast

ROOT = Path(__file__).resolve().parent
SPLITS = ("calibration", "holdout")
SEED = 42
CHOICES = ("A", "B", "tie", "uncertain")
CONTENT = ("A", "B", "both", "none", "uncertain")
INSTRUCTIONS = (ROOT / "instructions.md").read_text(encoding="utf-8")


def _is_list(value: object) -> TypeGuard[list[Any]]:
    return isinstance(value, list)


def _is_record(value: object) -> TypeGuard[dict[str, Any]]:
    return isinstance(value, dict) and all(
        isinstance(key, str) for key in cast(dict[object, object], value)
    )


def _load() -> list[dict[str, Any]]:
    pairs: list[dict[str, Any]] = json.loads((ROOT / "pairs.json").read_text())
    if len(pairs) != 24 or len({p["id"] for p in pairs}) != 24:
        raise ValueError("Expected 24 unique pairs")
    groups: dict[str, set[str]] = {s: set() for s in SPLITS}
    cases: dict[str, set[str]] = {s: set() for s in SPLITS}
    for pair in pairs:
        split = pair["split"]
        if split not in SPLITS:
            raise ValueError("Unknown split")
        groups[split].add(pair["family"])
        cases[split].add(pair["case_id"])
        if not isinstance(pair["context"], str) or not pair["context"].strip():
            raise ValueError("Missing context")
        candidates = pair["candidates"]
        if len(candidates) != 2 or candidates[0] == candidates[1]:
            raise ValueError("Expected two distinct candidates")
        for candidate in candidates:
            if not _is_list(candidate) or not candidate:
                raise ValueError("Expected nonempty paragraph list")
            if any(not isinstance(p, str) or not p.strip() for p in candidate):
                raise ValueError("Empty or invalid paragraph")
    if groups["calibration"] & groups["holdout"]:
        raise ValueError("Family leakage")
    if cases["calibration"] & cases["holdout"]:
        raise ValueError("Source-case leakage")
    for split in SPLITS:
        if sum(p["split"] == split for p in pairs) != 12:
            raise ValueError("Expected twelve pairs per split")
    return pairs


def _items(split: str, *, swap: bool = False) -> list[dict[str, Any]]:
    if split not in SPLITS:
        raise ValueError("Unknown split")
    selected = [p for p in _load() if p["split"] == split]
    rng = random.Random(SEED)
    rng.shuffle(selected)
    result: list[dict[str, Any]] = []
    prefix = "D" if split == "calibration" else "H"
    for index, pair in enumerate(selected, 1):
        order = [0, 1]
        rng.shuffle(order)
        if swap:
            order.reverse()
        result.append(
            {
                "id": f"{prefix}{index:02}",
                "context": pair["context"],
                "answers": {
                    side: {
                        f"{side}{i}": paragraph
                        for i, paragraph in enumerate(pair["candidates"][variant], 1)
                    }
                    for side, variant in zip(("A", "B"), order, strict=True)
                },
            }
        )
    return result


def _materials(split: str) -> dict[str, Any]:
    items = _items(split)
    title = "校准组" if split == "calibration" else "保留组"
    lines = [
        f"# 表达偏好: {title}",
        "",
        INSTRUCTIONS.replace("# ", "## ", 1).strip(),
        "",
    ]
    for item in items:
        lines.extend([f"## {item['id']}", "", item["context"], ""])
        for side, paragraphs in item["answers"].items():
            lines.extend([f"### {item['id']} / {side}", ""])
            for reference, paragraph in paragraphs.items():
                lines.extend([f"`{reference}`", "", paragraph, ""])
        lines.extend(["选择: ____ 理由/内容问题(可选): ____", ""])
    packet = "\n".join(lines)
    form: dict[str, Any] = {
        "split": split,
        "packet_sha256": hashlib.sha256(packet.encode()).hexdigest(),
        "ratings": [
            {
                "id": item["id"],
                "choice": None,
                "reason": "",
                "content_issue": None,
                "evidence": [],
            }
            for item in items
        ],
    }
    return {"packet": packet, "form": form}


def _evidence(item: dict[str, Any], references: list[Any]) -> dict[str, str]:
    paragraphs = {k: v for side in item["answers"].values() for k, v in side.items()}
    if any(not isinstance(r, str) or r not in paragraphs for r in references):
        raise ValueError("Unknown paragraph reference")
    if len(set(references)) != len(references):
        raise ValueError("Duplicate paragraph reference")
    return {r: paragraphs[r] for r in references}


def _validate(split: str, form: dict[str, Any]) -> dict[str, int]:
    expected = _materials(split)["form"]
    if set(form) != set(expected):
        raise ValueError("Unexpected form fields")
    if form["split"] != split or form["packet_sha256"] != expected["packet_sha256"]:
        raise ValueError("Packet identity mismatch")
    ratings = form["ratings"]
    if not _is_list(ratings) or len(ratings) != 12:
        raise ValueError("Expected twelve rating rows")
    items = {item["id"]: item for item in _items(split)}
    seen: set[str] = set()
    labeled = content_labeled = 0
    for rating in ratings:
        if not _is_record(rating) or set(rating) != set(expected["ratings"][0]):
            raise ValueError("Unexpected rating fields")
        key = rating["id"]
        if not isinstance(key, str) or key not in items or key in seen:
            raise ValueError("Unknown or duplicate pair ID")
        seen.add(key)
        if rating["choice"] is not None and rating["choice"] not in CHOICES:
            raise ValueError("Invalid preference label")
        if (
            rating["content_issue"] is not None
            and rating["content_issue"] not in CONTENT
        ):
            raise ValueError("Invalid content label")
        if not isinstance(rating["reason"], str) or not _is_list(rating["evidence"]):
            raise ValueError("Invalid reason or evidence")
        _evidence(items[key], rating["evidence"])
        labeled += rating["choice"] is not None
        content_labeled += rating["content_issue"] is not None
    return {"pairs": 12, "labeled": labeled, "content_labeled": content_labeled}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("render", "validate"))
    parser.add_argument("split", choices=SPLITS)
    parser.add_argument("labels", nargs="?", type=Path)
    args = parser.parse_args()
    if args.mode == "render":
        if args.labels is not None:
            parser.error("render accepts no labels path")
        result = _materials(args.split)
    else:
        if args.labels is None:
            parser.error("validate requires a labels path")
        form = json.loads(args.labels.read_text())
        if not _is_record(form):
            parser.error("labels must be an object")
        result = _validate(args.split, form)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
