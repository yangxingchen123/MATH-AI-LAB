"""CLI for Knowledge Workflow v1.0."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .constants import (
    RESULT_HEALTHY,
    RESULT_SUCCESS,
)
from .report import format_json, format_text
from .service import check_file_workflow, status, sync_file


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m tools.knowledge_workflow",
        description=(
            "Knowledge Workflow v1.0 — orchestrates Validator v1.1 and Indexer v1.0. "
            "Does not auto-fix, allocate IDs, or change reviewed status."
        ),
    )
    sub = parser.add_subparsers(dest="command", required=True)

    def add_common(p: argparse.ArgumentParser) -> None:
        p.add_argument("--root", type=Path, default=None)
        p.add_argument("--format", choices=("text", "json"), default="text")
        p.add_argument("--summary", action="store_true")
        p.add_argument("--strict-warnings", action="store_true")

    sync_p = sub.add_parser("sync", help="check-file → full check → index build")
    sync_p.add_argument("path", type=Path)
    add_common(sync_p)

    check_p = sub.add_parser("check", help="check-file → full check → index stale check (read-only)")
    check_p.add_argument("path", type=Path)
    add_common(check_p)

    status_p = sub.add_parser("status", help="full validation → index check (read-only)")
    add_common(status_p)

    return parser


def exit_code(result) -> int:
    if result.result in (RESULT_SUCCESS, RESULT_HEALTHY):
        return 0
    return 1


def run(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.format == "json" and args.summary:
        parser.error("--summary cannot be combined with --format json")

    if args.command == "sync":
        result = sync_file(args.path, root=args.root, strict_warnings=args.strict_warnings)
    elif args.command == "check":
        result = check_file_workflow(args.path, root=args.root, strict_warnings=args.strict_warnings)
    elif args.command == "status":
        result = status(root=args.root, strict_warnings=args.strict_warnings)
    else:
        parser.error(f"Unknown command: {args.command}")
        return 2

    if args.format == "json":
        payload = format_json(result)
        sys.stdout.write(payload if payload.endswith("\n") else payload + "\n")
    else:
        sys.stdout.write(format_text(result, summary_only=args.summary))
    return exit_code(result)


def main(argv: list[str] | None = None) -> None:
    raise SystemExit(run(argv))


if __name__ == "__main__":
    main()
