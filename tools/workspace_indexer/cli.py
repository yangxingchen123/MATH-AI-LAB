"""CLI for Workspace Indexer v1.5."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .models import IndexResultKind
from .report import format_text
from .service import check_index, rebuild_index, sync_index


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m tools.workspace_indexer",
        description=(
            "Workspace Indexer v1.5 — derived views from validated Knowledge/Problem/Attempt/Method "
            "and filesystem. Includes Descriptive Evidence and Knowledge Associated Evidence projection."
        ),
    )
    sub = parser.add_subparsers(dest="command", required=True)
    for name, help_text in (
        ("check", "Validate then compare generated index (read-only)."),
        ("rebuild", "Validate then rebuild 09_长期记忆/自动索引/."),
        ("sync", "Validate then publish generated views only when stale or missing."),
    ):
        p = sub.add_parser(name, help=help_text)
        p.add_argument("--root", type=Path, default=None, help="Explicit project root.")
    return parser


def exit_code(op) -> int:
    if op.result in (IndexResultKind.BUILT, IndexResultKind.UP_TO_DATE, IndexResultKind.CURRENT):
        return 0
    return 1


def run(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "check":
        op = check_index(root=args.root)
    elif args.command == "rebuild":
        op = rebuild_index(root=args.root)
    elif args.command == "sync":
        op = sync_index(root=args.root)
    else:
        parser.error(f"Unknown command: {args.command}")
        return 2
    sys.stdout.write(format_text(op, command=args.command))
    return exit_code(op)


def main(argv: list[str] | None = None) -> None:
    raise SystemExit(run(argv))


if __name__ == "__main__":
    main()
