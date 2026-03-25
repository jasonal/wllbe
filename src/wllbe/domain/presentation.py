from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class VersionPlan:
    version_id: str
    recipe_id: str
    style_pack_id: str
    allowed_layout_families: list[str] = field(default_factory=list)
    motion_intensity: str = "medium"
    density_target: str = "medium"
