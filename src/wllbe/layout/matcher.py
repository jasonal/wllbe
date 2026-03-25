from __future__ import annotations

from typing import Any

from wllbe.domain.slide_specs import SlideSpec

from .catalog import LayoutRecord


def choose_layout(
    spec: SlideSpec,
    layouts: list[LayoutRecord],
    recipe_rules: dict[str, Any],
) -> LayoutRecord:
    if spec.deterministic_layout_override is not None:
        return require_compatible_override(spec, layouts, spec.deterministic_layout_override)

    compatible = compatible_layouts(spec, layouts)
    if not compatible:
        raise ValueError(f"No compatible layouts found for purpose '{spec.slide_purpose}'")

    ranked = rank_layouts(spec, compatible, recipe_rules)
    if not ranked:
        raise ValueError("No layouts available after ranking")

    return ranked[0]


def compatible_layouts(spec: SlideSpec, layouts: list[LayoutRecord]) -> list[LayoutRecord]:
    compatible: list[LayoutRecord] = []
    for layout in layouts:
        if layout.status != "production":
            continue
        if spec.slide_purpose not in layout.supported_purposes:
            continue
        if not _layout_supports_content(spec, layout):
            continue
        if not _content_respects_capacity(spec, layout):
            continue
        compatible.append(layout)
    return compatible


def require_compatible_override(
    spec: SlideSpec, layouts: list[LayoutRecord], override_code: Any
) -> LayoutRecord:
    code = _validate_override_code(override_code)
    override_layout = next(
        (layout for layout in layouts if layout.layout_code == code), None
    )
    if override_layout is None:
        raise ValueError(f"Unknown layout override '{code}'")

    compatible = compatible_layouts(spec, layouts)
    if override_layout not in compatible:
        raise ValueError(f"Explicit layout override '{code}' is incompatible with the spec")

    return override_layout


def rank_layouts(
    spec: SlideSpec,
    layouts: list[LayoutRecord],
    recipe_rules: dict[str, Any],
) -> list[LayoutRecord]:
    ranked: list[LayoutRecord] = []
    seen_codes: set[str] = set()

    preferred = recipe_rules.get("preferred_layout_codes", {}).get(spec.slide_purpose)
    if preferred:
        preferred_list: list[str]
        if isinstance(preferred, str):
            preferred_list = [preferred]
        else:
            preferred_list = list(preferred)
        for code in preferred_list:
            for layout in layouts:
                if layout.layout_code == code and layout.layout_code not in seen_codes:
                    ranked.append(layout)
                    seen_codes.add(layout.layout_code)

    fallback = [layout for layout in layouts if layout.layout_code not in seen_codes]
    fallback.sort(key=lambda layout: layout.layout_code)
    ranked.extend(fallback)
    return ranked


def _layout_supports_content(spec: SlideSpec, layout: LayoutRecord) -> bool:
    slot_types = set(layout.slot_schema)
    block_types = {block.get("type") for block in spec.content_blocks if block.get("type")}
    return block_types.issubset(slot_types)


def _content_respects_capacity(spec: SlideSpec, layout: LayoutRecord) -> bool:
    bullets = sum(
        len(block.get("items", []))
        for block in spec.content_blocks
        if block.get("type") == "bullets"
    )
    bullets_max = layout.capacity_rules.get("bullets_max")
    if bullets_max is not None and bullets > bullets_max:
        return False
    return True


def _validate_override_code(value: Any) -> str:
    if not isinstance(value, str):
        raise ValueError(
            f"deterministic layout override must be a string, got {type(value).__name__} ({value!r})"
        )
    if value == "":
        raise ValueError("deterministic layout override must be a non-empty string")
    return value
