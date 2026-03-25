from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class Chapter:
    chapter_id: str
    title: str
    intent: str
    key_points: list[str] = field(default_factory=list)
    estimated_pages: int = 1


@dataclass(slots=True)
class ChapterOutline:
    chapters: list[Chapter]
    goal: str | None = None
    audience: str | None = None
    tone: str | None = None


@dataclass(slots=True)
class Page:
    page_id: str
    chapter_id: str
    title: str
    message: str
    content_blocks: list[dict[str, Any]] = field(default_factory=list)
    layout_hints: list[Any] = field(default_factory=list)


@dataclass(slots=True)
class PageOutline:
    pages: list[Page]
