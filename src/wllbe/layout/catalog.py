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
    for layout_file in sorted(root.rglob("*.json")):
        with layout_file.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
        records.append(_parse_record(data))
    return records


def _parse_record(data: dict[str, Any]) -> LayoutRecord:
    return LayoutRecord(
        layout_id=data["layout_id"],
        layout_code=data["layout_code"],
        layout_label=data.get("layout_label", ""),
        layout_family=data["layout_family"],
        supported_purposes=list(data.get("supported_purposes", [])),
        slot_schema=list(data.get("slot_schema", [])),
        capacity_rules=dict(data.get("capacity_rules", {})),
        visual_rhythm_tags=list(data.get("visual_rhythm_tags", [])),
        style_compatibility=list(data.get("style_compatibility", [])),
        status=data.get("status", "production"),
    )
