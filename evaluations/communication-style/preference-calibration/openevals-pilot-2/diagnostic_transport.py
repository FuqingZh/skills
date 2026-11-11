"""Add failure metadata without editing or weakening the frozen Pi transport.

This is an opt-in adapter for a new, authorized pilot controller. Historical
entrypoints and attempts remain unchanged. No call runs on import. Each invoke
loads a private copy of the frozen runner's namespace; process isolation,
timeout cleanup, parsing checks and one-attempt behavior remain its responsibility.

Only bounded identifier-shaped metadata and fixed error signals are retained.
Raw error text, response content, thinking, stderr and arbitrary event fields
are excluded. Signals are pattern matches, not verified root causes.
"""

from __future__ import annotations

import json
import re
import runpy
from pathlib import Path
from typing import Any, TypeGuard

CORE_PATH = Path(__file__).resolve().parents[2] / "run.py"
IDENTIFIER = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.:+-]{0,95}")
SECRET_PREFIX = re.compile(
    r"(?i)^(?:sk-|pk-|gh[pousr]_|github_pat_|eyJ|bearer|token|secret)"
)
HTTP_STATUS = re.compile(
    r"(?:^|\b(?:http(?: status)?|status(?: code)?)\s*[:=]?\s*)([45]\d\d)\b",
    re.IGNORECASE,
)
ERROR_SIGNALS = {
    "authentication": r"invalid[_ ]api[_ ]key|authentication|unauthorized",
    "permission": r"permission[_ ]denied|forbidden|access[_ ]denied",
    "rate_limit": r"rate[_ -]limit|too many requests",
    "quota_or_usage_limit": r"quota|usage limit|billing[_ ]hard[_ ]limit",
    "model_not_found": r"model_not_found",
    "context_limit": r"context[_ ]length[_ ]exceeded|maximum context length",
    "timeout": r"timed?[_ ]out|timeout",
    "connection": r"connection[_ ](?:error|reset|refused)|fetch failed",
}


def _is_record(value: object) -> TypeGuard[dict[object, object]]:
    return isinstance(value, dict)


def _identifier(value: object) -> str | None:
    if value is None:
        return None
    if (
        not isinstance(value, str)
        or not IDENTIFIER.fullmatch(value)
        or SECRET_PREFIX.search(value)
    ):
        return "[redacted]"
    return value


def _failure_metadata(stdout: str, model: str, provider: str) -> dict[str, Any]:
    expected = {"model": model, "provider": provider, "stopReason": "stop"}
    completions: list[dict[str, Any]] = []
    total = malformed = 0
    for line in stdout.split("\n"):
        if not line.strip():
            continue
        try:
            event: object = json.loads(line)
        except ValueError:
            malformed += 1
            continue
        if not _is_record(event) or event.get("type") != "message_end":
            continue
        message = event.get("message")
        if not _is_record(message) or message.get("role") != "assistant":
            continue
        total += 1
        if len(completions) == 4:
            continue
        raw_error = message.get("errorMessage")
        error = raw_error[:8192] if isinstance(raw_error, str) else ""
        completions.append(
            {
                "observed": {key: _identifier(message.get(key)) for key in expected},
                "mismatches": [
                    key for key, value in expected.items() if message.get(key) != value
                ],
                "error_present": bool(raw_error),
                "error_scan_truncated": isinstance(raw_error, str)
                and len(raw_error) > 8192,
                "http_statuses": sorted(
                    {int(m[1]) for m in HTTP_STATUS.finditer(error)}
                ),
                "error_signals": [
                    key
                    for key, pattern in ERROR_SIGNALS.items()
                    if re.search(pattern, error, re.IGNORECASE)
                ],
            }
        )
    return {
        "stage": "completion_validation",
        "expected": {key: _identifier(value) for key, value in expected.items()},
        "assistant_completion_count": total,
        "completions": completions,
        "omitted_completions": total - len(completions),
        "malformed_json_lines": malformed,
        "raw_error_text_retained": False,
    }


def invoke(
    system: str, prompt: str, config: dict[str, Any], cwd: str, timeout: int
) -> dict[str, Any]:
    """Preserve the original result, adding metadata only to rejected completions.

    A new controller selects this callable in its private pilot namespace with
    ``base["live"].__globals__["CORE"]["invoke"] = invoke``. Selection itself makes
    no call and grants no retry. The existing evaluate/live/save chain then
    retains the failure metadata alongside its original error.

    Process exits/timeouts still withhold stderr and have no completion metadata.
    A missing field is null; unsafe identifiers are redacted. Failed completions
    remain errors, never usable answers. This does not recover older lost logs.
    """
    core = runpy.run_path(str(CORE_PATH))
    original_parse = core["parse_events"]
    metadata: dict[str, Any] = {}

    def parse(stdout: str, model: str, provider: str) -> dict[str, Any]:
        try:
            return original_parse(stdout, model, provider)
        except (ValueError, KeyError, TypeError):
            metadata.update(_failure_metadata(stdout, model, provider))
            raise

    core["invoke"].__globals__["parse_events"] = parse
    result = core["invoke"](system, prompt, config, cwd, timeout)
    if "error" in result:
        result["failure_metadata"] = metadata or {
            "stage": "process",
            "completion_metadata_available": False,
        }
    return result
