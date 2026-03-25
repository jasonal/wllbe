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


def _version_id(index: int) -> str:
    if index >= 26:
        raise ValueError("version_count exceeds supported range")
    label = chr(ord("a") + index)
    return f"version-{label}"


def build_version_plan(version_count: int) -> list[VersionPlan]:
    if version_count <= 0:
        raise ValueError("version_count must be positive")

    catalog_root = Path.cwd() / "catalog"
    style_catalog = catalog.load_style_catalog(catalog_root / "styles")
    recipe_catalog = catalog.load_recipe_catalog(catalog_root / "recipes")

    if len(style_catalog) < version_count or len(recipe_catalog) < version_count:
        raise ValueError("not enough styles or recipes to build plan")

    plans: list[VersionPlan] = []
    for idx in range(version_count):
        recipe = recipe_catalog[idx]
        style = style_catalog[idx]
        plan = VersionPlan(
            version_id=_version_id(idx),
            recipe_id=recipe.recipe_id,
            style_pack_id=style.style_pack_id,
            allowed_layout_families=recipe.allowed_layout_families,
            motion_intensity=recipe.motion_intensity,
            density_target=recipe.density_target,
        )
        plans.append(plan)
    return plans
