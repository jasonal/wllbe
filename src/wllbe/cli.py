from __future__ import annotations

import sys
from pathlib import Path

from wllbe.projects.store import ProjectStore


APPROVE_USAGE = "wllbe approve <chapters|pages> --project <path> --input <path>"


def _run_approve(argv: list[str]) -> int:
    if not argv:
        print(APPROVE_USAGE)
        return 1

    target = argv[0]
    artifact_name: str | None = None
    if target == "chapters":
        artifact_name = "chapter-outline"
    elif target == "pages":
        artifact_name = "page-outline"
    else:
        print(f"unknown approve target: {target}")
        return 2

    project: str | None = None
    input_path: str | None = None
    i = 1
    while i < len(argv):
        token = argv[i]
        if token == "--project" and i + 1 < len(argv):
            project = argv[i + 1]
            i += 2
            continue
        if token == "--input" and i + 1 < len(argv):
            input_path = argv[i + 1]
            i += 2
            continue
        print(APPROVE_USAGE)
        return 1

    if project is None or input_path is None:
        print(APPROVE_USAGE)
        return 1

    store = ProjectStore(Path(project))
    try:
        store.approve_artifact(artifact_name, Path(input_path))
    except (ValueError, OSError) as exc:
        print(f"approval failed: {exc}", file=sys.stderr)
        return 1

    return 0


def main(argv: list[str] | None = None) -> int:
    argv = argv or []
    if not argv:
        print("wllbe <command>")
        return 1
    if argv[0] == "approve":
        return _run_approve(argv[1:])
    print(f"unknown command: {argv[0]}")
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
