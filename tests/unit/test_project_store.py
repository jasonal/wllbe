from pathlib import Path

from wllbe.domain.brief import Brief
from wllbe.projects.store import ProjectStore


def test_project_store_writes_brief_and_expected_paths(tmp_path: Path) -> None:
    store = ProjectStore(tmp_path / "runs" / "demo")
    brief = Brief(
        goal="Launch deck",
        audience="Leaders",
        tone="Clear",
        constraints=[],
        page_budget=8,
        source_materials=[],
    )
    store.write_brief(brief, raw_text="launch a product")

    assert (store.root / "brief.md").exists()
    assert (store.root / "brief.normalized.json").exists()
    assert store.chapter_outline_generated_path == (store.root / "chapter-outline.generated.json")
    assert store.chapter_outline_approved_path == (store.root / "chapter-outline.approved.json")
    assert store.page_outline_generated_path == (store.root / "page-outline.generated.json")
    assert store.page_outline_approved_path == (store.root / "page-outline.approved.json")
    assert store.slide_specs_path == (store.root / "slide-specs.json")
