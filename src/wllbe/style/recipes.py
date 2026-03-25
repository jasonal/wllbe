from dataclasses import dataclass
from pathlib import Path

from . import catalog


@dataclass(frozen=True)
class VersionPlan:
    version_id: str
    recipe_id: str
    style_pack_id: str
    allowed_layout_families: tuple[str, ...]
    motion_intensity: str
    density_target: str


REPO_ROOT = Path(__file__).resolve().parents[3]
CATALOG_ROOT = REPO_ROOT / "catalog"


def _version_label(index: int) -> str:
    if index < 0:
        raise ValueError("index must be non-negative")

    parts: list[str] = []
    value = index
    while True:
        parts.insert(0, chr(ord("a") + (value % 26)))
        value = value // 26 - 1
        if value < 0:
            break
    return "".join(parts)


def build_version_plan(version_count: int) -> list[VersionPlan]:
    if version_count <= 0:
        raise ValueError("version_count must be positive")

    style_catalog = catalog.load_style_catalog(CATALOG_ROOT / "styles")
    recipe_catalog = catalog.load_recipe_catalog(CATALOG_ROOT / "recipes")

    sorted_recipes = sorted(recipe_catalog, key=lambda recipe: recipe.recipe_id)
    if len(sorted_recipes) < version_count:
        raise ValueError("not enough recipes to build plan")

    style_map = {style.style_pack_id: style for style in style_catalog}

    plans: list[VersionPlan] = []
    for idx in range(version_count):
        recipe = sorted_recipes[idx]
        style = style_map.get(recipe.preferred_style_pack_id)
        if style is None:
            raise ValueError(
                f"recipe {recipe.recipe_id} references missing style "
                f"{recipe.preferred_style_pack_id}"
            )
        plans.append(
            VersionPlan(
                version_id=f"version-{_version_label(idx)}",
                recipe_id=recipe.recipe_id,
                style_pack_id=style.style_pack_id,
                allowed_layout_families=recipe.allowed_layout_families,
                motion_intensity=recipe.motion_intensity,
                density_target=recipe.density_target,
            )
        )
    return plans
