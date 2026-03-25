# wllbe Phase 1

Phase 1 is a controlled generation pipeline for turning a natural-language brief into approved outline artifacts, slide specs, versioned HTML output, and a validation report.

## Setup

Install the editable development environment:

```bash
python3 -m pip install -e '.[dev]'
```

## CLI Usage

`phase1-run --help` currently prints this exact usage line:

```text
wllbe phase1-run --brief-file <path> --project-dir <path> --provider fake --approved-chapters <path> --approved-pages <path>
```

Sample regression run:

```bash
python3 -m wllbe.cli phase1-run \
  --brief-file tests/fixtures/briefs/product-launch.md \
  --project-dir runs/launch \
  --provider fake \
  --approved-chapters tests/fixtures/projects/approved_chapters.json \
  --approved-pages tests/fixtures/projects/approved_pages.json
```

## Approved Outline Files

`phase1-run` expects the operator to pass two reviewed JSON files:

- `--approved-chapters`: chapter outline chosen for downstream page generation
- `--approved-pages`: page outline chosen for downstream slide-spec generation

For the built-in regression flow, edit these files:

- `tests/fixtures/projects/approved_chapters.json`
- `tests/fixtures/projects/approved_pages.json`

For project-specific runs, prepare JSON files with the same shape and pass those paths instead.

## Deterministic Layout Overrides

Deterministic layout selection lives in the approved page outline, not in the renderer. Add a required `layout_code` hint to `layout_hints` when a page must bind to a specific human-facing layout code such as `CMP-01`.

```json
{
  "page_id": "p1",
  "chapter_id": "c1",
  "title": "The market is fragmented",
  "message": "Teams are stuck stitching together too many tools.",
  "content_blocks": [
    {
      "type": "bullets",
      "items": ["Tool sprawl", "Slow handoffs"]
    }
  ],
  "layout_hints": [
    "comparison",
    {
      "layout_code": "CMP-01",
      "strength": "required"
    }
  ]
}
```

If the requested layout is incompatible with the slide spec, the run fails with a clear error. It is not silently replaced.

## Output Bundle

After a successful run, `--project-dir` contains:

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

Use `validation.json` to inspect content, layout, rendering, and versioning issues. Use `bundle/manifest.json` to inspect selected layouts, selected style packs, and rendered version paths.
