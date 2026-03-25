from __future__ import annotations

import sys


def main(argv: list[str] | None = None) -> int:
    argv = argv or []
    if not argv:
        print("wllbe <command>")
        return 1
    print(f"unknown command: {argv[0]}")
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
