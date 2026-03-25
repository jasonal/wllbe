# Render HTML Bundles Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Deliver the minimal HTML renderer and bundle writer from Task 9 so rendered decks and manifests exist for downstream tests.

**Architecture:** `render_version` concatenates deterministic templates for the deck, slides, and theme CSS so each version outputs a single document with a data-version marker. `write_bundle` mirrors the expected bundle layout by materializing `plan.json`, `bundle/manifest.json`, and each version’s `index.html`.

**Tech Stack:** Python 3 standard library for templating + JSON IO, pytest for verification.

---

### Task 1: HTML renderer baseline

**Files:**
- Create: `src/wllbe/render/templates/deck.html`
- Create: `src/wllbe/render/templates/slide.html`
- Create: `src/wllbe/render/templates/theme.css`
- Create: `src/wllbe/render/html_renderer.py`
- Test: `tests/unit/test_html_renderer.py`

- [ ] **Step 1: Write the failing renderer test**

```python
from pathlib import Path

from wllbe.render.html_renderer import render_version


def test_render_version_outputs_single_html_document(tmp_path: Path):
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
```

- [ ] **Step 2: Run the renderer test to verify it fails**

Run: `/Users/zengxiangyi/HTML PPT V2/.worktrees/phase1-subagent/.venv/bin/python -m pytest tests/unit/test_html_renderer.py -q`
Expected: FAIL because the renderer module and templates do not exist.

- [ ] **Step 3: Implement minimal HTML rendering**

```python
def render_version(version_id: str, slides: list[dict[str, Any]], style_pack: dict[str, Any]) -> str:
    slide_html = "\n".join(render_slide(slide) for slide in slides)
    return DECK_TEMPLATE.format(
        version_id=version_id,
        slide_html=slide_html,
        theme_css=render_theme_css(style_pack),
    )
```
fill `render_slide` by loading `slide.html` and `render_theme_css` from `theme.css`, anchoring tokens.

- [ ] **Step 4: Run the renderer test to verify it passes**

Run: `/Users/zengxiangyi/HTML PPT V2/.worktrees/phase1-subagent/.venv/bin/python -m pytest tests/unit/test_html_renderer.py -q`
Expected: PASS after templates and renderer exist.

- [ ] **Step 5: Commit**

```bash
git add src/wllbe/render/html_renderer.py src/wllbe/render/templates/deck.html src/wllbe/render/templates/slide.html src/wllbe/render/templates/theme.css tests/unit/test_html_renderer.py
git commit -m "feat: render versioned html decks and bundle manifest"
```

### Task 2: Bundle writer output

**Files:**
- Create: `src/wllbe/render/bundle_writer.py`
- Test: `tests/unit/test_html_renderer.py`

- [ ] **Step 1: Extend the renderer test to cover bundle output**

Add assertions that after calling `write_bundle` with a manifest and rendered versions, the following files exist and their text matches the inputs:
`plan.json`, `bundle/manifest.json`, `versions/version-a/index.html`, `versions/version-b/index.html`.

- [ ] **Step 2: Run the renderer test to verify it fails**

Run: `/Users/zengxiangyi/HTML PPT V2/.worktrees/phase1-subagent/.venv/bin/python -m pytest tests/unit/test_html_renderer.py -q`
Expected: FAIL because `write_bundle` does not exist or files are missing.

- [ ] **Step 3: Implement minimal bundle writer**

```python
def write_bundle(root: Path, manifest: dict[str, Any], version_plan: dict[str, Any], rendered_versions: dict[str, str]) -> None:
    root.mkdir(parents=True, exist_ok=True)
    (root / "plan.json").write_text(json.dumps(version_plan, indent=2), encoding="utf-8")
    (root / "bundle").mkdir(exist_ok=True)
    (root / "bundle" / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    for version_id, html in rendered_versions.items():
        version_dir = root / "versions" / version_id
        version_dir.mkdir(parents=True, exist_ok=True)
        (version_dir / "index.html").write_text(html, encoding="utf-8")
```

- [ ] **Step 4: Run the renderer test to verify it passes**

Run: `/Users/zengxiangyi/HTML PPT V2/.worktrees/phase1-subagent/.venv/bin/python -m pytest tests/unit/test_html_renderer.py -q`
Expected: PASS once `write_bundle` writes everything.

- [ ] **Step 5: Commit**

```bash
git add src/wllbe/render/bundle_writer.py tests/unit/test_html_renderer.py
git commit -m "feat: render versioned html decks and bundle manifest"
```

Plan complete and saved to `docs/superpowers/plans/2026-03-25-render-html-bundles.md`. Execution options:

1. Subagent-Driven (recommended) – use superpowers:subagent-driven-development to tackle each task with a dedicated subagent and reviewer per task.
2. Inline Execution – remain in this session using superpowers:executing-plans with manual checkpoints.
