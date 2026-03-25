import json
from dataclasses import asdict
from pathlib import Path

import pytest

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
    raw_text = "launch a product"
    store.write_brief(brief, raw_text=raw_text)

    assert (store.root / "brief.md").exists()
    assert (store.root / "brief.normalized.json").exists()
    assert (store.root / "brief.md").read_text(encoding="utf-8") == raw_text
    normalized = json.loads((store.root / "brief.normalized.json").read_text(encoding="utf-8"))
    assert normalized == asdict(brief)
    assert store.chapter_outline_generated_path == (store.root / "chapter-outline.generated.json")
    assert store.chapter_outline_approved_path == (store.root / "chapter-outline.approved.json")
    assert store.page_outline_generated_path == (store.root / "page-outline.generated.json")
    assert store.page_outline_approved_path == (store.root / "page-outline.approved.json")
    assert store.slide_specs_path == (store.root / "slide-specs.json")


def test_approve_chapter_outline_copies_user_edited_file(tmp_path: Path) -> None:
    store = ProjectStore(tmp_path / "runs" / "demo")
    store.write_json("chapter-outline.generated.json", {"chapters": [{"title": "Draft"}]})
    edited = tmp_path / "edited.json"
    edited.write_text('{"chapters": [{"title": "Approved"}]}', encoding="utf-8")

    store.approve_artifact("chapter-outline", edited)

    approved = store.read_json("chapter-outline.approved.json")
    assert approved["chapters"][0]["title"] == "Approved"


def test_approve_artifact_rejects_invalid_artifact_name(tmp_path: Path) -> None:
    store = ProjectStore(tmp_path / "runs" / "demo")
    edited = tmp_path / "edited.json"
    edited.write_text('{}', encoding="utf-8")

    with pytest.raises(ValueError):
        store.approve_artifact("../chapter-outline", edited)


def test_approve_artifact_requires_generated_file_without_creating_project_root(
    tmp_path: Path,
) -> None:
    store = ProjectStore(tmp_path / "runs" / "demo")
    edited = tmp_path / "edited.json"
    edited.write_text('{}', encoding="utf-8")

    with pytest.raises(FileNotFoundError):
        store.approve_artifact("chapter-outline", edited)

    assert not store.root.exists()


def test_write_json_rejects_paths_outside_project_root(tmp_path: Path) -> None:
    store = ProjectStore(tmp_path / "runs" / "demo")

    with pytest.raises(ValueError):
        store.write_json("../escaped.json", {"title": "Escaped"})

    assert not (tmp_path / "runs" / "escaped.json").exists()


def test_read_json_rejects_paths_outside_project_root(tmp_path: Path) -> None:
    store = ProjectStore(tmp_path / "runs" / "demo")
    escaped = tmp_path / "runs" / "escaped.json"
    escaped.parent.mkdir(parents=True, exist_ok=True)
    escaped.write_text('{"title": "Escaped"}', encoding="utf-8")

    with pytest.raises(ValueError):
        store.read_json("../escaped.json")
