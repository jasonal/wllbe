# wllbe Phase 1 Design

Date: 2026-03-25
Status: Draft for review

## Goal

Build the first phase of `wllbe` as a controllable generation system that proves one core capability:

```text
Natural-language brief -> approved outline -> approved page plan -> versioned HTML PPT output
```

This phase does not attempt to deliver the full `wllbe` product. It focuses on making content generation, page planning, layout selection, and versioned rendering stable enough to support later review and publishing workflows.

## Problem Statement

The long-term `wllbe` direction is a general-purpose HTML PPT system where:

1. Content can be generated from natural-language requests.
2. Presentation diversity comes from independently evolving layout and style systems.
3. The same approved content can produce multiple high-quality deck versions.
4. Later phases can support browser-based card-pick review and publishing without redefining the generation core.

The main risk is coupling content, layout, and style too early. If these concerns are mixed together in the first version, future tuning becomes difficult:

1. Content quality issues become tangled with layout issues.
2. Layout-library expansion becomes expensive and brittle.
3. Version generation becomes noisy instead of intentional.
4. Later review tooling must work with opaque outputs rather than structured artifacts.

## Phase 1 Scope

Phase 1 is limited to the generation core.

### In Scope

1. Parse a natural-language brief into structured generation inputs.
2. Generate a chapter-level outline for human approval.
3. Generate a page-level outline for human approval.
4. Convert approved page plans into a neutral `slide spec` contract.
5. Match slide specs against a layout library.
6. Apply style and motion packs after layout selection.
7. Generate multiple HTML PPT versions from the same approved content.
8. Produce structured validation results for content, layout, and rendering quality.
9. Output a standard deck bundle that later phases can consume.

### Out of Scope

1. Browser-based card-pick review UI.
2. Final mixed-deck assembly from per-page selections.
3. Docker publishing platform.
4. Sharing, management, and distribution APIs.
5. Learned large-scale layout generation beyond the contract needed to support it later.
6. Automatic quality ranking across finished deck versions beyond basic validation and fit scoring.

## Architecture

Phase 1 uses a three-layer generation architecture:

```text
Content layer -> Layout layer -> Style / motion layer
```

### Content Layer

Owns meaning, narrative structure, and page intent.

Responsibilities:

1. Parse the raw brief.
2. Produce chapter outline candidates.
3. Refine the approved chapter outline into page-level plans.
4. Convert approved page plans into `slide spec` objects.

This layer must remain semantic-first. It should not encode layout geometry, colors, font choices, or animation implementation details.

### Layout Layer

Owns spatial organization and slot assignment.

Responsibilities:

1. Store layout-library metadata and layout contracts.
2. Filter layouts by hard compatibility rules.
3. Rank compatible layouts by fit.
4. Select layouts according to explicit overrides, deck-recipe rules, and automatic ranking.

The layout layer determines how content blocks are placed, not what the content means.

### Style / Motion Layer

Owns visual identity after layout has been chosen.

Responsibilities:

1. Apply palette, typography, shape language, and motion profile.
2. Render multiple coherent versions from the same content and layout strategy.
3. Keep style decisions swappable without changing content structures.

This layer must not redefine content structure or layout compatibility.

## Workflow

Phase 1 uses a gated two-stage outline process before rendering:

```text
Natural-language brief
-> chapter outline
-> human approval
-> page outline
-> human approval
-> slide spec generation
-> layout matching
-> style application
-> versioned HTML output
```

The review gates are required. `wllbe` should not be designed as a black-box generator that goes directly from brief to final deck without human checkpoints.

## Core Artifacts

### 1. Brief

The raw user request plus normalized fields extracted from it.

Expected fields:

1. `goal`
2. `audience`
3. `tone`
4. `constraints`
5. `page_budget`
6. `source_materials`

### 2. Chapter Outline

A high-level narrative structure for human review.

Expected fields:

1. `chapter_id`
2. `title`
3. `intent`
4. `key_points`
5. `estimated_pages`

### 3. Page Outline

A page-level plan derived from the approved chapter outline.

Expected fields:

1. `page_id`
2. `chapter_id`
3. `title`
4. `message`
5. `content_blocks`
6. `layout_hints`

`layout_hints` may exist here, but they are advisory rather than binding unless explicitly promoted into a deterministic override.

### 4. Slide Spec

`slide spec` is the core contract between the content layer and the layout layer.

It represents one final slide in a layout- and style-independent way.

Expected fields:

1. `slide_id`
2. `chapter_id`
3. `sequence`
4. `slide_purpose`
5. `content_blocks`
6. `priority_metadata`
7. `density_metadata`
8. `visual_intent_tags`
9. `hard_constraints`
10. `deterministic_layout_override` (optional)

Examples of supported `slide_purpose` values:

1. `cover`
2. `section`
3. `comparison`
4. `timeline`
5. `data`
6. `quote`
7. `summary`
8. `ending`

Examples of supported `content_blocks`:

1. `heading`
2. `subheading`
3. `bullets`
4. `metric`
5. `image_slot`
6. `chart_slot`
7. `quote`
8. `callout`
9. `table`

### Slide Spec Design Rule

`slide spec` must include:

1. Semantic intent.
2. Content hierarchy.
3. Block types and payloads.
4. Emphasis and density metadata.
5. Hard rendering constraints.

`slide spec` must not include:

1. Absolute coordinates.
2. Specific colors or font families.
3. Theme-specific styling decisions.
4. Animation implementation details.
5. Template filenames as core semantic data.

This rule preserves the independence of the layout and style layers.

## Layout Library

The layout library is not just a folder of HTML templates. It is a searchable capability index with rendering assets behind it.

Each layout must expose metadata that allows reliable matching.

Required metadata:

1. `layout_id`
2. `layout_code`
3. `layout_label`
4. `layout_family`
5. `supported_purposes`
6. `slot_schema`
7. `capacity_rules`
8. `visual_rhythm_tags`
9. `style_compatibility`
10. `status`

### Dual Identifier Model

Every layout has two identifiers with different purposes:

1. `layout_id`
   - Internal canonical identifier.
   - Stable for code, data references, migrations, and ranking.
   - Must not change when human-facing names change.

2. `layout_code`
   - Human-facing deterministic code.
   - Used in prompts, configs, design reviews, and explicit page overrides.
   - Recommended format uses semantic family prefixes, for example:
     - `COV-01`
     - `SEC-03`
     - `CMP-12`
     - `DAT-07`

`layout_label` provides a human-readable description such as "Hero Left Image" or "Three Metrics Grid", but it is not a stable API surface.

### Deterministic Layout Control

Phase 1 must support deterministic layout selection, not only automatic matching.

Selection precedence:

1. Explicit page-level override.
2. Deck-recipe rule.
3. Automatic ranking among compatible layouts.

If a user or config explicitly chooses a layout code for a page, the system must not silently replace it with a different layout. If the chosen layout is incompatible, generation should fail with a clear compatibility error.

## Version Generation Strategy

Multiple deck versions should come from controlled variation, not page-level randomness.

Recommended model:

```text
Approved slide specs
-> compatible layout candidates
-> deck recipe
-> style / motion pack
-> versioned rendered decks
```

### Deck Recipe

A deck recipe is a control layer above per-slide layout matching.

It defines coherent presentation behavior for a whole deck, such as:

1. Global tone.
2. Allowed layout families.
3. Preferred density range.
4. Motion intensity.
5. Treatment rules for cover, section, comparison, data, and ending slides.

This keeps each generated version internally coherent.

### Why Not Full Randomness

Fully random per-slide assembly is explicitly rejected because it tends to:

1. Break deck-level coherence.
2. Produce noisy differences that are hard to compare.
3. Make later human review more cluttered.
4. Obscure whether quality changes come from content, layout, or style choices.

## Validation and Quality Gates

Phase 1 is complete only if generation outputs can be validated in a repeatable way.

### 1. Content Structure Validation

Checks:

1. Approved chapter outline expands cleanly into a full page outline.
2. Every page outline converts into a valid `slide spec`.
3. No pages are empty, untyped, or missing a primary message.

### 2. Layout Compatibility Validation

Checks:

1. Every `slide spec` matches at least one valid layout.
2. Every explicit `layout_code` override is checked against slot and capacity rules.
3. Incompatible explicit layout choices cause a clear error, not a silent fallback.

### 3. Rendering Validation

Checks:

1. No unresolved slots remain after layout binding.
2. No required visual assets are missing.
3. No text overflows exceed defined limits.
4. Required theme variables and motion settings are present.

### 4. Version Difference Validation

Checks:

1. Generated versions are meaningfully different.
2. Differences come from deck recipes, layout choices, style packs, or motion profiles.
3. Cosmetic micro-variation alone does not count as a new version.

Validation output should be structured so failures can be attributed to the correct layer:

1. content
2. layout
3. rendering
4. versioning

## Output Contract

Phase 1 should output a standard deck bundle rather than only raw HTML files.

Recommended bundle contents:

1. approved `chapter outline`
2. approved `page outline`
3. normalized `slide spec` set
4. selected layout records for each version
5. selected style / motion packs for each version
6. validation report
7. rendered versioned HTML decks

This bundle becomes the handoff point for later phases.

## Relationship to Later Review and Publishing

Phase 1 does not implement the card-pick review flow, but it must prepare for it.

The most important requirement is that later review should operate on structured, explainable generation outputs rather than opaque HTML blobs.

That means later phases should be able to consume:

1. one fixed content model
2. multiple coherent rendered versions
3. explicit layout and style decisions per version

This keeps future review and publishing systems separate from the generation engine while allowing them to interoperate cleanly.

## Non-Goals

Phase 1 is not trying to solve:

1. the final end-user review experience
2. deployment and publishing operations
3. large learned layout generation pipelines
4. advanced ranking or recommendation across many candidate decks

These belong to later phases once the generation contract is stable.

## Acceptance Criteria

Phase 1 is successful when all of the following are true:

1. A natural-language brief can produce a chapter outline for human review.
2. The approved chapter outline can produce a page outline for human review.
3. The approved page outline can produce valid `slide spec` objects.
4. Each `slide spec` can be matched to compatible layouts using the layout-library metadata contract.
5. Deterministic layout overrides by human-facing `layout_code` are supported and validated.
6. At least two or three deck versions can be rendered from the same approved content using controlled recipe-level variation.
7. Validation reports can distinguish content, layout, rendering, and versioning failures.
8. The output bundle is structured enough to support future card-pick review and publishing phases without redefining the core contracts.

## Open Follow-On Work

This spec intentionally stops at the Phase 1 design boundary. The next planning cycle should break implementation into workstreams such as:

1. brief and outline generation pipeline
2. `slide spec` schema and conversion logic
3. layout-library metadata model
4. deck recipe and version generation logic
5. renderer and validation pipeline
6. output bundle contract

Those workstreams belong in the implementation plan, not in this design spec.
