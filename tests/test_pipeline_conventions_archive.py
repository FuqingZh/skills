from __future__ import annotations

import hashlib

from tests.support import REPOSITORY_ROOT

ARCHIVE = REPOSITORY_ROOT / "docs/archive/pipeline-conventions"
REFERENCES = REPOSITORY_ROOT / "skills/calibration/references"
SNAPSHOTS = {
    "identifier.md": "128ec173740fbb138430b3c76837952da0ef9de30f9170592601df55997a0951",
    "schema.md": "01bbffe40177b45b15c1139b9490c1d55c6b563c06691808794e429e1a692357",
    "artifact.md": "9271f9c95bd4599897bc6ca222bb2deaab9e66fd3290da809d12bd48a3d21c8f",
    "pipeline-directory-layout.md": (
        "05ac10c81137a145dddbd50e120504631ffe12f5b4cf7412947bf1800a22db9f"
    ),
    "step-to-step-artifact-flow.md": (
        "2475f6c4a96ef1e4b7d9d0ae95bfef874261968864d9910726b14f0da4c07068"
    ),
}


def test_retired_pipeline_snapshots_are_preserved() -> None:
    for name, digest in SNAPSHOTS.items():
        assert hashlib.sha256((ARCHIVE / name).read_bytes()).hexdigest() == digest


def test_retired_pipeline_paths_are_not_shipped_or_routed() -> None:
    retired = tuple(
        f"docs/schema/{directory}/20260304-v1.1.md"
        for directory in (
            "pipeline_directory_layout_specification",
            "step_to_step_artifact_flow_specification",
            "identifier",
        )
    )
    for target in retired:
        assert not (REFERENCES / target).exists()
    for path in REFERENCES.parent.rglob("*.md"):
        body = path.read_text(encoding="utf-8")
        for target in retired:
            assert target not in body, path


def test_archive_navigation_links_to_current_contracts() -> None:
    index = (ARCHIVE / "README.md").read_text(encoding="utf-8")
    for target in ("naming/schema.md", "discipline/refactor.md#judgment-checks"):
        assert f"](../../../skills/calibration/references/{target})" in index
        assert (REFERENCES / target.split("#", 1)[0]).is_file()
    assert "paths have been removed" in index
