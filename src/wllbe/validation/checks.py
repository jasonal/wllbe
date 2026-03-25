from __future__ import annotations

from pathlib import Path
from typing import Any, Iterable

from wllbe.validation.report import ValidationIssue, ValidationReport, write_validation_report

VALIDATION_CATEGORIES = ("content", "layout", "rendering", "versioning")


def check_content_structure(slide_specs: Iterable[dict[str, Any]]) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    for spec in slide_specs:
        slide_id = spec.get("slide_id")
        if not slide_id:
            issues.append(
                ValidationIssue(
                    category="content",
                    message="Slide is missing slide_id",
                )
            )
        if not spec.get("slide_purpose"):
            issues.append(
                ValidationIssue(
                    category="content",
                    message="Slide is missing slide_purpose",
                    slide_id=slide_id,
                )
            )
    return issues


def check_layout_choices(
    slide_specs: Iterable[dict[str, Any]],
    chosen_layouts: Iterable[dict[str, Any]],
) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    layout_map = {
        layout.get("slide_id"): layout
        for layout in chosen_layouts
        if layout.get("slide_id")
    }

    for spec in slide_specs:
        slide_id = spec.get("slide_id")
        override = spec.get("deterministic_layout_override")
        if not slide_id or not override:
            continue
        chosen = layout_map.get(slide_id)
        if not chosen:
            continue
        if chosen.get("layout_code") != override:
            issues.append(
                ValidationIssue(
                    category="layout",
                    message=(
                        f"Slide {slide_id} override {override} conflicts with "
                        f"chosen layout {chosen.get('layout_code')}"
                    ),
                    slide_id=slide_id,
                )
            )
    return issues


def check_rendered_output(rendered_versions: dict[str, str]) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    for version_id, html in rendered_versions.items():
        if not isinstance(html, str) or not html.lstrip().startswith("<!DOCTYPE html>"):
            issues.append(
                ValidationIssue(
                    category="rendering",
                    message=f"Rendered version {version_id} is missing <!DOCTYPE html>",
                )
            )
    return issues


def check_version_differences(rendered_versions: dict[str, str]) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    if len(rendered_versions) < 1:
        issues.append(
            ValidationIssue(
                category="versioning",
                message="No rendered versions were generated",
            )
        )
        return issues

    if len(rendered_versions) > 1:
        unique = {
            html.encode("utf-8") if isinstance(html, str) else b""
            for html in rendered_versions.values()
        }
        if len(unique) <= 1:
            issues.append(
                ValidationIssue(
                    category="versioning",
                    message="Rendered versions are identical; expected variation",
                )
            )
    return issues


def validate_project(
    *,
    slide_specs: Iterable[dict[str, Any]],
    chosen_layouts: Iterable[dict[str, Any]],
    rendered_versions: dict[str, str],
    project_root: Path | str | None = None,
) -> ValidationReport:
    normalized_slide_specs = list(slide_specs)
    normalized_chosen_layouts = list(chosen_layouts)
    issues: list[ValidationIssue] = []
    issues.extend(check_content_structure(normalized_slide_specs))
    issues.extend(check_layout_choices(normalized_slide_specs, normalized_chosen_layouts))
    issues.extend(check_rendered_output(rendered_versions))
    issues.extend(check_version_differences(rendered_versions))

    report = ValidationReport.from_issues(issues)
    if project_root is not None:
        write_validation_report(Path(project_root), report)
    return report
