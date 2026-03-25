from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class SlideSpec:
    slide_id: str
    chapter_id: str
    sequence: int
    slide_purpose: str
    content_blocks: list[dict[str, Any]]
    priority_metadata: dict[str, Any]
    density_metadata: dict[str, Any]
    visual_intent_tags: list[str] = field(default_factory=list)
    hard_constraints: dict[str, Any] = field(default_factory=dict)
    deterministic_layout_override: str | None = None
