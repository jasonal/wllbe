from __future__ import annotations

import json
from pathlib import Path

from wllbe.validation.checks import validate_project


def _base_slide_spec(**overrides: object) -> dict[str, object]:
    base = {
        "slide_id": "s1",
        "slide_purpose": "comparison",
        "deterministic_layout_override": "CMP-01",
    }
    base.update(overrides)
    return base


def _base_layout_choice(**overrides: object) -> dict[str, object]:
    base = {
        "slide_id": "s1",
        "layout_code": "CMP-01",
        "layout_family": "comparison",
    }
    base.update(overrides)
    return base


def _rendered_versions(*versions: str) -> dict[str, str]:
    return {
        f"version-{idx}": version
        for idx, version in enumerate(versions, start=1)
    }


def test_validate_project_flags_incompatible_override():
    report = validate_project(
        slide_specs=[
            _base_slide_spec(deterministic_layout_override="CMP-99"),
        ],
        chosen_layouts=[_base_layout_choice(layout_code="CMP-01")],
        rendered_versions=_rendered_versions(
            "<!DOCTYPE html><html><body>ok</body></html>",
        ),
    )

    assert report.status == "failed"
    assert report.issues
    assert report.issues[0].category == "layout"


def test_validate_project_passes_with_valid_project(tmp_path: Path):
    report = validate_project(
        slide_specs=[_base_slide_spec()],
        chosen_layouts=[_base_layout_choice()],
        rendered_versions=_rendered_versions(
            "<!DOCTYPE html><html>alpha</html>",
            "<!DOCTYPE html><html>beta</html>",
        ),
        project_root=tmp_path,
    )

    assert report.status == "passed"
    assert not report.issues
    validation_path = tmp_path / "validation.json"
    assert validation_path.exists()
    assert json.loads(validation_path.read_text(encoding="utf-8"))["status"] == "passed"


def test_validate_project_detects_rendering_issue():
    report = validate_project(
        slide_specs=[_base_slide_spec()],
        chosen_layouts=[_base_layout_choice()],
        rendered_versions=_rendered_versions(
            "<html><body>missing doctype</body></html>",
        ),
    )

    assert any(issue.category == "rendering" for issue in report.issues)


def test_validate_project_detects_versioning_issue_for_identical_versions():
    report = validate_project(
        slide_specs=[_base_slide_spec()],
        chosen_layouts=[_base_layout_choice()],
        rendered_versions=_rendered_versions(
            "<!DOCTYPE html><html>same</html>",
            "<!DOCTYPE html><html>same</html>",
        ),
    )

    assert any(issue.category == "versioning" for issue in report.issues)
