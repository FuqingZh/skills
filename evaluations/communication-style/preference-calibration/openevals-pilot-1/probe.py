#!/usr/bin/env python3
"""One-off OpenEvals/Pi development probe; no retry, repair, or automatic next case.

The SDK-shaped client delegates exactly once to the existing isolated transport.
Only visible final text and usage are retained. Each attempt is reserved before
execution; malformed outputs remain in their original records. Preflight uses
synthetic fixtures and blocks in-process network access, including tracing.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib
import importlib.metadata
import json
import os
import runpy
import socket
import subprocess
import tempfile
from collections.abc import Callable, Generator
from contextlib import contextmanager
from pathlib import Path
from types import SimpleNamespace
from typing import Any, TypeGuard
from unittest.mock import patch

ROOT = Path(__file__).resolve().parent
CORE = runpy.run_path(str(ROOT.parent.parent / "run.py"))
SCRATCH = ROOT.parents[3] / ".venv/openevals-probe-5753dc7"
CONFIG = {"provider": "openai", "model": "gpt-6-sol", "thinking": "high"}
SETTINGS = {
    "retry": {"enabled": False, "maxRetries": 0, "provider": {"maxRetries": 0}},
    "compaction": {"enabled": False},
    "cacheWarming": "off",
    "transport": "sse",
    "enableInstallTelemetry": False,
    "enableAnalytics": False,
}
FILES = (
    "probe.py",
    "schema.json",
    "instructions.txt",
    "protocol.json",
    "upstream-helpfulness.txt",
    "upstream-LICENSE.txt",
    "../deletion-pilot-1.json",
    "../../run.py",
)


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def save(path: Path, value: Any) -> None:
    CORE["save_new"](path, value)


def hashes() -> dict[str, str]:
    return {
        name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() for name in FILES
    }


def is_object(value: object) -> TypeGuard[dict[object, object]]:
    return isinstance(value, dict)


def is_list(value: object) -> TypeGuard[list[object]]:
    return isinstance(value, list)


def validate(value: object, answer: str) -> None:
    if not is_object(value) or set(value) != {"findings"}:
        raise ValueError("Expected findings array only")
    findings = value["findings"]
    if not is_list(findings):
        raise ValueError("Expected findings array only")
    for item in findings:
        if not is_object(item) or set(item) != {"kind", "evidence", "reason"}:
            raise ValueError("Invalid finding fields")
        if item["kind"] not in ("strength", "issue", "uncertain"):
            raise ValueError("Invalid finding kind")
        for field in ("evidence", "reason"):
            text = item[field]
            if not isinstance(text, str) or not text.strip():
                raise ValueError("Empty finding text")
            if field == "evidence" and text not in answer:
                raise ValueError("Evidence absent from answer")


@contextmanager
def agent() -> Generator[str, None, None]:
    source = Path(os.environ.get("PI_CODING_AGENT_DIR", Path.home() / ".pi/agent"))
    with tempfile.TemporaryDirectory(prefix="agent-", dir=SCRATCH) as directory:
        root = Path(directory)
        save(root / "settings.json", SETTINGS)
        for name in ("auth.json", "models.json"):
            if (source / name).is_file():
                (root / name).symlink_to((source / name).resolve())
        with patch.dict(
            os.environ, {"PI_CODING_AGENT_DIR": directory, "PI_OFFLINE": "1"}
        ):
            yield directory


def live(system: str, prompt: str) -> dict[str, Any]:
    with agent() as directory:
        return CORE["invoke"](system, prompt, CONFIG, directory, 300)


class Client:
    def __init__(
        self, invoke: Callable[[str, str], dict[str, Any]], record: dict[str, Any]
    ):
        self.invoke = invoke
        self.record = record
        self.calls = 0
        self.chat = SimpleNamespace(completions=self)

    def create(self, **params: Any) -> SimpleNamespace:
        if self.calls:
            raise RuntimeError("Second invocation prohibited")
        self.calls += 1
        schema = params["response_format"]["json_schema"]["schema"]
        if schema != load(ROOT / "schema.json") or params["model"] != CONFIG["model"]:
            raise ValueError("Unexpected model/schema")
        system = (
            (ROOT / "instructions.txt").read_text(encoding="utf-8")
            + "\n"
            + json.dumps(schema, ensure_ascii=False)
        )
        prompt = json.dumps(params["messages"], ensure_ascii=False)
        self.record["request"] = {"system": system, "messages": params["messages"]}
        self.record["transport"] = self.invoke(system, prompt)
        if "error" in self.record["transport"]:
            raise RuntimeError(self.record["transport"]["error"])
        return SimpleNamespace(
            choices=[
                SimpleNamespace(
                    message=SimpleNamespace(content=self.record["transport"]["answer"])
                )
            ]
        )


def evaluate(
    context: str, answer: str, invoke: Callable[[str, str], dict[str, Any]]
) -> dict[str, Any]:
    record: dict[str, Any] = {"context": context, "answer_under_review": answer}
    client = Client(invoke, record)
    factory = importlib.import_module("openevals.llm").create_llm_as_judge
    tracing = importlib.import_module("langsmith").tracing_context
    try:
        with tracing(enabled=False):
            evaluator = factory(
                prompt=(ROOT / "upstream-helpfulness.txt").read_text(encoding="utf-8"),
                judge=client,
                model="openai:" + CONFIG["model"],
                output_schema=load(ROOT / "schema.json"),
            )
            result = evaluator(inputs=context, outputs=answer)
        validate(result, answer)
        record["diagnostic"] = result
    except Exception as exc:
        record["error"] = f"{type(exc).__name__}: {exc}"
    record["invocations"] = client.calls
    return record


def preflight() -> None:
    upstream = importlib.import_module("openevals.prompts").RAG_HELPFULNESS_PROMPT
    if upstream != (ROOT / "upstream-helpfulness.txt").read_text(encoding="utf-8"):
        raise ValueError("Upstream prompt differs")
    good = '{"findings":[{"kind":"strength","evidence":"甲","reason":"fixture"}]}'
    fixtures = [
        good,
        '{"findings":[]}',
        '{"findings":[],}',
        '{"wrong":[]}',
        good.replace("甲", "乙"),
        good.replace("strength", "unknown"),
        good.replace("fixture", ""),
        None,
    ]
    records: list[dict[str, Any]] = []
    for index, raw in enumerate(fixtures):

        def fake(_system: str, _prompt: str, text: str | None = raw) -> dict[str, Any]:
            return (
                {"answer": text}
                if text is not None
                else {"error": "fixture transport failure"}
            )

        record = evaluate("合成问题", "甲", fake)
        if record["invocations"] != 1 or ("error" in record) != (index >= 2):
            raise ValueError(f"Preflight fixture {index} failed")
        if raw is not None and record["transport"]["answer"] != raw:
            raise ValueError("Raw response changed")
        records.append(record)
    with tempfile.TemporaryDirectory(dir=SCRATCH) as directory:
        path = Path(directory) / "exclusive.json"
        save(path, {})
        try:
            save(path, {})
        except FileExistsError:
            pass
        else:
            raise ValueError("Overwrite allowed")
    with agent() as directory:
        version = subprocess.run(
            ["pi", *CORE["ISOLATION"], "--version"],
            cwd=directory,
            capture_output=True,
            text=True,
            timeout=20,
            check=True,
        ).stdout.strip()
        if version != "1.5.0":
            raise ValueError("Unexpected Pi version")
    packages = {
        d.metadata["Name"]: d.version for d in importlib.metadata.distributions()
    }
    save(
        ROOT / "preflight.json",
        {
            "fixtures": records,
            "exclusive_write": True,
            "pi_version": version,
            "agent_settings": SETTINGS,
            "packages": packages,
            "model_calls": 0,
        },
    )


def run(case_id: str) -> None:
    if load(ROOT / "manifest.json") != hashes():
        raise ValueError("Frozen source changed")
    if not (ROOT / "preflight.json").exists():
        raise ValueError("Preflight missing")
    if case_id == "P02" and load(ROOT / "review-P01.json")["decision"] != "continue":
        raise ValueError("First case not approved")
    output = ROOT / "results" / case_id
    output.mkdir(parents=True, exist_ok=False)
    cases = load(ROOT.parent / "deletion-pilot-1.json")["cases"]
    case = next(item for item in cases if item["id"] == case_id)
    for side in ("A", "B"):
        save(
            output / f"{side}.started.json",
            {"case": case_id, "side": side, "attempt": 1},
        )
        record = evaluate(case["context"], case["answers"][side], live)
        save(output / f"{side}.json", record)
        if "error" in record:
            raise RuntimeError("Probe failed; stop without retry or next case")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("preflight", "freeze", "P01", "P02"))
    args = parser.parse_args()
    os.environ.update(
        {
            "LANGSMITH_TRACING": "false",
            "LANGCHAIN_TRACING_V2": "false",
            "LANGCHAIN_TRACING": "false",
        }
    )
    attempts: list[str] = []

    def deny(*_args: Any, **_kwargs: Any) -> Any:
        attempts.append("blocked")
        raise RuntimeError("In-process networking prohibited")

    with (
        patch.object(socket.socket, "connect", deny),
        patch.object(socket.socket, "connect_ex", deny),
        patch.object(socket, "getaddrinfo", deny),
    ):
        if args.mode == "preflight":
            preflight()
        elif args.mode == "freeze":
            save(ROOT / "manifest.json", hashes())
        else:
            run(args.mode)
        if attempts:
            raise RuntimeError("Unexpected network attempt; stop")
    print(json.dumps({"mode": args.mode, "in_process_network_attempts": len(attempts)}))


if __name__ == "__main__":
    main()
