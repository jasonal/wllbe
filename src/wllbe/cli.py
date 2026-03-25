from __future__ import annotations


def main(argv: list[str] | None = None) -> int:
    argv = argv or []
    if not argv:
        print("wllbe <command>")
        return 1
    print(f"unknown command: {argv[0]}")
    return 2
