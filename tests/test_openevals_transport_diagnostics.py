"""Offline regression checks for opt-in failure metadata; never launch Pi."""

from __future__ import annotations

import json
import runpy
import signal
import subprocess
from pathlib import Path
from typing import Any
from unittest.mock import patch

import pytest

ROOT = Path(__file__).resolve().parents[1]
PILOT = (
    ROOT / "evaluations/communication-style/preference-calibration/openevals-pilot-2"
)
ADAPTER = runpy.run_path(str(PILOT / "diagnostic_transport.py"))
CORE = runpy.run_path(str(ADAPTER["CORE_PATH"]))
CONFIG = {"model": "gpt-6-sol", "provider": "openai", "thinking": "high"}


def stream(**overrides: object) -> str:
    message: dict[str, Any] = {
        "role": "assistant",
        "model": CONFIG["model"],
        "provider": CONFIG["provider"],
        "stopReason": "stop",
        "content": [
            {"type": "thinking", "thinking": "PRIVATE_THINKING"},
            {"type": "text", "text": "visible\u2028answer"},
        ],
        "usage": {"output": 5},
        "unknown": "EXTRA_MESSAGE_SECRET",
    }
    message.update(overrides)
    return "\n".join(
        json.dumps(event)
        for event in [
            {
                "type": "message_end",
                "message": message,
                "unknown": "EXTRA_EVENT_SECRET",
            },
            {"type": "agent_settled", "aborted": False},
        ]
    )


def invoke_fake(stdout: str, returncode: int = 0) -> dict[str, Any]:
    with patch("subprocess.Popen") as popen:
        process = popen.return_value.__enter__.return_value
        process.returncode = returncode
        process.communicate.return_value = (stdout, "STDERR_SECRET")
        result = ADAPTER["invoke"]("system", "prompt", CONFIG, ".", 1)
        assert popen.call_count == process.communicate.call_count == 1
        assert popen.call_args.kwargs["start_new_session"] is True
        assert "--no-tools" in popen.call_args.args[0]
        return result


@pytest.mark.parametrize(
    ("field", "value"),
    [("model", "other-model"), ("provider", "other-provider"), ("stopReason", "error")],
)
def test_each_mismatch_is_visible_without_retaining_private_text(
    field: str, value: str
) -> None:
    result = invoke_fake(
        stream(
            **{field: value},
            errorMessage=(
                "HTTP 429: usage limit; Authorization: Bearer CREDENTIAL_SECRET"
            ),
        )
    )
    assert result["error"] == "Model identity or completion status mismatch"
    assert "answer" not in result and "usage" not in result
    metadata = result["failure_metadata"]
    assert metadata["expected"] == {
        "model": "gpt-6-sol",
        "provider": "openai",
        "stopReason": "stop",
    }
    completion = metadata["completions"][0]
    assert completion["observed"][field] == value
    assert completion["mismatches"] == [field]
    assert completion["http_statuses"] == [429]
    assert completion["error_signals"] == ["quota_or_usage_limit"]
    serialized = json.dumps(result)
    for forbidden in (
        "PRIVATE_THINKING",
        "SECRET",
        "Authorization",
        "visible",
        "Bearer",
    ):
        assert forbidden not in serialized


def test_success_preserves_frozen_parser_result() -> None:
    result = invoke_fake(stream())
    result.pop("seconds")
    assert result == CORE["parse_events"](stream(), CONFIG["model"], CONFIG["provider"])
    assert "failure_metadata" not in result


@pytest.mark.parametrize(
    "stdout",
    [
        stream(stopReason="length"),
        stream() + '\n{"type":"auto_retry_start"}',
        stream() + '\n{"type":"tool_execution_start"}',
        stream() + "\n" + stream(),
        stream().split("\n")[0],
        stream() + "\nINVALID_JSON_SECRET",
    ],
)
def test_original_rejections_remain_rejections(stdout: str) -> None:
    with pytest.raises(ValueError) as error:
        CORE["parse_events"](stdout, CONFIG["model"], CONFIG["provider"])
    result = invoke_fake(stdout)
    assert result["error"] == str(error.value)
    assert result["failure_metadata"]["stage"] == "completion_validation"
    assert "answer" not in result and "SECRET" not in json.dumps(result)


@pytest.mark.parametrize(
    "value",
    ["sk-test-secret", "https://private/path", "Bearer credential", "x" * 97, {}],
)
def test_unsafe_identifiers_are_redacted(value: object) -> None:
    result = invoke_fake(stream(model=value))
    completion = result["failure_metadata"]["completions"][0]
    assert completion["observed"]["model"] == "[redacted]"
    assert completion["mismatches"] == ["model"]


def test_missing_fields_and_bounded_diagnostics() -> None:
    result = invoke_fake("\n".join([stream(model=None, errorMessage="x" * 9000)] * 5))
    metadata = result["failure_metadata"]
    assert metadata["assistant_completion_count"] == 5
    assert metadata["omitted_completions"] == 1
    assert len(metadata["completions"]) == 4
    assert metadata["completions"][0]["observed"]["model"] is None
    assert metadata["completions"][0]["error_scan_truncated"] is True
    assert len(json.dumps(result)) < 2000


def test_process_exit_does_not_claim_available_completion_metadata() -> None:
    result = invoke_fake(stream(), returncode=1)
    assert result["error"] == "Pi exit 1; stderr withheld"
    assert result["failure_metadata"] == {
        "stage": "process",
        "completion_metadata_available": False,
    }
    assert "SECRET" not in json.dumps(result)


def test_timeout_keeps_existing_kill_and_reap_behavior() -> None:
    with patch("subprocess.Popen") as popen, patch("os.killpg") as kill:
        process = popen.return_value.__enter__.return_value
        process.pid = 1234
        process.communicate.side_effect = [
            subprocess.TimeoutExpired("pi", 1),
            ("STDOUT_SECRET", "STDERR_SECRET"),
        ]
        result = ADAPTER["invoke"]("system", "prompt", CONFIG, ".", 1)
        kill.assert_called_once_with(1234, signal.SIGKILL)
        assert popen.call_count == 1 and process.communicate.call_count == 2
    assert result["error"] == "timeout; process group killed and parent reaped"
    assert result["failure_metadata"]["completion_metadata_available"] is False
    assert "SECRET" not in json.dumps(result)
