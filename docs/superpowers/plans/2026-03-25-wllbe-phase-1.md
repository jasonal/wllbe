# Wllbe Phase 1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the Phase 1 `wllbe` generation core so a natural-language brief can flow through reviewed outlines, semantic slide specs, layout/style selection, validation, and versioned HTML deck bundle output.

**Architecture:** Implement a provider-agnostic Python pipeline with strict intermediate artifacts: brief, chapter outline, page outline, slide specs, layout matches, style recipes, validation report, and rendered deck bundle. Keep content, layout, and style in separate modules so future card-pick review and publishing can consume structured outputs instead of raw HTML blobs.

**Tech Stack:** Python 3.12+, `pytest`, standard-library `dataclasses`/`json`/`pathlib`, static HTML/CSS templates, JSON catalogs for layouts/styles/recipes

---

## File Structure

### Repository bootstrap

- Create: `pyproject.toml`
- Create: `src/wllbe/__init__.py`
- Create: `src/wllbe/cli.py`
- Create: `tests/conftest.py`

### Domain artifacts

- Create: `src/wllbe/domain/brief.py`
- Create: `src/wllbe/domain/outlines.py`
- Create: `src/wllbe/domain/slide_specs.py`
- Create: `src/wllbe/domain/presentation.py`
- Create: `src/wllbe/projects/store.py`

### Generation pipeline

- Create: `src/wllbe/generation/provider.py`
- Create: `src/wllbe/generation/brief_to_chapters.py`
- Create: `src/wllbe/generation/chapters_to_pages.py`
- Create: `src/wllbe/generation/pages_to_specs.py`

### Layout and style catalogs

- Create: `src/wllbe/layout/catalog.py`
- Create: `src/wllbe/layout/matcher.py`
- Create: `src/wllbe/style/catalog.py`
- Create: `src/wllbe/style/recipes.py`
- Create: `catalog/layouts/cover/COV-01.json`
- Create: `catalog/layouts/section/SEC-01.json`
- Create: `catalog/layouts/comparison/CMP-01.json`
- Create: `catalog/layouts/data/DAT-01.json`
- Create: `catalog/styles/clean-light.json`
- Create: `catalog/styles/dark-tech.json`
- Create: `catalog/recipes/neutral-balanced.json`
- Create: `catalog/recipes/bold-contrast.json`

### Rendering and validation

- Create: `src/wllbe/render/templates/deck.html`
- Create: `src/wllbe/render/templates/slide.html`
- Create: `src/wllbe/render/templates/theme.css`
- Create: `src/wllbe/render/html_renderer.py`
- Create: `src/wllbe/render/bundle_writer.py`
- Create: `src/wllbe/validation/checks.py`
- Create: `src/wllbe/validation/report.py`

### Fixtures and tests

- Create: `tests/fixtures/briefs/product-launch.md`
- Create: `tests/fixtures/providers/chapter_outline.json`
- Create: `tests/fixtures/providers/page_outline.json`
- Create: `tests/fixtures/projects/approved_chapters.json`
- Create: `tests/fixtures/projects/approved_pages.json`
- Create: `tests/unit/test_cli.py`
- Create: `tests/unit/test_project_store.py`
- Create: `tests/unit/test_brief_to_chapters.py`
- Create: `tests/unit/test_chapters_to_pages.py`
- Create: `tests/unit/test_pages_to_specs.py`
- Create: `tests/unit/test_layout_catalog.py`
- Create: `tests/unit/test_layout_matcher.py`
- Create: `tests/unit/test_style_recipes.py`
- Create: `tests/unit/test_html_renderer.py`
- Create: `tests/unit/test_validation_checks.py`
- Create: `tests/e2e/test_phase1_cli.py`

## Project Bundle Contract

Every generated project should live under a directory shaped like this:

```text
runs/<project_slug>/
  brief.md
  brief.normalized.json
  chapter-outline.generated.json
  chapter-outline.approved.json
  page-outline.generated.json
  page-outline.approved.json
  slide-specs.json
  plan.json
  validation.json
  versions/
    version-a/
      index.html
    version-b/
      index.html
  bundle/
    manifest.json
```

The plan below assumes this directory structure from the start so later phases do not have to migrate artifact locations.

## Implementation Notes

- Use `@superpowers/test-driven-development` during implementation even though this plan already embeds the red-green sequence.
- Use `@superpowers/systematic-debugging` if any command fails unexpectedly.
- Keep runtime dependencies minimal in Phase 1. Do not add an LLM SDK yet; hide external generation behind `GenerationProvider`.
- Treat `layout_code` as human-facing and `layout_id` as canonical internal identity.
- Never silently override an explicit deterministic layout choice.

### Task 1: Bootstrap the Python package and CLI skeleton

**Files:**
- Create: `pyproject.toml`
- Create: `src/wllbe/__init__.py`
- Create: `src/wllbe/cli.py`
- Create: `tests/conftest.py`
- Test: `tests/unit/test_cli.py`

- [ ] **Step 1: Create the packaging scaffold needed to run tests**

```toml
[build-system]
requires = ["setuptools>=68"]
build-backend = "setuptools.build_meta"

[project]
name = "wllbe"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = []

[project.optional-dependencies]
dev = ["pytest>=8.0"]

[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = ["src"]
```

- [ ] **Step 2: Install the editable development environment**

Run: `python3 -m pip install -e '.[dev]'`
Expected: editable install succeeds and `pytest` becomes available

- [ ] **Step 3: Write the failing CLI smoke test**

```python
from wllbe.cli import main


def test_main_prints_usage_for_no_args(capsys):
    exit_code = main([])
    captured = capsys.readouterr()
    assert exit_code == 1
    assert "wllbe <command>" in captured.out
```

- [ ] **Step 4: Run the CLI smoke test to verify it fails**

Run: `python3 -m pytest tests/unit/test_cli.py -q`
Expected: FAIL because `wllbe.cli` or `main()` does not exist yet

- [ ] **Step 5: Implement the minimal CLI entry point**

```python
def main(argv: list[str] | None = None) -> int:
    argv = argv or []
    if not argv:
        print("wllbe <command>")
        return 1
    print(f"unknown command: {argv[0]}")
    return 2
```

- [ ] **Step 6: Run the CLI smoke test to verify it passes**

Run: `python3 -m pytest tests/unit/test_cli.py -q`
Expected: PASS

- [ ] **Step 7: Commit**

```bash
git add pyproject.toml src/wllbe/__init__.py src/wllbe/cli.py tests/conftest.py tests/unit/test_cli.py
git commit -m "chore: bootstrap wllbe phase1 package"
```

### Task 2: Define bundle models and project-store helpers

**Files:**
- Create: `src/wllbe/domain/brief.py`
- Create: `src/wllbe/domain/outlines.py`
- Create: `src/wllbe/domain/slide_specs.py`
- Create: `src/wllbe/domain/presentation.py`
- Create: `src/wllbe/projects/store.py`
- Test: `tests/unit/test_project_store.py`

- [ ] **Step 1: Write the failing project-store round-trip test**

```python
from pathlib import Path

from wllbe.domain.brief import Brief
from wllbe.projects.store import ProjectStore


def test_project_store_writes_brief_and_expected_paths(tmp_path: Path):
    store = ProjectStore(tmp_path / "runs" / "demo")
    brief = Brief(goal="Launch deck", audience="Leaders", tone="Clear", constraints=[], page_budget=8, source_materials=[])
    store.write_brief(brief, raw_text="launch a product")

    assert (store.root / "brief.md").exists()
    assert (store.root / "brief.normalized.json").exists()
```

- [ ] **Step 2: Run the store test to verify it fails**

Run: `python3 -m pytest tests/unit/test_project_store.py -q`
Expected: FAIL because the domain models and `ProjectStore` do not exist yet

- [ ] **Step 3: Implement the artifact dataclasses and store helper**

```python
@dataclass(slots=True)
class Brief:
    goal: str
    audience: str
    tone: str
    constraints: list[str]
    page_budget: int
    source_materials: list[str]
```

```python
class ProjectStore:
    def __init__(self, root: Path) -> None:
        self.root = root

    def write_brief(self, brief: Brief, raw_text: str) -> None:
        self.root.mkdir(parents=True, exist_ok=True)
        (self.root / "brief.md").write_text(raw_text, encoding="utf-8")
        (self.root / "brief.normalized.json").write_text(json.dumps(asdict(brief), indent=2), encoding="utf-8")
```

- [ ] **Step 4: Extend the test to cover generated and approved outline paths**

Add assertions for:
`chapter-outline.generated.json`
`chapter-outline.approved.json`
`page-outline.generated.json`
`page-outline.approved.json`
`slide-specs.json`

- [ ] **Step 5: Run the store test to verify it passes**

Run: `python3 -m pytest tests/unit/test_project_store.py -q`
Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add src/wllbe/domain/brief.py src/wllbe/domain/outlines.py src/wllbe/domain/slide_specs.py src/wllbe/domain/presentation.py src/wllbe/projects/store.py tests/unit/test_project_store.py
git commit -m "feat: add phase1 artifact models and project store"
```

### Task 3: Add provider abstraction and brief-to-chapter generation

**Files:**
- Create: `src/wllbe/generation/provider.py`
- Create: `src/wllbe/generation/brief_to_chapters.py`
- Create: `tests/fixtures/briefs/product-launch.md`
- Create: `tests/fixtures/providers/chapter_outline.json`
- Test: `tests/unit/test_brief_to_chapters.py`

- [ ] **Step 1: Write the failing chapter-generation test**

```python
from pathlib import Path

from wllbe.generation.brief_to_chapters import generate_chapter_outline
from wllbe.generation.provider import FakeGenerationProvider


def test_generate_chapter_outline_returns_structured_chapters():
    provider = FakeGenerationProvider.from_file(Path("tests/fixtures/providers/chapter_outline.json"))
    result = generate_chapter_outline("launch a new AI product", provider)
    assert result.chapters[0].title == "Why this launch matters"
    assert result.chapters[0].estimated_pages == 2
```

- [ ] **Step 2: Run the chapter-generation test to verify it fails**

Run: `python3 -m pytest tests/unit/test_brief_to_chapters.py -q`
Expected: FAIL because the provider abstraction and generator do not exist yet

- [ ] **Step 3: Implement `GenerationProvider` and the chapter generator**

```python
class GenerationProvider(Protocol):
    def generate_json(self, task: str, payload: dict[str, Any]) -> dict[str, Any]:
        ...
```

```python
def generate_chapter_outline(raw_brief: str, provider: GenerationProvider) -> ChapterOutline:
    payload = provider.generate_json("brief_to_chapters", {"brief": raw_brief})
    return ChapterOutline.from_dict(payload)
```

- [ ] **Step 4: Add normalization assertions to the test**

Also assert:
`goal`
`audience`
`tone`
`estimated_pages`
are all persisted in normalized form rather than free-form provider output

- [ ] **Step 5: Run the chapter-generation test to verify it passes**

Run: `python3 -m pytest tests/unit/test_brief_to_chapters.py -q`
Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add src/wllbe/generation/provider.py src/wllbe/generation/brief_to_chapters.py tests/fixtures/briefs/product-launch.md tests/fixtures/providers/chapter_outline.json tests/unit/test_brief_to_chapters.py
git commit -m "feat: generate chapter outlines from a brief"
```

### Task 4: Persist human approval gates for chapter outlines

**Files:**
- Modify: `src/wllbe/cli.py`
- Modify: `src/wllbe/projects/store.py`
- Test: `tests/unit/test_cli.py`
- Test: `tests/unit/test_project_store.py`

- [ ] **Step 1: Write the failing approval-flow test**

```python
from wllbe.projects.store import ProjectStore


def test_approve_chapter_outline_copies_user_edited_file(tmp_path):
    store = ProjectStore(tmp_path / "runs" / "demo")
    store.write_json("chapter-outline.generated.json", {"chapters": [{"title": "Draft"}]})
    edited = tmp_path / "edited.json"
    edited.write_text('{"chapters": [{"title": "Approved"}]}', encoding="utf-8")

    store.approve_artifact("chapter-outline", edited)

    approved = store.read_json("chapter-outline.approved.json")
    assert approved["chapters"][0]["title"] == "Approved"
```

- [ ] **Step 2: Run the approval-flow tests to verify they fail**

Run: `python3 -m pytest tests/unit/test_project_store.py tests/unit/test_cli.py -q`
Expected: FAIL because `approve_artifact()` and approval CLI commands do not exist yet

- [ ] **Step 3: Implement the explicit approval workflow**

```python
def approve_artifact(self, artifact_name: str, edited_path: Path) -> None:
    target = self.root / f"{artifact_name}.approved.json"
    shutil.copyfile(edited_path, target)
```

Add CLI commands shaped like:

```text
python3 -m wllbe.cli approve chapters --project runs/demo --input /tmp/edited.json
python3 -m wllbe.cli approve pages --project runs/demo --input /tmp/edited.json
```

- [ ] **Step 4: Run the approval-flow tests to verify they pass**

Run: `python3 -m pytest tests/unit/test_project_store.py tests/unit/test_cli.py -q`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/wllbe/cli.py src/wllbe/projects/store.py tests/unit/test_cli.py tests/unit/test_project_store.py
git commit -m "feat: add explicit outline approval flow"
```

### Task 5: Generate page outlines from approved chapters

**Files:**
- Create: `src/wllbe/generation/chapters_to_pages.py`
- Create: `tests/fixtures/providers/page_outline.json`
- Test: `tests/unit/test_chapters_to_pages.py`

- [ ] **Step 1: Write the failing page-outline generation test**

```python
from pathlib import Path

from wllbe.generation.chapters_to_pages import generate_page_outline
from wllbe.generation.provider import FakeGenerationProvider


def test_generate_page_outline_expands_chapters_into_pages():
    provider = FakeGenerationProvider.from_file(Path("tests/fixtures/providers/page_outline.json"))
    result = generate_page_outline({"chapters": [{"title": "Market problem"}]}, provider)
    assert result.pages[0].title == "The market is fragmented"
    assert result.pages[0].message
```

- [ ] **Step 2: Run the page-outline test to verify it fails**

Run: `python3 -m pytest tests/unit/test_chapters_to_pages.py -q`
Expected: FAIL because `generate_page_outline()` does not exist yet

- [ ] **Step 3: Implement the page-outline generator**

```python
def generate_page_outline(approved_chapters: dict[str, Any], provider: GenerationProvider) -> PageOutline:
    payload = provider.generate_json("chapters_to_pages", approved_chapters)
    return PageOutline.from_dict(payload)
```

- [ ] **Step 4: Add a persistence test through `ProjectStore`**

Verify generated page outlines are written to `page-outline.generated.json` and approved copies live in `page-outline.approved.json`

- [ ] **Step 5: Run the page-outline tests to verify they pass**

Run: `python3 -m pytest tests/unit/test_chapters_to_pages.py tests/unit/test_project_store.py -q`
Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add src/wllbe/generation/chapters_to_pages.py tests/fixtures/providers/page_outline.json tests/unit/test_chapters_to_pages.py tests/unit/test_project_store.py
git commit -m "feat: generate page outlines from approved chapters"
```

### Task 6: Convert approved page outlines into semantic slide specs

**Files:**
- Create: `src/wllbe/generation/pages_to_specs.py`
- Test: `tests/unit/test_pages_to_specs.py`

- [ ] **Step 1: Write the failing slide-spec conversion test**

```python
from wllbe.generation.pages_to_specs import build_slide_specs


def test_build_slide_specs_keeps_semantics_without_layout_coordinates():
    page_outline = {
        "pages": [
            {
                "page_id": "p1",
                "chapter_id": "c1",
                "title": "Launch opportunity",
                "message": "The market window is open",
                "content_blocks": [{"type": "bullets", "items": ["Speed", "Trust"]}],
                "layout_hints": ["comparison"],
            }
        ]
    }

    specs = build_slide_specs(page_outline)
    assert specs[0].slide_purpose == "comparison"
    assert "x" not in specs[0].content_blocks[0]
    assert specs[0].deterministic_layout_override is None
```

- [ ] **Step 2: Run the slide-spec test to verify it fails**

Run: `python3 -m pytest tests/unit/test_pages_to_specs.py -q`
Expected: FAIL because `build_slide_specs()` does not exist yet

- [ ] **Step 3: Implement the semantic slide-spec builder**

```python
def build_slide_specs(page_outline: dict[str, Any]) -> list[SlideSpec]:
    specs = []
    for index, page in enumerate(page_outline["pages"], start=1):
        specs.append(
            SlideSpec(
                slide_id=page["page_id"],
                chapter_id=page["chapter_id"],
                sequence=index,
                slide_purpose=infer_slide_purpose(page),
                content_blocks=page["content_blocks"],
                priority_metadata={"message": "primary"},
                density_metadata={"target": "medium"},
                visual_intent_tags=[],
                hard_constraints={},
                deterministic_layout_override=None,
            )
        )
    return specs
```

- [ ] **Step 4: Extend the test to cover explicit deterministic overrides**

Add one page with:
`"layout_hints": [{"layout_code": "CMP-01", "strength": "required"}]`

Expected:
`spec.deterministic_layout_override == "CMP-01"`

- [ ] **Step 5: Run the slide-spec tests to verify they pass**

Run: `python3 -m pytest tests/unit/test_pages_to_specs.py -q`
Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add src/wllbe/generation/pages_to_specs.py tests/unit/test_pages_to_specs.py
git commit -m "feat: convert approved pages into slide specs"
```

### Task 7: Add layout catalog loading and deterministic matching

**Files:**
- Create: `src/wllbe/layout/catalog.py`
- Create: `src/wllbe/layout/matcher.py`
- Create: `catalog/layouts/cover/COV-01.json`
- Create: `catalog/layouts/section/SEC-01.json`
- Create: `catalog/layouts/comparison/CMP-01.json`
- Create: `catalog/layouts/data/DAT-01.json`
- Test: `tests/unit/test_layout_catalog.py`
- Test: `tests/unit/test_layout_matcher.py`

- [ ] **Step 1: Write the failing layout-catalog test**

```python
from pathlib import Path

from wllbe.layout.catalog import load_layout_catalog


def test_load_layout_catalog_exposes_id_code_and_family():
    layouts = load_layout_catalog(Path("catalog/layouts"))
    assert any(layout.layout_code == "CMP-01" for layout in layouts)
    assert any(layout.layout_id.startswith("comparison.") for layout in layouts)
```

- [ ] **Step 2: Write the failing deterministic-match test**

```python
from wllbe.layout.matcher import choose_layout
from wllbe.layout.catalog import LayoutRecord
from wllbe.domain.slide_specs import SlideSpec


def test_choose_layout_respects_explicit_override():
    layouts = [
        LayoutRecord(
            layout_id="comparison.two-column",
            layout_code="CMP-01",
            layout_label="Two column comparison",
            layout_family="comparison",
            supported_purposes=["comparison"],
            slot_schema=["heading", "bullets"],
            capacity_rules={"bullets_max": 4},
            visual_rhythm_tags=["balanced"],
            style_compatibility=["clean-light", "dark-tech"],
            status="production",
        )
    ]
    spec = SlideSpec(
        slide_id="s1",
        chapter_id="c1",
        sequence=1,
        slide_purpose="comparison",
        content_blocks=[{"type": "bullets", "items": ["Speed", "Trust"]}],
        priority_metadata={"message": "primary"},
        density_metadata={"target": "medium"},
        visual_intent_tags=[],
        hard_constraints={},
        deterministic_layout_override="CMP-01",
    )
    chosen = choose_layout(spec, layouts, recipe_rules={})
    assert chosen.layout_code == "CMP-01"
```

- [ ] **Step 3: Run the layout tests to verify they fail**

Run: `python3 -m pytest tests/unit/test_layout_catalog.py tests/unit/test_layout_matcher.py -q`
Expected: FAIL because the catalog loader and matcher do not exist yet

- [ ] **Step 4: Implement layout records and matching precedence**

```python
def choose_layout(spec: SlideSpec, layouts: list[LayoutRecord], recipe_rules: dict[str, Any]) -> LayoutRecord:
    if spec.deterministic_layout_override:
        return require_compatible_override(spec, layouts, spec.deterministic_layout_override)
    compatible = compatible_layouts(spec, layouts)
    return rank_layouts(spec, compatible, recipe_rules)[0]
```

The matcher must enforce:
1. explicit override
2. recipe rule preference
3. auto-ranked fallback

- [ ] **Step 5: Run the layout tests to verify they pass**

Run: `python3 -m pytest tests/unit/test_layout_catalog.py tests/unit/test_layout_matcher.py -q`
Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add src/wllbe/layout/catalog.py src/wllbe/layout/matcher.py catalog/layouts/cover/COV-01.json catalog/layouts/section/SEC-01.json catalog/layouts/comparison/CMP-01.json catalog/layouts/data/DAT-01.json tests/unit/test_layout_catalog.py tests/unit/test_layout_matcher.py
git commit -m "feat: add layout catalog and deterministic matcher"
```

### Task 8: Add style packs and deck recipes for controlled version diversity

**Files:**
- Create: `src/wllbe/style/catalog.py`
- Create: `src/wllbe/style/recipes.py`
- Create: `catalog/styles/clean-light.json`
- Create: `catalog/styles/dark-tech.json`
- Create: `catalog/recipes/neutral-balanced.json`
- Create: `catalog/recipes/bold-contrast.json`
- Test: `tests/unit/test_style_recipes.py`

- [ ] **Step 1: Write the failing version-plan test**

```python
from wllbe.style.recipes import build_version_plan


def test_build_version_plan_returns_coherent_versions():
    plan = build_version_plan(version_count=2)
    assert plan[0].version_id == "version-a"
    assert plan[0].recipe_id != plan[1].recipe_id
    assert plan[0].style_pack_id != plan[1].style_pack_id
```

- [ ] **Step 2: Run the version-plan test to verify it fails**

Run: `python3 -m pytest tests/unit/test_style_recipes.py -q`
Expected: FAIL because recipe planning does not exist yet

- [ ] **Step 3: Implement style and recipe catalog loading**

```python
def build_version_plan(version_count: int) -> list[VersionPlan]:
    recipes = load_recipe_catalog(Path("catalog/recipes"))
    styles = load_style_catalog(Path("catalog/styles"))
    return [
        VersionPlan(version_id="version-a", recipe_id=recipes[0].recipe_id, style_pack_id=styles[0].style_pack_id),
        VersionPlan(version_id="version-b", recipe_id=recipes[1].recipe_id, style_pack_id=styles[1].style_pack_id),
    ][:version_count]
```

- [ ] **Step 4: Extend the test to assert deck-level coherence**

Assert each version plan contains:
`allowed_layout_families`
`motion_intensity`
`density_target`

- [ ] **Step 5: Run the version-plan test to verify it passes**

Run: `python3 -m pytest tests/unit/test_style_recipes.py -q`
Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add src/wllbe/style/catalog.py src/wllbe/style/recipes.py catalog/styles/clean-light.json catalog/styles/dark-tech.json catalog/recipes/neutral-balanced.json catalog/recipes/bold-contrast.json tests/unit/test_style_recipes.py
git commit -m "feat: add style packs and deck recipe planning"
```

### Task 9: Render HTML decks and write the bundle manifest

**Files:**
- Create: `src/wllbe/render/templates/deck.html`
- Create: `src/wllbe/render/templates/slide.html`
- Create: `src/wllbe/render/templates/theme.css`
- Create: `src/wllbe/render/html_renderer.py`
- Create: `src/wllbe/render/bundle_writer.py`
- Test: `tests/unit/test_html_renderer.py`

- [ ] **Step 1: Write the failing renderer test**

```python
from wllbe.render.html_renderer import render_version


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
    assert "data-version=\"version-a\"" in html
    assert "Launch opportunity" in html
```

- [ ] **Step 2: Run the renderer test to verify it fails**

Run: `python3 -m pytest tests/unit/test_html_renderer.py -q`
Expected: FAIL because renderer and templates do not exist yet

- [ ] **Step 3: Implement minimal HTML rendering and bundle writing**

```python
def render_version(version_id: str, slides: list[RenderedSlide], style_pack: dict[str, Any]) -> str:
    slide_html = "\n".join(render_slide(slide) for slide in slides)
    return DECK_TEMPLATE.format(version_id=version_id, slide_html=slide_html, theme_css=render_theme_css(style_pack))
```

```python
def write_bundle(root: Path, manifest: dict[str, Any], version_plan: dict[str, Any], rendered_versions: dict[str, str]) -> None:
    (root / "plan.json").write_text(json.dumps(version_plan, indent=2), encoding="utf-8")
    for version_id, html in rendered_versions.items():
        version_dir = root / "versions" / version_id
        version_dir.mkdir(parents=True, exist_ok=True)
        (version_dir / "index.html").write_text(html, encoding="utf-8")
```

- [ ] **Step 4: Extend the test to assert bundle manifest output**

Add assertions for:
`bundle/manifest.json`
`plan.json`
`versions/version-a/index.html`
`versions/version-b/index.html`

- [ ] **Step 5: Run the renderer tests to verify they pass**

Run: `python3 -m pytest tests/unit/test_html_renderer.py -q`
Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add src/wllbe/render/templates/deck.html src/wllbe/render/templates/slide.html src/wllbe/render/templates/theme.css src/wllbe/render/html_renderer.py src/wllbe/render/bundle_writer.py tests/unit/test_html_renderer.py
git commit -m "feat: render versioned html decks and bundle manifest"
```

### Task 10: Add validation checks for structure, layout, rendering, and version differences

**Files:**
- Create: `src/wllbe/validation/checks.py`
- Create: `src/wllbe/validation/report.py`
- Test: `tests/unit/test_validation_checks.py`

- [ ] **Step 1: Write the failing validation test**

```python
from wllbe.validation.checks import validate_project


def test_validate_project_flags_incompatible_override():
    report = validate_project(
        slide_specs=[
            {
                "slide_id": "s1",
                "slide_purpose": "comparison",
                "deterministic_layout_override": "CMP-99",
            }
        ],
        chosen_layouts=[
            {
                "slide_id": "s1",
                "layout_code": "CMP-01",
                "layout_family": "comparison",
            }
        ],
        rendered_versions={"version-a": "<!DOCTYPE html><html><body>demo</body></html>"},
    )
    assert report.status == "failed"
    assert report.issues[0].category == "layout"
```

- [ ] **Step 2: Run the validation test to verify it fails**

Run: `python3 -m pytest tests/unit/test_validation_checks.py -q`
Expected: FAIL because validation code does not exist yet

- [ ] **Step 3: Implement structured validation categories**

```python
VALIDATION_CATEGORIES = ("content", "layout", "rendering", "versioning")
```

```python
def validate_project(
    slide_specs: list[dict[str, Any]],
    chosen_layouts: list[dict[str, Any]],
    rendered_versions: dict[str, str],
) -> ValidationReport:
    issues = []
    issues.extend(check_content_structure(slide_specs))
    issues.extend(check_layout_choices(slide_specs, chosen_layouts))
    issues.extend(check_rendered_output(rendered_versions))
    issues.extend(check_version_differences(rendered_versions))
    return ValidationReport.from_issues(issues)
```

Also persist the final report to:
`validation.json`

- [ ] **Step 4: Extend the test to cover a passing project**

Assert a valid sample project returns:
`report.status == "passed"`
and an empty `issues` list

Also assert:
`validation.json`
is written in the project root

- [ ] **Step 5: Run the validation tests to verify they pass**

Run: `python3 -m pytest tests/unit/test_validation_checks.py -q`
Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add src/wllbe/validation/checks.py src/wllbe/validation/report.py tests/unit/test_validation_checks.py
git commit -m "feat: add phase1 validation pipeline"
```

### Task 11: Wire the end-to-end CLI flow and regression fixture

**Files:**
- Modify: `src/wllbe/cli.py`
- Create: `tests/fixtures/projects/approved_chapters.json`
- Create: `tests/fixtures/projects/approved_pages.json`
- Test: `tests/e2e/test_phase1_cli.py`

- [ ] **Step 1: Write the failing end-to-end CLI test**

```python
def test_phase1_cli_generates_bundle_from_fixture(tmp_path):
    exit_code = main(
        [
            "phase1-run",
            "--brief-file", "tests/fixtures/briefs/product-launch.md",
            "--project-dir", str(tmp_path / "runs" / "launch"),
            "--provider", "fake",
            "--approved-chapters", "tests/fixtures/projects/approved_chapters.json",
            "--approved-pages", "tests/fixtures/projects/approved_pages.json",
        ]
    )
    assert exit_code == 0
    assert (tmp_path / "runs" / "launch" / "bundle" / "manifest.json").exists()
```

- [ ] **Step 2: Run the end-to-end test to verify it fails**

Run: `python3 -m pytest tests/e2e/test_phase1_cli.py -q`
Expected: FAIL because the `phase1-run` command is not fully wired yet

- [ ] **Step 3: Implement the orchestration command**

The command should perform, in order:
1. normalize brief
2. generate chapter outline
3. apply approved chapter fixture
4. generate page outline
5. apply approved page fixture
6. build slide specs
7. choose layouts
8. build version plan
9. render versions
10. validate
11. write bundle

CLI contract:

```text
python3 -m wllbe.cli phase1-run \
  --brief-file tests/fixtures/briefs/product-launch.md \
  --project-dir runs/launch \
  --provider fake \
  --approved-chapters tests/fixtures/projects/approved_chapters.json \
  --approved-pages tests/fixtures/projects/approved_pages.json
```

- [ ] **Step 4: Run the end-to-end test to verify it passes**

Run: `python3 -m pytest tests/e2e/test_phase1_cli.py -q`
Expected: PASS

- [ ] **Step 5: Run the full suite**

Run: `python3 -m pytest -q`
Expected: PASS with all unit and end-to-end tests green

- [ ] **Step 6: Commit**

```bash
git add src/wllbe/cli.py tests/fixtures/projects/approved_chapters.json tests/fixtures/projects/approved_pages.json tests/e2e/test_phase1_cli.py
git commit -m "feat: wire phase1 end-to-end generation flow"
```

### Task 12: Add operator-facing documentation for the Phase 1 workflow

**Files:**
- Modify: `README.md` if it exists, otherwise create: `README.md`

- [ ] **Step 1: Write the failing docs checklist**

Create a manual checklist in the task notes and do not implement code until all three items are documented:
1. how to run `phase1-run`
2. where to edit approved chapter/page outlines
3. how deterministic `layout_code` overrides work

- [ ] **Step 2: Add the minimum operator docs**

Document:
1. setup command
2. sample run command
3. output bundle directory structure
4. deterministic override example like `CMP-01`

- [ ] **Step 3: Verify the docs match the CLI**

Run: `python3 -m wllbe.cli phase1-run --help`
Expected: command usage matches the README exactly

- [ ] **Step 4: Commit**

```bash
git add README.md
git commit -m "docs: describe the phase1 generation workflow"
```

## Final Verification

Before declaring the plan executed, the implementer must run:

```bash
python3 -m pytest -q
python3 -m wllbe.cli phase1-run --help
```

Expected:

1. all tests pass
2. the CLI help text is readable
3. the documented bundle paths exist after the end-to-end fixture run
4. no explicit layout override is silently replaced

## Execution Order

Execute tasks in order. Do not skip ahead.

1. Task 1 establishes the package and test harness.
2. Tasks 2 through 6 establish the artifact contracts and semantic pipeline.
3. Tasks 7 and 8 establish controlled layout and style diversity.
4. Tasks 9 and 10 establish output generation and quality gates.
5. Tasks 11 and 12 make the system runnable and operable.
