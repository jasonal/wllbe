from __future__ import annotations

import json
import shutil
from dataclasses import asdict
from pathlib import Path
from typing import Any

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

    def write_json(self, filename: str, payload: Any) -> None:
        self.root.mkdir(parents=True, exist_ok=True)
        (self.root / filename).write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def read_json(self, filename: str) -> Any:
        return json.loads((self.root / filename).read_text(encoding="utf-8"))

    def approve_artifact(self, artifact_name: str, edited_path: Path) -> None:
        self.root.mkdir(parents=True, exist_ok=True)
        valid_artifacts = {
            "chapter-outline": (self.chapter_outline_generated_path, self.chapter_outline_approved_path),
            "page-outline": (self.page_outline_generated_path, self.page_outline_approved_path),
        }
        if artifact_name not in valid_artifacts:
            raise ValueError(f"invalid artifact name: {artifact_name}")

        generated_path, approved_path = valid_artifacts[artifact_name]
        if not generated_path.exists():
            raise FileNotFoundError(f"generated artifact not found: {generated_path}")

        shutil.copyfile(edited_path, approved_path)
