"""Offline checks for the bounded communication-style experiment."""

from __future__ import annotations

import json
import runpy
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
EVAL = ROOT / "evaluations/communication-style"
RUN = runpy.run_path(str(EVAL / "run.py"))


def events(*, model: str = "model", stop: str = "stop") -> str:
    return "\n".join(
        json.dumps(event)
        for event in [
            {
                "type": "message_end",
                "message": {
                    "role": "assistant",
                    "model": model,
                    "provider": "provider",
                    "stopReason": stop,
                    "content": [
                        {"type": "thinking", "thinking": "private reasoning"},
                        {"type": "text", "text": "visible\u2028answer"},
                    ],
                    "usage": {"output": 5},
                },
            },
            {"type": "agent_settled", "aborted": False},
        ]
    )


def test_parser_discards_thinking_and_preserves_unicode_line_separator() -> None:
    result = RUN["parse_events"](events(), "model", "provider")
    assert result["answer"] == "visible\u2028answer"
    assert "private reasoning" not in json.dumps(result)


@pytest.mark.parametrize(
    "stream",
    [
        "{}",
        events(model="wrong"),
        events(stop="length"),
        events() + '\n{"type":"tool_execution_start"}',
        events() + '\n{"type":"auto_retry_start"}',
        events().split("\n")[0],
        events() + "\n" + events(),
    ],
)
def test_parser_rejects_invalid_runs(stream: str) -> None:
    with pytest.raises(ValueError):
        RUN["parse_events"](stream, "model", "provider")


def test_attempt_files_cannot_be_overwritten(tmp_path: Path) -> None:
    target = tmp_path / "sample.json"
    RUN["save_new"](target, {"answer": "original"})
    with pytest.raises(FileExistsError):
        RUN["save_new"](target, {"answer": "replacement"})
    assert json.loads(target.read_text())["answer"] == "original"


def test_judge_requires_all_ratings_content_and_exact_quotes() -> None:
    answer = [{"id": "R1", "answer": "answer"}]
    rating = {
        "id": "R1",
        "content": [{"index": 0, "met": True, "reason": "evidence"}],
        "critical": [],
        "style": [],
        "clarity": "clear",
        "clarity_reason": "connected explanation",
    }
    RUN["validate_ratings"]({"ratings": [rating]}, answer, 1)
    with pytest.raises(ValueError):
        RUN["validate_ratings"]({"ratings": []}, answer, 1)
    with pytest.raises(ValueError):
        RUN["validate_ratings"]({"ratings": [rating]}, answer, 2)
    rating["style"] = [
        {
            "kind": "preamble",
            "quote": "invented quotation",
            "reason": "filler",
            "region": "opening",
        }
    ]
    with pytest.raises(ValueError):
        RUN["validate_ratings"]({"ratings": [rating]}, answer, 1)


def test_cases_are_balanced_and_families_do_not_cross_splits() -> None:
    cases = json.loads((EVAL / "cases.json").read_text())
    assert len(cases) == len({c["id"] for c in cases}) == 12
    families: dict[str, set[str]] = {}
    for split in ("development", "holdout"):
        rows = [c for c in cases if c["split"] == split]
        assert len(rows) == 6
        assert sum(c["length"] == "long" for c in rows) == 3
        assert sum(c["origin"] == "reconstructed" for c in rows) == 4
        assert all(c["required"] and c["critical"] for c in rows)
        families[split] = {c["family"] for c in rows}
    assert not families["development"] & families["holdout"]


def test_prompts_are_frozen_and_example_is_only_addition() -> None:
    RUN["verify_sources"]()
    direct = (EVAL / "prompts/direct.txt").read_text()
    assert (EVAL / "prompts/example.txt").read_text().startswith(direct + "\n")


def test_isolation_disables_ambient_instruction_and_tool_loading() -> None:
    flags = RUN["ISOLATION"]
    assert {
        "--no-session",
        "--no-tools",
        "--no-extensions",
        "--no-mcp",
        "--no-skills",
        "--no-prompt-templates",
        "--no-context-files",
        "--no-approve",
    }.issubset(flags)
    assert "--continue" not in flags
    assert "--resume" not in flags
