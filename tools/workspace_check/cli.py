"""CLI for Workspace Check v1."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .checker import run_workspace_check
from .report import format_text


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m tools.workspace_check",
        description="Workspace Check v1 — read-only repository consistency checks.",
    )
    sub = parser.add_subparsers(dest="command", required=True)
    check_p = sub.add_parser("check", help="Run workspace checks (read-only).")
    check_p.add_argument("--root", type=Path, default=None, help="Explicit project root.")
    return parser


def run(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command != "check":
        parser.error(f"Unknown command: {args.command}")
        return 2
    result = run_workspace_check(root=args.root)
    sys.stdout.write(format_text(result))
    return 1 if result.error_count > 0 else 0


def main(argv: list[str] | None = None) -> None:
    raise SystemExit(run(argv))


if __name__ == "__main__":
    main()
