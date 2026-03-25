from __future__ import annotations

import re
from typing import Any

from wllbe.domain.outlines import Chapter, ChapterOutline
from wllbe.generation.provider import GenerationProvider


def generate_chapter_outline(raw_brief: str, provider: GenerationProvider) -> ChapterOutline:
    payload = provider.generate_json("brief_to_chapters", {"brief": raw_brief})
    return _parse_chapter_outline(payload)


def _parse_chapter_outline(payload: dict[str, Any]) -> ChapterOutline:
    if "chapters" not in payload:
        raise ValueError("chapter outline payload missing required 'chapters' field")
    chapters_payload = payload["chapters"]
    if not isinstance(chapters_payload, list):
        raise ValueError("chapter outline payload 'chapters' must be a list")

    chapters = [_parse_chapter(chapter_payload) for chapter_payload in chapters_payload]
    goal = _normalize_optional_text(payload.get("goal"))
    audience = _normalize_optional_text(payload.get("audience"))
    tone = _normalize_optional_text(payload.get("tone"))
    return ChapterOutline(chapters=chapters, goal=goal, audience=audience, tone=tone)


def _parse_chapter(chapter_payload: Any) -> Chapter:
    if not isinstance(chapter_payload, dict):
        raise ValueError("chapter payload must be an object")

    key_points_payload = chapter_payload.get("key_points", [])
    if not isinstance(key_points_payload, list):
        raise ValueError("chapter key_points must be a list")

    return Chapter(
        chapter_id=_normalize_text(chapter_payload["chapter_id"]),
        title=_normalize_text(chapter_payload["title"]),
        intent=_normalize_text(chapter_payload["intent"]),
        key_points=[_normalize_text(point) for point in key_points_payload],
        estimated_pages=_normalize_estimated_pages(chapter_payload.get("estimated_pages", 1)),
    )


def _normalize_optional_text(value: Any) -> str | None:
    if value is None:
        return None
    return _normalize_text(value)


def _normalize_text(value: Any) -> str:
    if not isinstance(value, str):
        raise ValueError("text field must be a string")
    return " ".join(value.split())


def _normalize_estimated_pages(value: Any) -> int:
    if isinstance(value, bool):
        raise ValueError("estimated_pages must be an integer or numeric string")
    if isinstance(value, int):
        if value < 1:
            raise ValueError("estimated_pages must be >= 1")
        return value
    if isinstance(value, str):
        match = re.search(r"\d+", value)
        if match is None:
            raise ValueError("estimated_pages string must include a number")
        parsed = int(match.group(0))
        if parsed < 1:
            raise ValueError("estimated_pages must be >= 1")
        return parsed
    raise ValueError("estimated_pages must be an integer or numeric string")
