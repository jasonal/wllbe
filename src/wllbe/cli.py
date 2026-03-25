from __future__ import annotations

import json
import sys
from dataclasses import asdict, dataclass
from html import escape
from pathlib import Path
from typing import Any

from wllbe.domain.brief import Brief
from wllbe.generation.brief_to_chapters import generate_chapter_outline
from wllbe.generation.chapters_to_pages import generate_page_outline
from wllbe.generation.pages_to_specs import build_slide_specs
from wllbe.generation.provider import FakeGenerationProvider
from wllbe.layout.catalog import load_layout_catalog
from wllbe.layout.matcher import choose_layout
from wllbe.projects.store import ProjectStore
from wllbe.render.bundle_writer import write_bundle
from wllbe.render.html_renderer import render_version
from wllbe.style.catalog import load_style_catalog
from wllbe.style.recipes import build_version_plan
from wllbe.validation.checks import validate_project


APPROVE_USAGE = "wllbe approve <chapters|pages> --project <path> --input <path>"
PHASE1_RUN_USAGE = (
    "wllbe phase1-run --brief-file <path> --project-dir <path> --provider fake "
    "--approved-chapters <path> --approved-pages <path>"
)
REPO_ROOT = Path(__file__).resolve().parents[2]
CATALOG_ROOT = REPO_ROOT / "catalog"
PROVIDER_FIXTURE_ROOT = REPO_ROOT / "tests" / "fixtures" / "providers"


@dataclass(slots=True)
class Phase1RunArgs:
    brief_file: Path
    project_dir: Path
    provider: str
    approved_chapters: Path
    approved_pages: Path


def _run_approve(argv: list[str]) -> int:
    if not argv:
        print(APPROVE_USAGE)
        return 1

    target = argv[0]
    artifact_name: str | None = None
    if target == "chapters":
        artifact_name = "chapter-outline"
    elif target == "pages":
        artifact_name = "page-outline"
    else:
        print(f"unknown approve target: {target}")
        return 2

    project: str | None = None
    input_path: str | None = None
    i = 1
    while i < len(argv):
        token = argv[i]
        if token == "--project" and i + 1 < len(argv):
            project = argv[i + 1]
            i += 2
            continue
        if token == "--input" and i + 1 < len(argv):
            input_path = argv[i + 1]
            i += 2
            continue
        print(APPROVE_USAGE)
        return 1

    if project is None or input_path is None:
        print(APPROVE_USAGE)
        return 1

    store = ProjectStore(Path(project))
    try:
        store.approve_artifact(artifact_name, Path(input_path))
    except (ValueError, OSError) as exc:
        print(f"approval failed: {exc}", file=sys.stderr)
        return 1

    return 0


def _run_phase1(argv: list[str]) -> int:
    args = _parse_phase1_args(argv)
    if args is None:
        print(PHASE1_RUN_USAGE)
        return 1

    try:
        _execute_phase1(args)
    except (ValueError, OSError) as exc:
        print(f"phase1-run failed: {exc}", file=sys.stderr)
        return 1

    return 0


def _parse_phase1_args(argv: list[str]) -> Phase1RunArgs | None:
    values: dict[str, str] = {}
    i = 0
    while i < len(argv):
        token = argv[i]
        if token in {
            "--brief-file",
            "--project-dir",
            "--provider",
            "--approved-chapters",
            "--approved-pages",
        } and i + 1 < len(argv):
            values[token] = argv[i + 1]
            i += 2
            continue
        return None

    required = {
        "--brief-file",
        "--project-dir",
        "--provider",
        "--approved-chapters",
        "--approved-pages",
    }
    if not required.issubset(values):
        return None

    return Phase1RunArgs(
        brief_file=Path(values["--brief-file"]),
        project_dir=Path(values["--project-dir"]),
        provider=values["--provider"],
        approved_chapters=Path(values["--approved-chapters"]),
        approved_pages=Path(values["--approved-pages"]),
    )


def _execute_phase1(args: Phase1RunArgs) -> None:
    raw_brief = args.brief_file.read_text(encoding="utf-8")
    brief = _normalize_brief(raw_brief)
    store = ProjectStore(args.project_dir)
    store.write_brief(brief, raw_brief)

    provider = _load_provider(args.provider)

    chapter_outline = generate_chapter_outline(raw_brief, provider)
    store.write_json(store.chapter_outline_generated_path.name, asdict(chapter_outline))
    store.approve_artifact("chapter-outline", args.approved_chapters)
    approved_chapters = store.read_json(store.chapter_outline_approved_path.name)

    page_outline = generate_page_outline(approved_chapters, provider)
    store.write_json(store.page_outline_generated_path.name, asdict(page_outline))
    store.approve_artifact("page-outline", args.approved_pages)
    approved_pages = store.read_json(store.page_outline_approved_path.name)

    slide_specs = build_slide_specs(approved_pages)
    slide_spec_payload = [asdict(spec) for spec in slide_specs]
    store.write_json(store.slide_specs_path.name, slide_spec_payload)

    layout_catalog = load_layout_catalog(CATALOG_ROOT / "layouts")
    chosen_layouts = [_choose_layout_payload(spec, layout_catalog) for spec in slide_specs]

    version_plan = build_version_plan(2)
    style_catalog = load_style_catalog(CATALOG_ROOT / "styles")
    style_map = {style.style_pack_id: asdict(style) for style in style_catalog}
    rendered_versions = {
        version.version_id: render_version(
            version.version_id,
            _build_rendered_slides(
                slide_spec_payload=slide_spec_payload,
                approved_pages=approved_pages,
                chosen_layouts=chosen_layouts,
                recipe_id=version.recipe_id,
            ),
            style_map[version.style_pack_id],
        )
        for version in version_plan
    }

    report = validate_project(
        slide_specs=slide_spec_payload,
        chosen_layouts=chosen_layouts,
        rendered_versions=rendered_versions,
        project_root=store.root,
    )

    manifest = {
        "approved_artifacts": {
            "chapters": store.chapter_outline_approved_path.name,
            "pages": store.page_outline_approved_path.name,
            "slide_specs": store.slide_specs_path.name,
        },
        "selected_layouts": chosen_layouts,
        "selected_style_packs": {
            version.version_id: style_map[version.style_pack_id]
            for version in version_plan
        },
        "versions": [
            {
                "version_id": version.version_id,
                "recipe_id": version.recipe_id,
                "style_pack_id": version.style_pack_id,
                "path": f"versions/{version.version_id}/index.html",
            }
            for version in version_plan
        ],
        "validation": report.to_dict(),
    }
    plan_payload = {
        "versions": [asdict(version) for version in version_plan],
    }
    write_bundle(store.root, manifest, plan_payload, rendered_versions)


def _normalize_brief(raw_text: str) -> Brief:
    goal = _extract_goal(raw_text)
    audience = ", ".join(_collect_list_section(raw_text, "Target audience:"))
    tone = ", ".join(_collect_list_section(raw_text, "Tone:"))
    constraints = _collect_list_section(raw_text, "Constraints:")
    source_materials = _collect_list_section(raw_text, "Source materials:")
    return Brief(
        goal=goal or "Untitled deck",
        audience=audience or "General audience",
        tone=tone or "Clear",
        constraints=constraints,
        page_budget=8,
        source_materials=source_materials,
    )


def _extract_goal(raw_text: str) -> str:
    for paragraph in raw_text.split("\n\n"):
        lines = [line.strip() for line in paragraph.splitlines() if line.strip()]
        if not lines:
            continue
        first = lines[0]
        if first.startswith("#"):
            continue
        if first.endswith(":"):
            continue
        return " ".join(lines)
    return ""


def _collect_list_section(raw_text: str, header: str) -> list[str]:
    items: list[str] = []
    collecting = False
    header_lower = header.lower()
    for raw_line in raw_text.splitlines():
        line = raw_line.strip()
        if not collecting:
            if line.lower() == header_lower:
                collecting = True
            continue

        if not line:
            if items:
                break
            continue
        if line.endswith(":") and not line.startswith("-"):
            break
        if not line.startswith("-"):
            break
        item = line[1:].strip()
        if item:
            items.append(item)
    return items


def _load_provider(provider_name: str) -> FakeGenerationProvider:
    if provider_name != "fake":
        raise ValueError(f"unsupported provider: {provider_name}")

    chapter_provider = FakeGenerationProvider.from_file(
        PROVIDER_FIXTURE_ROOT / "chapter_outline.json"
    )
    page_provider = FakeGenerationProvider.from_file(
        PROVIDER_FIXTURE_ROOT / "page_outline.json"
    )
    responses = dict(chapter_provider.responses)
    responses.update(page_provider.responses)
    return FakeGenerationProvider(responses=responses)


def _choose_layout_payload(
    spec: Any,
    layout_catalog: list[Any],
) -> dict[str, Any]:
    layout = choose_layout(spec, layout_catalog, {})
    payload = asdict(layout)
    payload["slide_id"] = spec.slide_id
    return payload


def _build_rendered_slides(
    *,
    slide_spec_payload: list[dict[str, Any]],
    approved_pages: dict[str, Any],
    chosen_layouts: list[dict[str, Any]],
    recipe_id: str,
) -> list[dict[str, str]]:
    page_lookup = _page_lookup(approved_pages)
    layout_lookup = {
        layout["slide_id"]: layout
        for layout in chosen_layouts
        if isinstance(layout.get("slide_id"), str)
    }

    slides: list[dict[str, str]] = []
    for spec in slide_spec_payload:
        slide_id = str(spec["slide_id"])
        page = page_lookup.get(slide_id, {})
        title = str(page.get("title", slide_id))
        message = str(page.get("message", ""))
        body_parts: list[str] = []
        if message:
            body_parts.append(f"    <p>{escape(message)}</p>")
        body_parts.extend(_render_content_blocks(page.get("content_blocks", [])))
        layout_code = layout_lookup.get(slide_id, {}).get("layout_code")
        if isinstance(layout_code, str) and layout_code:
            body_parts.append(f"    <p>Layout: {escape(layout_code)}</p>")
        body_parts.append(f"    <p>Recipe: {escape(recipe_id)}</p>")
        slides.append(
            {
                "slide_id": slide_id,
                "title": escape(title),
                "body_html": "\n".join(body_parts),
            }
        )
    return slides


def _page_lookup(approved_pages: dict[str, Any]) -> dict[str, dict[str, Any]]:
    pages_payload = approved_pages.get("pages", [])
    if not isinstance(pages_payload, list):
        raise ValueError("approved page outline must contain a pages list")

    pages: dict[str, dict[str, Any]] = {}
    for page in pages_payload:
        if not isinstance(page, dict):
            continue
        page_id = page.get("page_id")
        if isinstance(page_id, str) and page_id:
            pages[page_id] = page
    return pages


def _render_content_blocks(content_blocks: Any) -> list[str]:
    if not isinstance(content_blocks, list):
        return []

    rendered: list[str] = []
    for block in content_blocks:
        if not isinstance(block, dict):
            continue

        if block.get("type") == "bullets":
            items = block.get("items", [])
            if not isinstance(items, list):
                continue
            bullet_html = "".join(
                f"<li>{escape(str(item))}</li>"
                for item in items
            )
            rendered.append(f"    <ul>{bullet_html}</ul>")
            continue

        rendered.append(
            "    <pre>"
            + escape(json.dumps(block, sort_keys=True, ensure_ascii=False))
            + "</pre>"
        )
    return rendered


def main(argv: list[str] | None = None) -> int:
    argv = [] if argv is None else argv
    if not argv:
        print("wllbe <command>")
        return 1
    if argv[0] == "approve":
        return _run_approve(argv[1:])
    if argv[0] == "phase1-run":
        return _run_phase1(argv[1:])
    print(f"unknown command: {argv[0]}")
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
