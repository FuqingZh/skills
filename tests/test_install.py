from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

import pytest

from scripts.validate_skills import _validate_active_references
from tests.support import REPOSITORY_ROOT
from tests.support.installer import run_installer

AGENTS = ("codex", "grok", "pi")
HOME_VARIABLES = {
    "codex": "CODEX_HOME",
    "grok": "CALIBRATION_GROK_HOME",
    "pi": "PI_CODING_AGENT_DIR",
}
FIRST_PARTY = ("calibration", "writing-code-docs", "closeout", "retrospect")
BEGIN = "<!-- FuqingZh/skills:begin -->"
END = "<!-- FuqingZh/skills:end -->"
LEGACY_BEGIN = "<!-- calibration:begin -->"
LEGACY_END = "<!-- calibration:end -->"


@pytest.fixture(autouse=True)
def isolated_environment(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("HOME", str(tmp_path / "user"))
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / "config"))
    for variable in HOME_VARIABLES.values():
        monkeypatch.delenv(variable, raising=False)


def snapshot_tree(root: Path) -> list[tuple[str, str, bytes | str]]:
    return [
        (
            str(path.relative_to(root)),
            "link" if path.is_symlink() else "file" if path.is_file() else "dir",
            os.readlink(path)
            if path.is_symlink()
            else path.read_bytes()
            if path.is_file()
            else b"",
        )
        for path in sorted(root.rglob("*"))
    ]


def install(home: Path, agent: str, *args: str) -> subprocess.CompletedProcess[str]:
    return run_installer(
        None, "--agent", agent, *args, env_updates={HOME_VARIABLES[agent]: str(home)}
    )


def cleanup(home: Path, agent: str, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            str(REPOSITORY_ROOT / "scripts/cleanup-legacy-links.sh"),
            "--agent",
            agent,
            *args,
        ],
        cwd=REPOSITORY_ROOT,
        env={**os.environ, HOME_VARIABLES[agent]: str(home)},
        capture_output=True,
        text=True,
        check=False,
    )


@pytest.mark.parametrize("agent", AGENTS)
def test_install_renders_only_global_block(tmp_path: Path, agent: str) -> None:
    home = tmp_path / agent
    result = install(home, agent)
    assert result.returncode == 0, result.stderr
    template = (
        (REPOSITORY_ROOT / "codex/AGENTS.md.template")
        .read_text()
        .replace("{{HOST_AUTHORITY}}", str(tmp_path / "config/calibration/AGENTS.md"))
        .rstrip("\n")
    )
    if agent != "codex":
        template = template.replace("$calibration", "calibration")
    assert (home / "AGENTS.md").read_text() == f"{BEGIN}\n{template}\n{END}\n"
    assert list(home.iterdir()) == [home / "AGENTS.md"]
    before = snapshot_tree(home)
    assert install(home, agent).returncode == 0
    assert snapshot_tree(home) == before


@pytest.mark.parametrize("agent", AGENTS)
def test_block_refresh_preserves_personal_text_and_backs_up(
    tmp_path: Path, agent: str
) -> None:
    home = tmp_path / agent
    home.mkdir()
    target = home / "AGENTS.md"
    original = f"Personal prefix.\n\n{BEGIN}\nold block\n{END}\nPersonal suffix.\n"
    target.write_text(original)
    target.chmod(0o640)
    result = install(home, agent, "--force")
    assert result.returncode == 0, result.stderr
    assert target.read_text().startswith("Personal prefix.\n\n" + BEGIN)
    assert target.read_text().endswith(END + "\nPersonal suffix.\n")
    assert target.stat().st_mode & 0o777 == 0o640
    assert [p.read_text() for p in home.glob("AGENTS.md.bak.*")] == [original]


@pytest.mark.parametrize("agent", ("pi", "grok"))
def test_non_codex_appends_to_unmarked_personal_file(
    tmp_path: Path, agent: str
) -> None:
    home = tmp_path / agent
    home.mkdir()
    (home / "AGENTS.md").write_text("My instructions.\n")
    assert install(home, agent).returncode == 0
    assert (home / "AGENTS.md").read_text().startswith("My instructions.\n" + BEGIN)


@pytest.mark.parametrize("original", ["Personal rules.\n", ""])
def test_codex_requires_force_for_unmarked_file(tmp_path: Path, original: str) -> None:
    home = tmp_path / "codex"
    home.mkdir()
    target = home / "AGENTS.md"
    target.write_text(original)
    before = snapshot_tree(home)
    result = install(home, "codex")
    assert result.returncode != 0
    assert "--force" in result.stderr
    assert snapshot_tree(home) == before
    assert install(home, "codex", "--force", "--dry-run").returncode == 0
    assert snapshot_tree(home) == before
    result = install(home, "codex", "--force")
    assert result.returncode == 0, result.stderr
    assert target.read_text().startswith(BEGIN)
    assert "Personal rules." not in target.read_text()
    assert [p.read_text() for p in home.glob("AGENTS.md.bak.*")] == [original]
    assert "restore" in result.stdout


def test_force_never_disables_migration_backup(tmp_path: Path) -> None:
    home = tmp_path / "codex"
    home.mkdir()
    (home / "AGENTS.md").write_text("personal")
    before = snapshot_tree(home)
    assert install(home, "codex", "--force", "--no-backup").returncode != 0
    assert snapshot_tree(home) == before


@pytest.mark.parametrize("agent", AGENTS)
@pytest.mark.parametrize("force", [(), ("--force",)])
def test_regular_refresh_always_backs_up(
    tmp_path: Path, agent: str, force: tuple[str, ...]
) -> None:
    home = tmp_path / agent
    home.mkdir()
    (home / "AGENTS.md").write_text(f"{BEGIN}\nold\n{END}\n")
    assert install(home, agent, *force).returncode == 0
    assert [p.read_text() for p in home.glob("*.bak.*")] == [f"{BEGIN}\nold\n{END}\n"]
    before = snapshot_tree(home)
    assert install(home, agent, *force).returncode == 0
    assert snapshot_tree(home) == before


@pytest.mark.parametrize("agent", AGENTS)
@pytest.mark.parametrize("kind", ("directory", "symlink", "dangling"))
def test_force_refuses_nonregular_targets(
    tmp_path: Path, agent: str, kind: str
) -> None:
    home = tmp_path / agent
    home.mkdir()
    target = home / "AGENTS.md"
    foreign = tmp_path / "foreign"
    if kind == "directory":
        target.mkdir()
        (target / "keep").write_text("keep")
    else:
        if kind == "symlink":
            foreign.write_text("keep")
        target.symlink_to(foreign)
    before = snapshot_tree(tmp_path)
    assert install(home, agent, "--force").returncode != 0
    assert snapshot_tree(tmp_path) == before


@pytest.mark.parametrize("agent", AGENTS)
@pytest.mark.parametrize(
    "text",
    [
        f"{BEGIN}\nunclosed\n",
        f"{END}\n",
        f"{BEGIN}\n{END}\n{BEGIN}\n{END}\n",
        "prefix <!-- calibration:begin -->\n",
    ],
)
def test_malformed_blocks_fail_even_with_force(
    tmp_path: Path, agent: str, text: str
) -> None:
    home = tmp_path / agent
    home.mkdir()
    (home / "AGENTS.md").write_text(text)
    before = snapshot_tree(home)
    assert install(home, agent, "--force").returncode != 0
    assert snapshot_tree(home) == before


def test_all_targets_are_preflighted_before_writes(tmp_path: Path) -> None:
    homes = [tmp_path / agent for agent in AGENTS]
    homes[-1].mkdir()
    (homes[-1] / "AGENTS.md").mkdir()
    before = snapshot_tree(tmp_path)
    result = run_installer(
        homes[0],
        "--agent",
        "all",
        env_updates={
            "CALIBRATION_GROK_HOME": str(homes[1]),
            "PI_CODING_AGENT_DIR": str(homes[2]),
        },
    )
    assert result.returncode != 0
    assert snapshot_tree(tmp_path) == before


@pytest.mark.parametrize(
    "args",
    [
        ("--skills-only",),
        ("--instructions-only",),
        ("--profile", "standard"),
        ("--profile", "ao-worker"),
        ("--unknown",),
        ("--agent",),
        ("--agent", "other"),
        ("--pi-home", "/unused"),
        ("--codex-home", "/unused"),
        ("--grok-home", "/unused"),
        ("--no-backup",),
    ],
)
def test_invalid_or_retired_options_fail_without_writes(
    tmp_path: Path, args: tuple[str, ...]
) -> None:
    before = snapshot_tree(tmp_path)
    assert run_installer(tmp_path / "codex", *args).returncode != 0
    assert snapshot_tree(tmp_path) == before


def test_missing_homes_and_relative_xdg_fail(tmp_path: Path) -> None:
    result = run_installer(
        None, "--agent", "pi", unset_env=("HOME", "PI_CODING_AGENT_DIR")
    )
    assert result.returncode != 0
    assert (
        run_installer(
            tmp_path / "codex", env_updates={"XDG_CONFIG_HOME": "relative"}
        ).returncode
        != 0
    )
    assert not (tmp_path / "codex").exists()


@pytest.mark.parametrize("agent", AGENTS)
def test_environment_home_overrides_default(tmp_path: Path, agent: str) -> None:
    home = tmp_path / "custom" / agent
    result = install(home, agent)
    assert result.returncode == 0, result.stderr
    assert (home / "AGENTS.md").is_file()
    assert not (tmp_path / "user").exists()


@pytest.mark.parametrize("agent", AGENTS)
@pytest.mark.parametrize("value", ["relative", "/"])
def test_invalid_environment_home_fails(tmp_path: Path, agent: str, value: str) -> None:
    before = snapshot_tree(tmp_path)
    result = run_installer(
        None, "--agent", agent, env_updates={HOME_VARIABLES[agent]: value}
    )
    assert result.returncode != 0
    assert snapshot_tree(tmp_path) == before


def test_path_safety_and_overlapping_homes(tmp_path: Path) -> None:
    for home in (REPOSITORY_ROOT, REPOSITORY_ROOT / "unsafe", REPOSITORY_ROOT.parent):
        assert install(home, "codex").returncode != 0
    home = tmp_path / "same"
    assert (
        run_installer(
            home,
            "--agent",
            "codex",
            "pi",
            env_updates={"PI_CODING_AGENT_DIR": str(home / "nested")},
        ).returncode
        != 0
    )
    assert not home.exists()


def test_dry_run_and_paths_with_special_characters(tmp_path: Path) -> None:
    home = tmp_path / "space & back\\slash"
    before = snapshot_tree(tmp_path)
    assert install(home, "pi", "--dry-run").returncode == 0
    assert snapshot_tree(tmp_path) == before
    result = run_installer(
        None,
        "--agent",
        "pi",
        env_updates={
            "PI_CODING_AGENT_DIR": str(home),
            "XDG_CONFIG_HOME": str(home / "config"),
        },
    )
    assert result.returncode == 0, result.stderr
    assert (
        str(home / "config/calibration/AGENTS.md") in (home / "AGENTS.md").read_text()
    )


def test_install_never_touches_skill_paths(tmp_path: Path) -> None:
    home = tmp_path / "codex"
    home.mkdir()
    (home / "skills").write_text("Even a conflicting skills path is irrelevant.")
    assert install(home, "codex").returncode == 0
    assert (
        home / "skills"
    ).read_text() == "Even a conflicting skills path is irrelevant."


def test_backup_failure_preserves_original(tmp_path: Path) -> None:
    home = tmp_path / "codex"
    home.mkdir()
    target = home / "AGENTS.md"
    target.write_text("personal")
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    cp = bin_dir / "cp"
    cp.write_text("#!/bin/sh\nexit 42\n")
    cp.chmod(0o755)
    result = run_installer(
        home, "--force", env_updates={"PATH": f"{bin_dir}:{os.environ['PATH']}"}
    )
    assert result.returncode == 42
    assert target.read_text() == "personal"
    assert not list(home.glob(".calibration-AGENTS.*"))


@pytest.mark.parametrize("agent", AGENTS)
def test_cleanup_removes_only_exact_owned_links(tmp_path: Path, agent: str) -> None:
    home = tmp_path / agent
    skills = home / "skills"
    skills.mkdir(parents=True)
    (home / "AGENTS.md").write_text("personal")
    owned = {
        "calibration": "skills",
        "teach": "thirdparty/skills",
        "grilling": "thirdparty/archive",
        "coding-protocol": "thirdparty/skills",
        "global-defaults": "skills",
    }
    for name, parent in owned.items():
        (skills / name).symlink_to(REPOSITORY_ROOT / parent / name)
    foreign = tmp_path / "foreign"
    foreign.mkdir()
    (skills / "closeout").symlink_to(foreign)
    (skills / "retrospect").mkdir()
    (skills / "retrospect/personal.txt").write_text("keep")
    (skills / "writing-code-docs").write_text("keep")
    shared = tmp_path / "user/.agents/skills/grilling"
    shared.mkdir(parents=True)
    (shared / "SKILL.md").write_text("upstream")
    before = snapshot_tree(tmp_path)
    assert cleanup(home, agent, "--dry-run").returncode == 0
    assert snapshot_tree(tmp_path) == before
    result = cleanup(home, agent)
    assert result.returncode == 0, result.stderr
    assert all(not (skills / name).is_symlink() for name in owned)
    assert (skills / "closeout").readlink() == foreign
    assert (skills / "retrospect/personal.txt").read_text() == "keep"
    assert (skills / "writing-code-docs").read_text() == "keep"
    assert (shared / "SKILL.md").read_text() == "upstream"
    assert (home / "AGENTS.md").read_text() == "personal"
    assert (REPOSITORY_ROOT / "skills/calibration/SKILL.md").is_file()
    after = snapshot_tree(tmp_path)
    assert cleanup(home, agent).returncode == 0
    assert snapshot_tree(tmp_path) == after


def test_cleanup_refuses_symlinked_root_and_force(tmp_path: Path) -> None:
    home = tmp_path / "pi"
    home.mkdir()
    foreign = tmp_path / "foreign"
    foreign.mkdir()
    (home / "skills").symlink_to(foreign)
    before = snapshot_tree(tmp_path)
    assert cleanup(home, "pi").returncode != 0
    assert cleanup(home, "pi", "--force").returncode != 0
    assert snapshot_tree(tmp_path) == before


@pytest.mark.parametrize("agent", AGENTS)
def test_block_preserves_suffix_without_final_newline(
    tmp_path: Path, agent: str
) -> None:
    home = tmp_path / agent
    home.mkdir()
    target = home / "AGENTS.md"
    target.write_bytes(f"prefix\r\n{BEGIN}\nold\n{END}\nsuffix\r\nlast".encode())
    assert install(home, agent).returncode == 0
    assert target.read_bytes().startswith(b"prefix\r\n")
    assert target.read_bytes().endswith(b"suffix\r\nlast")
    before = snapshot_tree(home)
    assert install(home, agent).returncode == 0
    assert snapshot_tree(home) == before


@pytest.mark.parametrize("agent", AGENTS)
@pytest.mark.parametrize("empty", [False, True])
def test_default_homes_when_override_unset_or_empty(
    tmp_path: Path, agent: str, empty: bool
) -> None:
    env = {HOME_VARIABLES[agent]: ""} if empty else {}
    result = run_installer(None, "--agent", agent, env_updates=env)
    assert result.returncode == 0, result.stderr
    suffix = {"codex": ".codex", "grok": ".grok", "pi": ".pi/agent"}[agent]
    assert (tmp_path / "user" / suffix / "AGENTS.md").is_file()


def test_bash_invocation_from_another_directory(tmp_path: Path) -> None:
    before = snapshot_tree(tmp_path)
    result = subprocess.run(
        ["bash", str(REPOSITORY_ROOT / "install.sh"), "--agent", "all", "--dry-run"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert snapshot_tree(tmp_path) == before


@pytest.mark.parametrize(
    "option", ["--no-backup", "--codex-home", "--grok-home", "--pi-home"]
)
def test_cleanup_rejects_removed_options_without_writes(
    tmp_path: Path, option: str
) -> None:
    before = snapshot_tree(tmp_path)
    assert cleanup(tmp_path / "pi", "pi", option).returncode != 0
    assert snapshot_tree(tmp_path) == before


def test_first_party_skills_are_portable_copies(tmp_path: Path) -> None:
    for name in FIRST_PARTY:
        target = tmp_path / name
        shutil.copytree(REPOSITORY_ROOT / "skills" / name, target)
        errors: list[str] = []
        _validate_active_references([target], errors)
        assert errors == []


@pytest.mark.parametrize("agent", AGENTS)
@pytest.mark.parametrize("suffix", [b"", b"personal\r\nlast line"])
def test_legacy_markers_migrate_without_force_and_preserve_external_bytes(
    tmp_path: Path, agent: str, suffix: bytes
) -> None:
    home = tmp_path / agent
    home.mkdir()
    target = home / "AGENTS.md"
    original = (
        b"personal prefix\r\n\r\n"
        + f"{LEGACY_BEGIN}\nold body\n{LEGACY_END}\n".encode()
        + suffix
    )
    target.write_bytes(original)
    target.chmod(0o640)
    before = snapshot_tree(home)
    preview = install(home, agent, "--dry-run")
    assert preview.returncode == 0, preview.stderr
    assert "calibration" in preview.stdout and "FuqingZh/skills" in preview.stdout
    assert snapshot_tree(home) == before

    result = install(home, agent)
    assert result.returncode == 0, result.stderr
    rendered = target.read_bytes()
    assert rendered.startswith(b"personal prefix\r\n\r\n" + BEGIN.encode())
    assert rendered.endswith(END.encode() + b"\n" + suffix)
    assert LEGACY_BEGIN.encode() not in rendered
    assert LEGACY_END.encode() not in rendered
    assert rendered.count(BEGIN.encode()) == rendered.count(END.encode()) == 1
    assert target.stat().st_mode & 0o777 == 0o640
    assert [p.read_bytes() for p in home.glob("AGENTS.md.bak.*")] == [original]
    after = snapshot_tree(home)
    assert install(home, agent).returncode == 0
    assert snapshot_tree(home) == after


@pytest.mark.parametrize("agent", AGENTS)
@pytest.mark.parametrize("force", [(), ("--force",)])
@pytest.mark.parametrize(
    "text",
    [
        f"{LEGACY_BEGIN}\n{LEGACY_END}\n{BEGIN}\n{END}\n",
        f"{BEGIN}\n{END}\n{LEGACY_BEGIN}\n{LEGACY_END}\n",
        f"{LEGACY_BEGIN}\n{END}\n",
        f"{BEGIN}\n{LEGACY_END}\n",
        f"{LEGACY_BEGIN}\n{BEGIN}\n{LEGACY_END}\n{END}\n",
        f"{LEGACY_BEGIN}\n{LEGACY_END}\n{LEGACY_BEGIN}\n{LEGACY_END}\n",
        f"{LEGACY_BEGIN}\nunclosed\n",
        f"{LEGACY_END}\n",
        f"prefix {BEGIN}\n",
        "<!-- FuqingZh/skills:unknown -->\n",
    ],
)
def test_mixed_or_malformed_migration_markers_never_write(
    tmp_path: Path, agent: str, force: tuple[str, ...], text: str
) -> None:
    home = tmp_path / agent
    home.mkdir()
    (home / "AGENTS.md").write_text(text)
    before = snapshot_tree(home)
    assert install(home, agent, *force, "--dry-run").returncode != 0
    assert install(home, agent, *force).returncode != 0
    assert snapshot_tree(home) == before


def test_invalid_migration_in_last_agent_prevents_all_migrations(
    tmp_path: Path,
) -> None:
    homes = {agent: tmp_path / agent for agent in AGENTS}
    for home in homes.values():
        home.mkdir()
        (home / "AGENTS.md").write_text(f"{LEGACY_BEGIN}\nold\n{LEGACY_END}\n")
    (homes["pi"] / "AGENTS.md").write_text(f"{LEGACY_BEGIN}\n{END}\n")
    before = snapshot_tree(tmp_path)
    result = run_installer(
        homes["codex"],
        "--agent",
        "all",
        "--force",
        env_updates={HOME_VARIABLES[agent]: str(home) for agent, home in homes.items()},
    )
    assert result.returncode != 0
    assert snapshot_tree(tmp_path) == before
