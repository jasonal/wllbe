from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class LayoutRecord:
    layout_id: str
    layout_code: str
    layout_label: str
    layout_family: str
    supported_purposes: list[str]
    slot_schema: list[str]
    capacity_rules: dict[str, Any] = field(default_factory=dict)
    visual_rhythm_tags: list[str] = field(default_factory=list)
    style_compatibility: list[str] = field(default_factory=list)
    status: str = "production"


def load_layout_catalog(root: Path) -> list[LayoutRecord]:
    root = root.expanduser().resolve()
    records: list[LayoutRecord] = []
    seen_layout_ids: set[str] = set()
    seen_layout_codes: set[str] = set()

    for layout_file in sorted(root.rglob("*.json")):
        with layout_file.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
        record = _parse_record(data)
        if record.layout_id in seen_layout_ids:
            raise ValueError(
                f"Duplicate layout_id '{record.layout_id}' seen while loading {layout_file}"
            )
        if record.layout_code in seen_layout_codes:
            raise ValueError(
                f"Duplicate layout_code '{record.layout_code}' seen while loading {layout_file}"
            )
        seen_layout_ids.add(record.layout_id)
        seen_layout_codes.add(record.layout_code)
        records.append(record)
    return records


def _parse_record(data: dict[str, Any]) -> LayoutRecord:
    layout_id = _require_string(data.get("layout_id"), "layout_id", required=True)
    layout_code = _require_string(data.get("layout_code"), "layout_code", required=True)
    layout_label = _require_string(data.get("layout_label"), "layout_label", default="")
    layout_family = _require_string(data.get("layout_family"), "layout_family", required=True)
    supported_purposes = _require_string_list(
        data.get("supported_purposes"), "supported_purposes", required=True
    )
    slot_schema = _require_string_list(
        data.get("slot_schema"), "slot_schema", required=True
    )
    capacity_rules = _require_dict(data.get("capacity_rules"), "capacity_rules", default={})
    visual_rhythm_tags = _require_string_list(
        data.get("visual_rhythm_tags"), "visual_rhythm_tags", default=[]
    )
    style_compatibility = _require_string_list(
        data.get("style_compatibility"), "style_compatibility", default=[]
    )
    status = _require_string(data.get("status"), "status", default="production")

    return LayoutRecord(
        layout_id=layout_id,
        layout_code=layout_code,
        layout_label=layout_label,
        layout_family=layout_family,
        supported_purposes=supported_purposes,
        slot_schema=slot_schema,
        capacity_rules=capacity_rules,
        visual_rhythm_tags=visual_rhythm_tags,
        style_compatibility=style_compatibility,
        status=status,
    )


def _require_string(
    value: Any,
    field_name: str,
    *,
    required: bool = False,
    default: str | None = None,
) -> str:
    if value is None:
        if default is not None:
            return default
        if required:
            raise ValueError(f"Missing required string field '{field_name}'")
        return ""
    if not isinstance(value, str):
        raise ValueError(
            f"Layout field '{field_name}' must be a string, got {type(value).__name__} ({value!r})"
        )
    return value


def _require_string_list(
    value: Any,
    field_name: str,
    *,
    required: bool = False,
    default: list[str] | None = None,
) -> list[str]:
    if value is None:
        if default is not None:
            return default
        if required:
            raise ValueError(f"Missing required list field '{field_name}'")
        return []
    if not isinstance(value, list):
        raise ValueError(
            f"Layout field '{field_name}' must be a list of strings, got {type(value).__name__} ({value!r})"
        )
    if not all(isinstance(item, str) for item in value):
        raise ValueError(f"Layout field '{field_name}' must contain only strings")
    return list(value)


def _require_dict(
    value: Any, field_name: str, *, default: dict[str, Any] | None = None
) -> dict[str, Any]:
    if value is None:
        return default or {}
    if not isinstance(value, dict):
        raise ValueError(
            f"Layout field '{field_name}' must be a dict, got {type(value).__name__} ({value!r})"
        )
    return dict(value)
