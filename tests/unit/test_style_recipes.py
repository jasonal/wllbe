import json
from pathlib import Path

import pytest

from wllbe.style import catalog, recipes


def _write_json(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def test_load_style_catalog_reads_every_style(tmp_path: Path) -> None:
    style_dir = tmp_path / "styles"
    style_dir.mkdir()
    _write_json(
        style_dir / "clean-light.json",
        {
            "style_pack_id": "clean-light",
            "label": "Clean Light",
            "tokens": {"accent": "#ffffff"},
            "motion_profile": {"pace": "calm"},
            "status": "published",
        },
    )
    _write_json(
        style_dir / "dark-tech.json",
        {
            "style_pack_id": "dark-tech",
            "label": "Dark Tech",
            "tokens": {"accent": "#00ffcc"},
            "motion_profile": {"pace": "energetic"},
            "status": "preview",
        },
    )

    styles = catalog.load_style_catalog(style_dir)

    assert [style.style_pack_id for style in styles] == ["clean-light", "dark-tech"]
    assert styles[0].motion_profile["pace"] == "calm"
    assert styles[1].status == "preview"


def test_load_recipe_catalog_reads_every_recipe(tmp_path: Path) -> None:
    recipe_dir = tmp_path / "recipes"
    recipe_dir.mkdir()
    _write_json(
        recipe_dir / "neutral-balanced.json",
        {
            "recipe_id": "neutral-balanced",
            "label": "Neutral Balanced",
            "allowed_layout_families": ["text-led"],
            "motion_intensity": "low",
            "density_target": "medium",
        },
    )
    _write_json(
        recipe_dir / "bold-contrast.json",
        {
            "recipe_id": "bold-contrast",
            "label": "Bold Contrast",
            "allowed_layout_families": ["burst-grid"],
            "motion_intensity": "high",
            "density_target": "dense",
        },
    )

    recipes_list = catalog.load_recipe_catalog(recipe_dir)

    assert [recipe.recipe_id for recipe in recipes_list] == ["bold-contrast", "neutral-balanced"]
    assert recipes_list[0].motion_intensity == "high"
    assert recipes_list[1].density_target == "medium"


def test_build_version_plan_pairs_recipes_and_styles(monkeypatch: pytest.MonkeyPatch) -> None:
    styles = [
        catalog.StylePackRecord(
            style_pack_id="zebra",
            label="Zebra",
            tokens={"accent": "#000"},
            motion_profile={"pace": "fast"},
            status="draft",
        ),
        catalog.StylePackRecord(
            style_pack_id="alpha",
            label="Alpha",
            tokens={"accent": "#fff"},
            motion_profile={"pace": "calm"},
            status="published",
        ),
    ]
    recipes_data = [
        catalog.RecipeRecord(
            recipe_id="zebra-roll",
            label="Zebra Roll",
            allowed_layout_families=("panel",),
            motion_intensity="high",
            density_target="dense",
        ),
        catalog.RecipeRecord(
            recipe_id="alpha-card",
            label="Alpha Card",
            allowed_layout_families=("panel", "grid"),
            motion_intensity="calm",
            density_target="balanced",
        ),
    ]

    monkeypatch.setattr(catalog, "load_style_catalog", lambda _: styles)
    monkeypatch.setattr(catalog, "load_recipe_catalog", lambda _: recipes_data)

    plan = recipes.build_version_plan(2)

    assert plan[0].version_id == "version-a"
    assert plan[0].recipe_id == "zebra-roll"
    assert plan[0].style_pack_id == "zebra"
    assert plan[1].version_id == "version-b"
    assert plan[1].recipe_id == "alpha-card"
    assert plan[1].style_pack_id == "alpha"
    assert plan[1].allowed_layout_families == ("panel", "grid")
    assert plan[1].motion_intensity == "calm"


def test_build_version_plan_requires_sufficient_items(monkeypatch: pytest.MonkeyPatch) -> None:
    single_style = catalog.StylePackRecord(
        style_pack_id="solo",
        label="Solo",
        tokens={},
        motion_profile={},
        status="published",
    )
    single_recipe = catalog.RecipeRecord(
        recipe_id="solo-recipe",
        label="Solo Recipe",
        allowed_layout_families=("panel",),
        motion_intensity="medium",
        density_target="medium",
    )

    monkeypatch.setattr(catalog, "load_style_catalog", lambda _: [single_style])
    monkeypatch.setattr(catalog, "load_recipe_catalog", lambda _: [single_recipe])

    with pytest.raises(ValueError):
        recipes.build_version_plan(2)
