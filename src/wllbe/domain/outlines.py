from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class Chapter:
    title: str
    estimated_pages: int = 1
    chapter_id: str | None = None
    message: str | None = None


@dataclass(slots=True)
class ChapterOutline:
    chapters: list[Chapter]
    goal: str | None = None
    audience: str | None = None
    tone: str | None = None

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> ChapterOutline:
        chapters = [
            Chapter(
                title=str(chapter.get("title", "")),
                estimated_pages=int(chapter.get("estimated_pages", 1)),
                chapter_id=chapter.get("chapter_id"),
                message=chapter.get("message"),
            )
            for chapter in payload.get("chapters", [])
        ]
        return cls(
            chapters=chapters,
            goal=payload.get("goal"),
            audience=payload.get("audience"),
            tone=payload.get("tone"),
        )


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

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> PageOutline:
        pages = [
            Page(
                page_id=str(page.get("page_id", "")),
                chapter_id=str(page.get("chapter_id", "")),
                title=str(page.get("title", "")),
                message=str(page.get("message", "")),
                content_blocks=list(page.get("content_blocks", [])),
                layout_hints=list(page.get("layout_hints", [])),
            )
            for page in payload.get("pages", [])
        ]
        return cls(pages=pages)
