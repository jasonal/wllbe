from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

from wllbe.domain.brief import Brief


class ProjectStore:
    def __init__(self, root: Path) -> None:
        self.root = root

    @property
    def chapter_outline_generated_path(self) -> Path:
        return self.root / "chapter-outline.generated.json"

    @property
    def chapter_outline_approved_path(self) -> Path:
        return self.root / "chapter-outline.approved.json"

    @property
    def page_outline_generated_path(self) -> Path:
        return self.root / "page-outline.generated.json"

    @property
    def page_outline_approved_path(self) -> Path:
        return self.root / "page-outline.approved.json"

    @property
    def slide_specs_path(self) -> Path:
        return self.root / "slide-specs.json"

    def write_brief(self, brief: Brief, raw_text: str) -> None:
        self.root.mkdir(parents=True, exist_ok=True)
        (self.root / "brief.md").write_text(raw_text, encoding="utf-8")
        (self.root / "brief.normalized.json").write_text(
            json.dumps(asdict(brief), indent=2),
            encoding="utf-8",
        )
