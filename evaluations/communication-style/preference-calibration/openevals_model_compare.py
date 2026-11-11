"""Compare two judge configurations with fixed contribution-v1 and ID evidence.

Reuse the frozen serial execution engine and paragraph-ID adapter. Arm names
baseline/revised are storage keys for current/challenger models here, not prompt
variants. Provider and model can both differ; identical thinking labels do not
establish equal compute. No historical source or output is modified.
"""

from __future__ import annotations

import runpy
from collections.abc import Callable
from pathlib import Path
from typing import Any, TypeGuard
from unittest.mock import patch

ROOT = Path(__file__).resolve().parent
IDS = runpy.run_path(str(ROOT / "openevals_id_evidence.py"))
ENGINE = IDS["ENGINE"]
BASE = IDS["BASE"]
ID_EVALUATE = IDS["evaluate_prompt"]
ID_PREFLIGHT = IDS["preflight"]
ENGINE_VERIFY = ENGINE["verify"]


def _is_record(value: object) -> TypeGuard[dict[object, object]]:
    return isinstance(value, dict)


def configuration(study: Path, arm: str) -> dict[str, str]:
    if arm not in ("baseline", "revised"):
        raise ValueError("Unknown model arm")
    config: object = BASE["load"](study / "protocol.json")["models"][arm]
    fields = ("provider", "model", "thinking")
    if not _is_record(config) or set(config) != set(fields):
        raise ValueError("Invalid model configuration fields")
    result: dict[str, str] = {}
    for key in fields:
        value = config[key]
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Invalid model configuration values")
        result[key] = value
    return result


def fixed_prompt(study: Path, _arm: str) -> str:
    """Both models get the same frozen semantic template; no arm name is sent."""
    return (study / "revised-helpfulness.txt").read_text(encoding="utf-8")


def verify(study: Path) -> None:
    ENGINE_VERIFY(study)
    configs = [configuration(study, arm) for arm in ("baseline", "revised")]
    if configs[0] != BASE["CONFIG"] or configs[0] == configs[1]:
        raise ValueError("Expected current model and a distinct challenger")
    if any(config["thinking"] != "high" for config in configs):
        raise ValueError("Both configurations must request high thinking")
    reference = ROOT / "openevals-contribution-v1-id-evidence"
    for name in ("guidance.txt", "revised-helpfulness.txt", "id-instructions.txt"):
        if (study / name).read_bytes() != (reference / name).read_bytes():
            raise ValueError("Fixed criteria or citation instructions changed")


def evaluate_prompt(
    study: Path,
    arm: str,
    context: str,
    answer: str,
    invoke: Callable[[str, str], dict[str, Any]],
) -> dict[str, Any]:
    config = configuration(study, arm)
    # evaluate, Client and live share this private namespace. The native Pi
    # transport receives this config, including provider, through live().
    with (
        patch.dict(BASE["evaluate"].__globals__, {"CONFIG": config}),
        patch.dict(ENGINE, {"prompt": fixed_prompt}),
    ):
        record = ID_EVALUATE(study, arm, context, answer, invoke)
    record["judge_configuration"] = config
    return record


def preflight(study: Path) -> dict[str, Any]:
    with (
        patch.dict(ENGINE, {"prompt": fixed_prompt}),
        patch.dict(ID_PREFLIGHT.__globals__, {"evaluate_prompt": evaluate_prompt}),
    ):
        report = ID_PREFLIGHT(study)
    report["comparison"] = "judge_configurations_with_fixed_criteria"
    report["models"] = {
        arm: configuration(study, arm) for arm in ("baseline", "revised")
    }
    return report


def main() -> None:
    with patch.dict(
        ENGINE["main"].__globals__,
        {"verify": verify, "evaluate_prompt": evaluate_prompt, "preflight": preflight},
    ):
        ENGINE["main"]()


if __name__ == "__main__":
    main()
