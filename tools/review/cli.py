"""CLI for v1.7 defect scanning."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .detect import scan_tree


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="python -m tools.review")
    parser.add_argument("root")
    return parser


def main(argv: list[str] | None = None) -> int:
    try:
        return run(argv)
    except SystemExit as exc:
        if exc.code is None:
            return 0
        if isinstance(exc.code, int):
            return exc.code
        return 1


def run(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    findings = scan_tree(Path(args.root))
    sys.stdout.write(json.dumps([item.__dict__ for item in findings], indent=2) + "\n")
    return 1 if any(item.severity == "BLOCKING" for item in findings) else 0


if __name__ == "__main__":
    raise SystemExit(main())
