from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def write_bundle(
    root: Path,
    manifest: dict[str, Any],
    version_plan: dict[str, Any],
    rendered_versions: dict[str, str],
) -> None:
    """Write the plan, manifest, and rendered HTML versions for a bundle."""
    root.mkdir(parents=True, exist_ok=True)
    (root / "plan.json").write_text(json.dumps(version_plan, indent=2), encoding="utf-8")

    bundle_dir = root / "bundle"
    bundle_dir.mkdir(parents=True, exist_ok=True)
    (bundle_dir / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    versions_dir = root / "versions"
    versions_dir.mkdir(parents=True, exist_ok=True)
    for version_id, html in rendered_versions.items():
        version_dir = versions_dir / version_id
        version_dir.mkdir(parents=True, exist_ok=True)
        (version_dir / "index.html").write_text(html, encoding="utf-8")
