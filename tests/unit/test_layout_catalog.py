import json
from pathlib import Path

import pytest

from wllbe.layout.catalog import LayoutRecord, load_layout_catalog


def _catalog_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _write_layout(tmp_path: Path, rel_path: str, data: dict[str, object]) -> Path:
    target = tmp_path / rel_path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(data))
    return target


def _minimal_layout(
    *,
    layout_id: str = "comparison.focus",
    layout_code: str = "CMP-01",
    layout_family: str = "comparison",
) -> dict[str, object]:
    return {
        "layout_id": layout_id,
        "layout_code": layout_code,
        "layout_label": "Comparison focus layout",
        "layout_family": layout_family,
        "supported_purposes": ["comparison"],
        "slot_schema": ["heading", "bullets"],
        "status": "production",
    }


def test_load_layout_catalog_returns_expected_records():
    catalog_dir = _catalog_root() / "catalog" / "layouts"
    layouts = load_layout_catalog(catalog_dir)
    assert len(layouts) == 4
    assert all(isinstance(record, LayoutRecord) for record in layouts)


def test_catalog_includes_comparison_layout():
    catalog_dir = _catalog_root() / "catalog" / "layouts"
    layouts = load_layout_catalog(catalog_dir)
    comparison_layouts = [layout for layout in layouts if layout.layout_family == "comparison"]
    assert comparison_layouts
    assert any(layout.layout_code == "CMP-01" for layout in comparison_layouts)


def test_load_layout_catalog_rejects_duplicate_layout_code(tmp_path):
    root = tmp_path / "layouts"
    _write_layout(root, "a.json", _minimal_layout(layout_code="DUP-01"))
    _write_layout(root, "b.json", _minimal_layout(layout_id="comparison.dup", layout_code="DUP-01"))
    with pytest.raises(ValueError, match="layout_code 'DUP-01'"):
        load_layout_catalog(root)


def test_load_layout_catalog_rejects_duplicate_layout_id(tmp_path):
    root = tmp_path / "layouts"
    _write_layout(root, "a/a.json", _minimal_layout(layout_id="dup.id"))
    _write_layout(root, "b/b.json", _minimal_layout(layout_id="dup.id", layout_code="CMP-02"))
    with pytest.raises(ValueError, match="layout_id 'dup.id'"):
        load_layout_catalog(root)


def test_load_layout_catalog_rejects_malformed_supported_purposes(tmp_path):
    root = tmp_path / "layouts"
    malformed = _minimal_layout()
    malformed["supported_purposes"] = "comparison"
    _write_layout(root, "bad.json", malformed)
    with pytest.raises(ValueError, match="supported_purposes"):
        load_layout_catalog(root)
