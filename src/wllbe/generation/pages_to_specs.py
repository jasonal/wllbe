from __future__ import annotations

from typing import Any

from wllbe.domain.slide_specs import SlideSpec


def build_slide_specs(page_outline: dict[str, Any]) -> list[SlideSpec]:
    if not isinstance(page_outline, dict):
        raise ValueError("page outline must be an object")

    pages = _extract_pages(page_outline)
    specs: list[SlideSpec] = []

    for sequence, page_payload in enumerate(pages, start=1):
        page = _ensure_page_payload(page_payload)
        layout_hints = _ensure_layout_hints(page)
        specs.append(
            SlideSpec(
                slide_id=_ensure_id("page_id", _require_field(page, "page_id")),
                chapter_id=_ensure_id("chapter_id", _require_field(page, "chapter_id")),
                sequence=sequence,
                slide_purpose=_infer_slide_purpose(layout_hints),
                content_blocks=_ensure_content_blocks(page),
                priority_metadata={"message": "primary"},
                density_metadata={"target": "medium"},
                visual_intent_tags=[],
                hard_constraints={},
                deterministic_layout_override=_find_required_override(layout_hints),
            )
        )

    return specs


def _extract_pages(page_outline: dict[str, Any]) -> list[Any]:
    if "pages" not in page_outline:
        raise ValueError("page outline payload missing required 'pages' field")

    pages_payload = page_outline["pages"]
    if not isinstance(pages_payload, list):
        raise ValueError("page outline 'pages' must be a list")

    return pages_payload


def _ensure_page_payload(payload: Any) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise ValueError("page payload must be an object")
    return payload


def _require_field(payload: dict[str, Any], field_name: str) -> Any:
    if field_name not in payload:
        raise ValueError(f"page payload missing required '{field_name}' field")
    return payload[field_name]


def _ensure_id(field_name: str, value: Any) -> str:
    value = _ensure_string(field_name, value)
    trimmed = value.strip()
    if not trimmed:
        raise ValueError(f"{field_name} must not be empty")
    return trimmed


def _ensure_string(field_name: str, value: Any) -> str:
    if not isinstance(value, str):
        raise ValueError(f"{field_name} must be a string")
    return value


def _ensure_content_blocks(page: dict[str, Any]) -> list[Any]:
    content_blocks = page.get("content_blocks", [])
    if not isinstance(content_blocks, list):
        raise ValueError("page content_blocks must be a list")
    return content_blocks


def _ensure_layout_hints(page: dict[str, Any]) -> list[Any]:
    layout_hints = page.get("layout_hints", [])
    if not isinstance(layout_hints, list):
        raise ValueError("page layout_hints must be a list")
    return layout_hints


def _infer_slide_purpose(layout_hints: list[Any]) -> str:
    for hint in layout_hints:
        if isinstance(hint, str):
            trimmed = hint.strip()
            if trimmed:
                return trimmed
    return "section"


def _find_required_override(layout_hints: list[Any]) -> str | None:
    for hint in layout_hints:
        if not isinstance(hint, dict):
            continue
        layout_code = hint.get("layout_code")
        strength = hint.get("strength")
        if (
            isinstance(layout_code, str)
            and layout_code.strip()
            and isinstance(strength, str)
            and strength.lower() == "required"
        ):
            return layout_code.strip()
    return None
