from __future__ import annotations

from typing import Any

import pytest

from wllbe.generation.pages_to_specs import build_slide_specs


def _sample_page(page_id: str, chapter_id: str, **overrides: Any) -> dict[str, Any]:
    base: dict[str, Any] = {
        "page_id": page_id,
        "chapter_id": chapter_id,
        "content_blocks": [{"type": "bullets", "items": ["Speed", "Trust"]}],
        "layout_hints": [],
    }
    base.update(overrides)
    return base


def test_build_slide_specs_uses_layout_hint_for_slide_purpose():
    page_outline = {
        "pages": [
            _sample_page("p1", "c1", layout_hints=["comparison"]),
        ]
    }

    specs = build_slide_specs(page_outline)

    assert len(specs) == 1
    spec = specs[0]
    assert spec.slide_purpose == "comparison"
    assert spec.sequence == 1
    assert spec.priority_metadata == {"message": "primary"}
    assert spec.density_metadata == {"target": "medium"}
    assert "x" not in spec.content_blocks[0]
    assert spec.deterministic_layout_override is None


def test_build_slide_specs_sets_deterministic_override_from_required_hint():
    page_outline = {
        "pages": [
            _sample_page(
                "p2",
                "c2",
                layout_hints=[
                    {"layout_code": "CMP-01", "strength": "required"}
                ],
            ),
        ]
    }

    spec = build_slide_specs(page_outline)[0]

    assert spec.deterministic_layout_override == "CMP-01"
    assert spec.slide_purpose == "section"


def test_build_slide_specs_preserves_sequence_order_across_pages():
    page_outline = {
        "pages": [
            _sample_page("p1", "c1"),
            _sample_page("p2", "c1")
        ]
    }

    specs = build_slide_specs(page_outline)

    assert [spec.sequence for spec in specs] == [1, 2]


def test_build_slide_specs_raises_on_malformed_page():
    page_outline = {
        "pages": [
            {
                "chapter_id": "c1",
                "content_blocks": [],
                "layout_hints": [],
            }
        ]
    }

    with pytest.raises(ValueError, match="page payload missing required 'page_id' field"):
        build_slide_specs(page_outline)
