from __future__ import annotations

import ipaddress
import re
import subprocess
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
PERSONAL_HOME_PATTERNS = (
    re.compile(rb"/(?:home|Users)/[A-Za-z0-9._-]+"),
    re.compile(rb"/root(?:/|(?=$))"),
    re.compile(rb"[A-Za-z]:[\\/]+Users[\\/]+[A-Za-z0-9._-]+"),
)
IPV4_CANDIDATE = re.compile(rb"(?<![0-9])(?:[0-9]{1,3}\.){3}[0-9]{1,3}(?![0-9])")
PRIVATE_DEPLOYMENT_NETWORKS = tuple(
    ipaddress.ip_network(network)
    for network in (
        "10." + "0.0.0/8",
        "172." + "16.0.0/12",
        "192." + "168.0.0/16",
    )
)
KNOWN_PRIVATE_TOKENS = (b"fq" + b"zhang",)


def tracked_text() -> dict[str, bytes]:
    result = subprocess.run(
        ["git", "ls-files", "-z"],
        cwd=REPOSITORY_ROOT,
        check=True,
        capture_output=True,
    )
    tracked: dict[str, bytes] = {}
    for raw_path in result.stdout.split(b"\0"):
        if not raw_path:
            continue
        relative = raw_path.decode()
        path = REPOSITORY_ROOT / relative
        if not path.is_file():
            continue
        tracked[relative] = path.read_bytes()
    return tracked


def private_values(content: bytes) -> set[bytes]:
    values = {token for token in KNOWN_PRIVATE_TOKENS if token in content}
    values.update(
        {
            match.group()
            for pattern in PERSONAL_HOME_PATTERNS
            for match in pattern.finditer(content)
        }
    )
    for match in IPV4_CANDIDATE.finditer(content):
        candidate = match.group()
        try:
            address = ipaddress.ip_address(candidate.decode())
        except ValueError:
            continue
        if any(address in network for network in PRIVATE_DEPLOYMENT_NETWORKS):
            values.add(candidate)
    return values


def portability_violations(tracked: dict[str, bytes]) -> list[str]:
    violations: list[str] = []
    for relative, content in tracked.items():
        values = private_values(relative.encode()) | private_values(content)
        unexpected = sorted(values)
        if unexpected:
            rendered = ", ".join(repr(value.decode()) for value in unexpected)
            violations.append(f"{relative}: {rendered}")
    return violations


def test_first_party_surfaces_have_no_personal_paths_or_private_ipv4() -> None:
    tracked = tracked_text()
    assert portability_violations(tracked) == []


def test_private_value_detection_is_structural() -> None:
    samples = (
        b"/ho" + b"me/alice/project",
        b"/Us" + b"ers/bob/project",
        b"/ro" + b"ot/project",
        b"C:\\Us" + b"ers\\carol\\project",
        b"10." + b"23.4.5",
        b"172." + b"31.4.5",
        b"192." + b"168.4.5",
    )
    for sample in samples:
        assert private_values(sample)


def test_known_private_username_is_denied_outside_home_paths() -> None:
    samples = (
        b"build-" + b"fq" + b"zhang.local",
        b"/tmp/" + b"fq" + b"zhang-cache",
    )
    for sample in samples:
        assert KNOWN_PRIVATE_TOKENS[0] in private_values(sample)


def test_binary_tracked_content_is_scanned_without_decoding() -> None:
    private_binary = b"\x89PNG\r\n\x1a\n\0host=" + b"fq" + b"zhang.local"
    tracked = {"assets/private.png": private_binary}

    expected = f"assets/private.png: {KNOWN_PRIVATE_TOKENS[0].decode()!r}"
    assert portability_violations(tracked) == [expected]
