from __future__ import annotations

from typing import Any

from wllbe.domain.outlines import Page, PageOutline
from wllbe.generation.provider import GenerationProvider


def generate_page_outline(approved_chapters: dict[str, Any], provider: GenerationProvider) -> PageOutline:
    payload = provider.generate_json("chapters_to_pages", approved_chapters)
    return _parse_page_outline(payload)


def _parse_page_outline(payload: dict[str, Any]) -> PageOutline:
    if "pages" not in payload:
        raise ValueError("page outline payload missing required 'pages' field")
    pages_payload = payload["pages"]
    if not isinstance(pages_payload, list):
        raise ValueError("page outline payload 'pages' must be a list")

    pages = [_parse_page(page_payload) for page_payload in pages_payload]
    return PageOutline(pages=pages)


def _parse_page(page_payload: Any) -> Page:
    if not isinstance(page_payload, dict):
        raise ValueError("page payload must be an object")

    page_id = _normalize_text(page_payload["page_id"])
    chapter_id = _normalize_text(page_payload["chapter_id"])
    title = _normalize_text(page_payload["title"])
    message = _normalize_text(page_payload["message"])

    content_blocks_payload = page_payload.get("content_blocks", [])
    layout_hints_payload = page_payload.get("layout_hints", [])

    if not isinstance(content_blocks_payload, list):
        raise ValueError("page content_blocks must be a list")
    if not isinstance(layout_hints_payload, list):
        raise ValueError("page layout_hints must be a list")

    return Page(
        page_id=page_id,
        chapter_id=chapter_id,
        title=title,
        message=message,
        content_blocks=content_blocks_payload,
        layout_hints=layout_hints_payload,
    )


def _normalize_text(value: Any) -> str:
    if not isinstance(value, str):
        raise ValueError("text field must be a string")
    return " ".join(value.split())
