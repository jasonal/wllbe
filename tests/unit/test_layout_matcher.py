from pathlib import Path

import pytest

from wllbe.domain.slide_specs import SlideSpec
from wllbe.layout.catalog import LayoutRecord, load_layout_catalog
from wllbe.layout.matcher import choose_layout


def _load_catalog() -> list[LayoutRecord]:
    catalog_dir = Path(__file__).resolve().parents[2] / "catalog" / "layouts"
    return load_layout_catalog(catalog_dir)


@pytest.fixture
def comparison_spec() -> SlideSpec:
    return SlideSpec(
        slide_id="s1",
        chapter_id="c1",
        sequence=1,
        slide_purpose="comparison",
        content_blocks=[{"type": "bullets", "items": ["Speed", "Trust"]}],
        priority_metadata={"message": "primary"},
        density_metadata={"target": "medium"},
        visual_intent_tags=[],
        hard_constraints={},
        deterministic_layout_override=None,
    )


def _mock_comparison_layouts() -> list[LayoutRecord]:
    return [
        LayoutRecord(
            layout_id="comparison.focus",
            layout_code="CMP-01",
            layout_label="Comparison two column",
            layout_family="comparison",
            supported_purposes=["comparison"],
            slot_schema=["heading", "bullets"],
            capacity_rules={"bullets_max": 4},
            visual_rhythm_tags=["balanced"],
            style_compatibility=["clean-light", "dark-tech"],
            status="production",
        ),
        LayoutRecord(
            layout_id="comparison.expanded",
            layout_code="CMP-02",
            layout_label="Comparison expanded",
            layout_family="comparison",
            supported_purposes=["comparison"],
            slot_schema=["heading", "bullets"],
            capacity_rules={"bullets_max": 8},
            visual_rhythm_tags=["balanced"],
            style_compatibility=["clean-light"],
            status="production",
        ),
    ]


def test_choose_layout_respects_override(comparison_spec):
    layouts = _load_catalog()
    comparison_spec.deterministic_layout_override = "CMP-01"
    chosen = choose_layout(comparison_spec, layouts, recipe_rules={})
    assert chosen.layout_code == "CMP-01"


def test_choose_layout_errors_on_unknown_override(comparison_spec):
    layouts = _mock_comparison_layouts()
    comparison_spec.deterministic_layout_override = "COV-01"
    with pytest.raises(ValueError, match="Unknown layout override 'COV-01'"):
        choose_layout(comparison_spec, layouts, recipe_rules={})


def test_choose_layout_errors_on_known_incompatible_override(comparison_spec):
    layouts = _mock_comparison_layouts()
    comparison_spec.content_blocks = [
        {"type": "bullets", "items": list("abcdef")},
    ]
    comparison_spec.deterministic_layout_override = "CMP-01"
    with pytest.raises(ValueError, match="incompatible"):
        choose_layout(comparison_spec, layouts, recipe_rules={})


def test_choose_layout_errors_on_empty_override(comparison_spec):
    layouts = _mock_comparison_layouts()
    comparison_spec.deterministic_layout_override = ""
    with pytest.raises(ValueError, match="deterministic layout override"):
        choose_layout(comparison_spec, layouts, recipe_rules={})


def test_recipe_preference_trumps_ranking(comparison_spec):
    layouts = _mock_comparison_layouts()
    recipe_rules = {"preferred_layout_codes": {"comparison": ["CMP-02"]}}
    chosen = choose_layout(comparison_spec, layouts, recipe_rules=recipe_rules)
    assert chosen.layout_code == "CMP-02"


def test_capacity_filters_overfull_layout(comparison_spec):
    comparison_spec.content_blocks = [
        {"type": "bullets", "items": ["a", "b", "c", "d", "e", "f"]}
    ]
    layouts = _mock_comparison_layouts()
    chosen = choose_layout(comparison_spec, layouts, recipe_rules={})
    assert chosen.layout_code == "CMP-02"


def test_ranking_fallback_is_deterministic(comparison_spec):
    layouts = _mock_comparison_layouts()
    layouts.append(
        LayoutRecord(
            layout_id="comparison.alt",
            layout_code="CMP-03",
            layout_label="Comparison alternate",
            layout_family="comparison",
            supported_purposes=["comparison"],
            slot_schema=["heading", "bullets"],
            capacity_rules={"bullets_max": 8},
            visual_rhythm_tags=["balanced"],
            style_compatibility=["clean-light"],
            status="production",
        )
    )
    chosen = choose_layout(comparison_spec, layouts, recipe_rules={})
    assert chosen.layout_code == "CMP-01"
