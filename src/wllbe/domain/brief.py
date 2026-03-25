from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class Brief:
    goal: str
    audience: str
    tone: str
    constraints: list[str]
    page_budget: int
    source_materials: list[str]
