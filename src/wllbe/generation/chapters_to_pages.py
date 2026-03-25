from __future__ import annotations

from typing import Any

from wllbe.domain.outlines import Page, PageOutline
from wllbe.generation.provider import GenerationProvider


def generate_page_outline(approved_chapters: dict[str, Any], provider: GenerationProvider) -> PageOutline:
    approved_ids = _collect_approved_chapter_ids(approved_chapters)
    payload = provider.generate_json("chapters_to_pages", approved_chapters)
    return _parse_page_outline(payload, approved_ids)


def _parse_page_outline(payload: dict[str, Any], approved_ids: set[str]) -> PageOutline:
    if "pages" not in payload:
        raise ValueError("page outline payload missing required 'pages' field")
    pages_payload = payload["pages"]
    if not isinstance(pages_payload, list):
        raise ValueError("page outline payload 'pages' must be a list")

    pages = [_parse_page(page_payload, approved_ids) for page_payload in pages_payload]
    return PageOutline(pages=pages)


def _parse_page(page_payload: Any, approved_ids: set[str]) -> Page:
    if not isinstance(page_payload, dict):
        raise ValueError("page payload must be an object")

    page_id = _ensure_id("page_id", _require_field(page_payload, "page_id"))
    chapter_id = _ensure_id("chapter_id", _require_field(page_payload, "chapter_id"))
    title = _ensure_string("title", _require_field(page_payload, "title"))
    message = _ensure_string("message", _require_field(page_payload, "message"))

    content_blocks_payload = page_payload.get("content_blocks", [])
    layout_hints_payload = page_payload.get("layout_hints", [])

    if not isinstance(content_blocks_payload, list):
        raise ValueError("page content_blocks must be a list")
    if not isinstance(layout_hints_payload, list):
        raise ValueError("page layout_hints must be a list")

    if chapter_id not in approved_ids:
        raise ValueError(f"page chapter_id '{chapter_id}' is not in approved chapters")

    return Page(
        page_id=page_id,
        chapter_id=chapter_id,
        title=title,
        message=message,
        content_blocks=content_blocks_payload,
        layout_hints=layout_hints_payload,
    )


def _collect_approved_chapter_ids(approved_chapters: dict[str, Any]) -> set[str]:
    chapters_payload = approved_chapters.get("chapters", [])
    if not isinstance(chapters_payload, list):
        return set()

    approved_ids: set[str] = set()
    for chapter in chapters_payload:
        if not isinstance(chapter, dict):
            continue
        chapter_id = chapter.get("chapter_id")
        if not isinstance(chapter_id, str):
            continue
        trimmed = chapter_id.strip()
        if trimmed:
            approved_ids.add(trimmed)
    return approved_ids


def _require_field(payload: dict[str, Any], field_name: str) -> Any:
    if field_name not in payload:
        raise ValueError(f"page payload missing required '{field_name}' field")
    return payload[field_name]


def _ensure_string(field_name: str, value: Any) -> str:
    if not isinstance(value, str):
        raise ValueError(f"{field_name} must be a string")
    return value


def _ensure_id(field_name: str, value: Any) -> str:
    value = _ensure_string(field_name, value)
    trimmed = value.strip()
    if not trimmed:
        raise ValueError(f"{field_name} must not be empty")
    return trimmed
