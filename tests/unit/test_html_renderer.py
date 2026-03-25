from __future__ import annotations

import json
from pathlib import Path

import pytest

from wllbe.render.html_renderer import render_version
from wllbe.render.bundle_writer import write_bundle


def test_render_version_outputs_single_html_document():
    html = render_version(
        version_id="version-a",
        slides=[
            {
                "slide_id": "s1",
                "title": "Launch opportunity",
                "body_html": "<ul><li>Speed</li><li>Trust</li></ul>",
            }
        ],
        style_pack={"style_pack_id": "clean-light", "tokens": {"bg": "#ffffff", "text": "#111111"}},
    )
    assert html.startswith("<!DOCTYPE html>")
    assert 'data-version="version-a"' in html
    assert "Launch opportunity" in html
    assert "#ffffff" in html


def test_write_bundle_creates_expected_files(tmp_path: Path):
    rendered_versions = {
        "version-a": "<html>alpha</html>",
        "version-b": "<html>beta</html>",
    }
    manifest = {"bundle_id": "bundle-alpha"}
    version_plan = {"plan_id": "plan-alpha", "versions": list(rendered_versions)}
    write_bundle(tmp_path, manifest, version_plan, rendered_versions)

    assert (tmp_path / "plan.json").exists()
    assert json.loads((tmp_path / "plan.json").read_text(encoding="utf-8")) == version_plan

    bundle_manifest_path = tmp_path / "bundle" / "manifest.json"
    assert bundle_manifest_path.exists()
    assert json.loads(bundle_manifest_path.read_text(encoding="utf-8")) == manifest

    for version_id, html in rendered_versions.items():
        version_index = tmp_path / "versions" / version_id / "index.html"
        assert version_index.exists()
        assert version_index.read_text(encoding="utf-8") == html
