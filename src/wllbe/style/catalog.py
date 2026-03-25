from dataclasses import dataclass
from pathlib import Path
import json


@dataclass(frozen=True)
class StylePackRecord:
    style_pack_id: str
    label: str
    tokens: dict
    motion_profile: dict
    status: str


@dataclass(frozen=True)
class RecipeRecord:
    recipe_id: str
    label: str
    allowed_layout_families: tuple[str, ...]
    motion_intensity: str
    density_target: str


def _load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def load_style_catalog(root: Path) -> list[StylePackRecord]:
    entries: list[StylePackRecord] = []
    for file in sorted(root.iterdir()):
        if file.suffix != ".json":
            continue
        payload = _load_json(file)
        entries.append(StylePackRecord(**payload))
    return entries


def load_recipe_catalog(root: Path) -> list[RecipeRecord]:
    entries: list[RecipeRecord] = []
    for file in sorted(root.iterdir()):
        if file.suffix != ".json":
            continue
        payload = _load_json(file)
        payload["allowed_layout_families"] = tuple(payload.get("allowed_layout_families", []))
        entries.append(RecipeRecord(**payload))
    return entries
