#!/usr/bin/env python3
"""Run the frozen, response-only style comparison through fresh Pi processes.

No prompt discovery, extensions, tools, session persistence, or repository context
are enabled. Existing provider credentials are resolved by Pi without exporting
secrets. Only visible answers and usage metadata are retained, never thinking.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import random
import signal
import subprocess
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any, TypeGuard

ROOT = Path(__file__).resolve().parent
ARMS = ("baseline", "direct", "example")
STYLE = {
    "preamble",
    "self_defense",
    "redundancy",
    "invented_contrast",
    "forced_colloquialism",
    "decorative_metaphor",
}
ISOLATION = (
    "--print",
    "--mode",
    "json",
    "--no-session",
    "--no-tools",
    "--no-extensions",
    "--no-mcp",
    "--no-skills",
    "--no-prompt-templates",
    "--no-context-files",
    "--no-themes",
    "--no-approve",
    "--offline",
)


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def save_new(path: Path, value: Any) -> None:
    """Refuse overwrite so failures and earlier samples cannot disappear."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8") as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.write("\n")


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def source_paths() -> list[Path]:
    return [
        ROOT / "cases.json",
        ROOT / "protocol.json",
        ROOT / "judge.txt",
        ROOT / "run.py",
        *(ROOT / "prompts" / f"{arm}.txt" for arm in ARMS),
    ]


def verify_sources() -> None:
    manifest = read_json(ROOT / "execution-manifest.json")
    for path in source_paths():
        if digest(path) != manifest["sha256"][path.relative_to(ROOT).as_posix()]:
            raise ValueError(f"Frozen source changed: {path.name}")


def parse_events(stdout: str, model: str, provider: str) -> dict[str, Any]:
    """Keep only visible final text; reject partial, retried, or tool-using runs."""
    events = [json.loads(line) for line in stdout.split("\n") if line.strip()]
    messages = [
        e["message"]
        for e in events
        if e.get("type") == "message_end"
        and e.get("message", {}).get("role") == "assistant"
    ]
    if len(messages) != 1:
        raise ValueError("Expected exactly one assistant message")
    m = messages[0]
    if (m.get("model"), m.get("provider"), m.get("stopReason")) != (
        model,
        provider,
        "stop",
    ):
        raise ValueError("Model identity or completion status mismatch")
    if any(
        e.get("type", "").startswith(("tool_execution", "auto_retry", "compaction"))
        for e in events
    ):
        raise ValueError("Unexpected tools, retries, or compaction")
    if not any(
        e.get("type") == "agent_settled" and e.get("aborted") is False for e in events
    ):
        raise ValueError("Missing successful settled event")
    if any(b.get("type") == "toolCall" for b in m.get("content", [])):
        raise ValueError("Unexpected tool call")
    answer = "\n".join(b["text"] for b in m["content"] if b.get("type") == "text")
    if not answer.strip():
        raise ValueError("Empty visible answer")
    return {
        "answer": answer,
        "characters": len(answer),
        "model": model,
        "provider": provider,
        "usage": m.get("usage", {}),
    }


def invoke(
    system: str, prompt: str, config: dict[str, Any], cwd: str, timeout: int
) -> dict[str, Any]:
    command = [
        "pi",
        *ISOLATION,
        "--provider",
        config["provider"],
        "--model",
        config["model"],
        "--thinking",
        config["thinking"],
        "--system-prompt",
        system,
    ]
    started = time.monotonic()
    with subprocess.Popen(
        command,
        cwd=cwd,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        start_new_session=True,
    ) as proc:
        try:
            stdout, _stderr = proc.communicate(prompt, timeout=timeout)
        except subprocess.TimeoutExpired:
            os.killpg(proc.pid, signal.SIGKILL)
            proc.communicate()
            return {
                "error": "timeout; process group killed and parent reaped",
                "seconds": round(time.monotonic() - started, 3),
            }
        if proc.returncode:
            return {
                "error": f"Pi exit {proc.returncode}; stderr withheld",
                "seconds": round(time.monotonic() - started, 3),
            }
    try:
        result = parse_events(stdout, config["model"], config["provider"])
    except (ValueError, KeyError, TypeError) as exc:
        result = {"error": str(exc)}
    return {**result, "seconds": round(time.monotonic() - started, 3)}


def is_record(value: object) -> TypeGuard[dict[object, object]]:
    """Narrow untrusted JSON objects without assuming field names or value types."""
    return isinstance(value, dict)


def validate_ratings(
    value: dict[str, Any], answers: list[dict[str, str]], required_count: int
) -> None:
    expected = {a["id"]: a["answer"] for a in answers}
    ratings = value["ratings"]
    if len(ratings) != len(expected) or {r["id"] for r in ratings} != set(expected):
        raise ValueError("Judge omitted or duplicated answers")
    for r in ratings:
        content = r["content"]
        if len(content) != required_count or {x["index"] for x in content} != set(
            range(required_count)
        ):
            raise ValueError("Judge content coverage incomplete")
        if any(type(x["met"]) is not bool or not x.get("reason") for x in content):
            raise ValueError("Invalid content judgment")
        if not isinstance(r["critical"], list):
            raise ValueError("Invalid critical findings")
        for finding in r["critical"]:
            if not is_record(finding):
                raise ValueError("Invalid critical evidence")
            quote = finding.get("quote")
            reason = finding.get("reason")
            if (
                not isinstance(quote, str)
                or not quote.strip()
                or quote not in expected[r["id"]]
                or not isinstance(reason, str)
                or not reason.strip()
            ):
                raise ValueError("Invalid critical evidence")
        if r["clarity"] not in {"clear", "mixed", "unclear"} or not r["clarity_reason"]:
            raise ValueError("Invalid clarity judgment")
        for item in r["style"]:
            if (
                item["kind"] not in STYLE
                or not item["quote"]
                or item["quote"] not in expected[r["id"]]
                or not item["reason"]
                or item["region"] not in {"opening", "middle", "ending"}
            ):
                raise ValueError("Invalid style evidence")


def generate(split: str, arms: list[str], output: Path) -> None:
    protocol = read_json(ROOT / "protocol.json")
    cases = [c for c in read_json(ROOT / "cases.json") if c["split"] == split]
    if split == "holdout":
        selection = read_json(ROOT / "selection.json")
        if arms != ["baseline", selection["candidate"]]:
            raise ValueError("Holdout arms must match the frozen selection")
    jobs = [
        (c, a, rep)
        for c in cases
        for a in arms
        for rep in range(1, protocol["repetitions"] + 1)
    ]
    random.Random(protocol["order_seed"]).shuffle(jobs)
    targets = [output / f"{c['id']}-{a}-{rep}.json" for c, a, rep in jobs]
    if any(p.exists() for p in targets):
        raise FileExistsError("Output contains prior attempts; use a new directory")
    save_new(
        output / "run.json",
        {
            "split": split,
            "arms": arms,
            "jobs": len(jobs),
            "pi_version": subprocess.check_output(
                ["pi", "--version"], text=True
            ).strip(),
            "isolation": ISOLATION,
            "source_manifest": read_json(ROOT / "execution-manifest.json"),
        },
    )
    with tempfile.TemporaryDirectory(prefix="style-empty-") as cwd:

        def one(job: tuple[dict[str, Any], str, int]) -> None:
            case, arm, rep = job
            system = (ROOT / "prompts" / f"{arm}.txt").read_text(encoding="utf-8")
            result = invoke(
                system,
                case["prompt"],
                protocol["generator"],
                cwd,
                protocol["timeout_seconds"],
            )
            record = {
                "case": case["id"],
                "arm": arm,
                "rep": rep,
                "split": split,
                "length": case["length"],
                **result,
            }
            save_new(output / f"{case['id']}-{arm}-{rep}.json", record)
            print(case["id"], arm, rep, result.get("error", "ok"), flush=True)

        with ThreadPoolExecutor(max_workers=protocol["workers"]) as pool:
            list(pool.map(one, jobs))


def judge(split: str, responses: Path, output: Path) -> None:
    protocol = read_json(ROOT / "protocol.json")
    cases = [c for c in read_json(ROOT / "cases.json") if c["split"] == split]
    run = read_json(responses / "run.json")
    if run["split"] != split:
        raise ValueError("Response split mismatch")
    packets: list[tuple[dict[str, Any], list[dict[str, str]], dict[str, str]]] = []
    for case in cases:
        rows = [
            read_json(responses / f"{case['id']}-{arm}-{rep}.json")
            for arm in run["arms"]
            for rep in range(1, protocol["repetitions"] + 1)
        ]
        if any("error" in r for r in rows):
            raise ValueError("Failed generation; cannot silently omit it")
        random.Random(f"{protocol['order_seed']}:{case['id']}").shuffle(rows)
        answers = [
            {"id": f"R{i + 1}", "answer": r["answer"]} for i, r in enumerate(rows)
        ]
        mapping = {
            f"R{i + 1}": f"{r['case']}-{r['arm']}-{r['rep']}"
            for i, r in enumerate(rows)
        }
        packets.append((case, answers, mapping))
    if any((output / f"{c['id']}.json").exists() for c in cases):
        raise FileExistsError("Judgments already exist")
    with tempfile.TemporaryDirectory(prefix="style-judge-") as cwd:

        def one(
            packet: tuple[dict[str, Any], list[dict[str, str]], dict[str, str]],
        ) -> None:
            case, answers, mapping = packet
            prompt = json.dumps(
                {
                    "task": case["prompt"],
                    "required": case["required"],
                    "critical_examples": case["critical"],
                    "answers": answers,
                },
                ensure_ascii=False,
            )
            result = invoke(
                (ROOT / "judge.txt").read_text(encoding="utf-8"),
                prompt,
                protocol["judge"],
                cwd,
                protocol["timeout_seconds"],
            )
            if "error" not in result:
                try:
                    parsed = json.loads(result["answer"])
                    validate_ratings(parsed, answers, len(case["required"]))
                    result["ratings"] = parsed["ratings"]
                except (ValueError, KeyError, TypeError) as exc:
                    result["error"] = f"Invalid judgment: {exc}"
            save_new(
                output / f"{case['id']}.json",
                {"case": case["id"], "mapping": mapping, **result},
            )
            print("judge", case["id"], result.get("error", "ok"), flush=True)

        with ThreadPoolExecutor(max_workers=protocol["workers"]) as pool:
            list(pool.map(one, packets))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("freeze", "generate", "judge"))
    parser.add_argument(
        "--split", choices=("development", "holdout"), default="development"
    )
    parser.add_argument("--arms", nargs="+", choices=ARMS, default=list(ARMS))
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--responses", type=Path)
    args = parser.parse_args()
    if args.mode == "freeze":
        save_new(
            args.output,
            {
                "sha256": {
                    p.relative_to(ROOT).as_posix(): digest(p) for p in source_paths()
                }
            },
        )
        return
    verify_sources()
    if args.mode == "generate":
        generate(args.split, args.arms, args.output)
    else:
        if args.responses is None:
            parser.error("judge requires --responses")
        judge(args.split, args.responses, args.output)


if __name__ == "__main__":
    main()
