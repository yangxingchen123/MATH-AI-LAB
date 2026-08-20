"""CLI for Knowledge Indexer v1.0."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .models import IndexResultKind
from .report import format_json, format_text
from .service import build_index, check_index


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m tools.knowledge_indexer",
        description=(
            "Knowledge Indexer v1.0 — derived index from validated Knowledge Metadata. "
            "Does not modify Knowledge sources."
        ),
    )
    sub = parser.add_subparsers(dest="command", required=True)

    def add_common(p: argparse.ArgumentParser) -> None:
        p.add_argument("--root", type=Path, default=None, help="Explicit project root.")
        p.add_argument("--format", choices=("text", "json"), default="text")
        p.add_argument("--summary", action="store_true")
        p.add_argument(
            "--strict-warnings",
            action="store_true",
            help="Treat Validator WARNING as failure.",
        )

    build_p = sub.add_parser("build", help="Validate then build/publish 01_知识库/_索引/.")
    add_common(build_p)

    check_p = sub.add_parser("check", help="Validate and check whether index is current (no writes).")
    add_common(check_p)

    return parser


def exit_code(op) -> int:
    if op.result in (IndexResultKind.BUILT, IndexResultKind.UP_TO_DATE, IndexResultKind.CURRENT):
        return 0
    return 1


def run(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.format == "json" and args.summary:
        parser.error("--summary cannot be combined with --format json")

    if args.command == "build":
        op = build_index(root=args.root, strict_warnings=args.strict_warnings)
    elif args.command == "check":
        op = check_index(root=args.root, strict_warnings=args.strict_warnings)
    else:
        parser.error(f"Unknown command: {args.command}")
        return 2

    if args.format == "json":
        payload = format_json(op)
        sys.stdout.write(payload if payload.endswith("\n") else payload + "\n")
    else:
        sys.stdout.write(format_text(op, summary_only=args.summary))
    return exit_code(op)


def main(argv: list[str] | None = None) -> None:
    raise SystemExit(run(argv))


if __name__ == "__main__":
    main()
