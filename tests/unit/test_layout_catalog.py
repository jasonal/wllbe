from pathlib import Path

from wllbe.layout.catalog import LayoutRecord, load_layout_catalog


def _catalog_root() -> Path:
    return Path(__file__).resolve().parents[2]


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
