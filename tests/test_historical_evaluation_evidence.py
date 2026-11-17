from __future__ import annotations

import hashlib
import json
from pathlib import Path
from statistics import median
from typing import cast

import yaml

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
EVALUATION_ROOT = REPOSITORY_ROOT / "evaluations/progressive-validation-selection"
CASES = sorted((EVALUATION_ROOT / "cases").glob("*.yaml"))


def _manifest_entries() -> dict[str, str]:
    paths = [
        path
        for path in EVALUATION_ROOT.rglob("*")
        if path.is_file()
        and path.name != "fixture-manifest.json"
        and "results" not in path.relative_to(EVALUATION_ROOT).parts
        and (
            "fixtures" in path.relative_to(EVALUATION_ROOT).parts
            or path.relative_to(EVALUATION_ROOT).parts[0] == "cases"
            or path.name
            in {
                "rubric.yaml",
                "judge-prompt.md",
                "result.schema.json",
                "batch-config.json",
                "batch.schema.json",
            }
        )
    ]
    return {
        path.relative_to(EVALUATION_ROOT).as_posix(): hashlib.sha256(
            path.read_bytes()
        ).hexdigest()
        for path in sorted(paths)
    }


def test_prompts_and_fixtures_do_not_leak_oracle_metadata() -> None:
    forbidden = ("expected", "forbidden", "rubric", "arm")
    for path in CASES:
        prompt = yaml.safe_load(path.read_text(encoding="utf-8"))["prompt"].lower()
        assert not any(token in prompt for token in forbidden), path
    for path in (EVALUATION_ROOT / "fixtures").rglob("*"):
        if path.is_file() and path.suffix in {".md", ".py", ".txt"}:
            text = path.read_text(encoding="utf-8").lower()
            assert not any(
                token in text
                for token in ("expected event", "forbidden family", "rubric")
            ), path


def test_alias_paths_exist_or_name_an_intentional_executable() -> None:
    executables = {"bash", "sh", "python", "python3", "make"}
    for path in CASES:
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
        fixture = EVALUATION_ROOT / "fixtures" / raw["fixture"]
        for config in raw["command_contract"]["families"].values():
            for command in config["commands"]:
                assert command[0] in executables, (path, command)
                for part in command[1:]:
                    if part.startswith(("scripts/", "tests/")) and part.endswith(
                        (".py", ".sh")
                    ):
                        assert (fixture / part).is_file(), (path, part)


def test_manifest_hashes_freeze_the_final_lexical_tree() -> None:
    manifest = json.loads((EVALUATION_ROOT / "fixture-manifest.json").read_text())
    entries = _manifest_entries()
    assert manifest["files"] == entries
    canonical = "".join(f"{path}\0{digest}\n" for path, digest in entries.items())
    assert (
        manifest["root_tree_sha256"] == hashlib.sha256(canonical.encode()).hexdigest()
    )


def test_w07_paired_results_preserve_controls_and_bounded_claim() -> None:
    repository_evaluation_root = (
        Path(__file__).resolve().parents[1] / "evaluations/ai-native-implementation"
    )
    result_path = repository_evaluation_root / "results/W07-2026-08-14.json"
    payload = cast(
        dict[str, object], json.loads(result_path.read_text(encoding="utf-8"))
    )
    fixture = cast(dict[str, str], payload["fixture"])
    for name, path in (
        ("case_sha256", repository_evaluation_root / "cases/W07.yaml"),
        ("scorer_sha256", repository_evaluation_root / "score_w07.py"),
    ):
        assert fixture[name] == hashlib.sha256(path.read_bytes()).hexdigest()
    fixture_root = repository_evaluation_root / "fixtures/W07"
    fixture_manifest = "".join(
        f"{hashlib.sha256(path.read_bytes()).hexdigest()}  "
        f"./{path.relative_to(fixture_root).as_posix()}\n"
        for path in sorted(path for path in fixture_root.rglob("*") if path.is_file())
    )
    assert (
        fixture["fixture_tree_sha256"]
        == hashlib.sha256(fixture_manifest.encode()).hexdigest()
    )

    arms = cast(dict[str, dict[str, object]], payload["arms"])
    assert (
        arms["candidate"]["agents_template_sha256"]
        == "d71053d50e0835912d84b85ad6492744db376ca80cac723688a9a20a27a216e2"
    )
    assert (
        cast(int, arms["candidate"]["agents_template_words"])
        - cast(int, arms["baseline"]["agents_template_words"])
        == 70
    )

    runs = cast(list[dict[str, object]], payload["runs"])
    assert len(runs) == 6
    assert [cast(str, run["arm"]) for run in runs] == [
        "baseline",
        "candidate",
        "candidate",
        "baseline",
        "baseline",
        "candidate",
    ]
    for run in runs:
        assert run["correctness_passed"] is True
        assert run["critical_failures"] == 0
        assert run["diagnostic_suppressions"] == 0
        assert run["repeated_reasoning_or_scope_commentary"] == 0
        assert run["scope_churn_events"] == 0
        assert run["compactions"] == 0
        assert run["ao_routes"] == 0
        assert run["calibration_routes"] == 0
        assert cast(int, run["total_tokens"]) == cast(int, run["input_tokens"]) + cast(
            int, run["output_tokens"]
        )

    baseline = [run for run in runs if run["arm"] == "baseline"]
    candidate = [run for run in runs if run["arm"] == "candidate"]
    observed = cast(dict[str, dict[str, object]], payload["observed_aggregate"])
    for arm, arm_runs in (("baseline", baseline), ("candidate", candidate)):
        aggregate = observed[arm]
        assert aggregate["median_elapsed_seconds"] == median(
            cast(float, run["elapsed_seconds"]) for run in arm_runs
        )
        assert aggregate["median_total_tokens"] == median(
            cast(int, run["total_tokens"]) for run in arm_runs
        )
        assert aggregate["median_first_effective_edit_upper_bound_seconds"] == median(
            cast(int, run["first_effective_edit_upper_bound_seconds"])
            for run in arm_runs
        )
        assert aggregate["total_rework_cycles"] == sum(
            cast(int, run["rework_cycles"]) for run in arm_runs
        )

    decision = cast(dict[str, object], payload["decision"])
    assert decision["adopt_compact_policy"] is True
    assert decision["generalization_claim"] is False


def test_runtime_archive_preserves_bytes_and_removes_active_entrypoints() -> None:
    archive = REPOSITORY_ROOT / "evaluations/archive/writable-agent-runtime"
    manifest_path = archive / "manifest.json"
    assert hashlib.sha256(manifest_path.read_bytes()).hexdigest() == (
        "9ce38e89db9ec99c2d8a64c70d84d1fee4c75e2f6be4f0385ff69fc051497c3e"
    )
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert manifest["source_ref"] == "8f14136352780fc5e2471bf05ec322d4953fa0e9"
    files = cast(dict[str, str], manifest["files"])
    assert len(files) == 20
    snapshots = {
        path.relative_to(archive).as_posix() for path in archive.rglob("*.txt")
    }
    assert snapshots == {f"{source}.txt" for source in files}
    assert not list(archive.rglob("*.py"))
    for source, digest in files.items():
        assert not (REPOSITORY_ROOT / source).exists(), source
        snapshot = archive / f"{source}.txt"
        assert hashlib.sha256(snapshot.read_bytes()).hexdigest() == digest, source


def test_frozen_case_inventory_and_raw_contracts_remain_intact() -> None:
    case_ids = {f"P{number:02}" for number in range(1, 11)} | {
        f"H{number:02}" for number in range(1, 5)
    }
    assert {path.stem for path in CASES} == case_ids | {"C01"}
    config = json.loads((EVALUATION_ROOT / "batch-config.json").read_text())
    assert config["case_ids"] == ["P02", "P03", "P05"]
    assert config["live_canary_case_id"] == "C01"
    for path in CASES:
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
        assert raw["id"] == path.stem
        contract = raw["command_contract"]
        assert all(contract[key] for key in ("required", "ordered")), path
        assert "forbidden" in contract, path
