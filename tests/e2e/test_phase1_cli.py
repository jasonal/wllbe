from __future__ import annotations

import json
from pathlib import Path

from wllbe.cli import main


def test_phase1_cli_generates_bundle_from_fixture(tmp_path: Path) -> None:
    repo_root = Path(__file__).resolve().parents[2]
    project_dir = tmp_path / "runs" / "launch"

    exit_code = main(
        [
            "phase1-run",
            "--brief-file",
            str(repo_root / "tests" / "fixtures" / "briefs" / "product-launch.md"),
            "--project-dir",
            str(project_dir),
            "--provider",
            "fake",
            "--approved-chapters",
            str(repo_root / "tests" / "fixtures" / "projects" / "approved_chapters.json"),
            "--approved-pages",
            str(repo_root / "tests" / "fixtures" / "projects" / "approved_pages.json"),
        ]
    )

    assert exit_code == 0
    assert (project_dir / "brief.md").exists()
    assert (project_dir / "brief.normalized.json").exists()
    assert (project_dir / "chapter-outline.generated.json").exists()
    assert (project_dir / "chapter-outline.approved.json").exists()
    assert (project_dir / "page-outline.generated.json").exists()
    assert (project_dir / "page-outline.approved.json").exists()
    assert (project_dir / "slide-specs.json").exists()
    assert (project_dir / "plan.json").exists()
    assert (project_dir / "bundle" / "manifest.json").exists()
    assert (project_dir / "versions" / "version-a" / "index.html").exists()
    assert (project_dir / "versions" / "version-b" / "index.html").exists()
    assert (project_dir / "validation.json").exists()

    slide_specs = json.loads((project_dir / "slide-specs.json").read_text(encoding="utf-8"))
    assert slide_specs[0]["slide_purpose"] == "comparison"
    assert slide_specs[0]["deterministic_layout_override"] == "CMP-01"

    validation = json.loads((project_dir / "validation.json").read_text(encoding="utf-8"))
    assert validation["status"] == "passed"

    plan = json.loads((project_dir / "plan.json").read_text(encoding="utf-8"))
    assert [version["version_id"] for version in plan["versions"]] == [
        "version-a",
        "version-b",
    ]

    manifest = json.loads(
        (project_dir / "bundle" / "manifest.json").read_text(encoding="utf-8")
    )
    assert manifest["validation"]["status"] == "passed"
    assert manifest["selected_layouts"][0]["layout_code"] == "CMP-01"
    assert manifest["selected_style_packs"]["version-a"]["style_pack_id"] == "dark-tech"
    assert manifest["selected_style_packs"]["version-b"]["style_pack_id"] == "clean-light"
