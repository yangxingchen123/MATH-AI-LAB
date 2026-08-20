"""CLI for Problem Validator v1."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .discovery import DiscoveryError
from .report import format_json, format_text
from .validator import discovery_error_result, validate_file, validate_project


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m tools.problem_validator",
        description=(
            "Problem Metadata Validator v1 "
            "(validates Frozen Problem Schema v1). Read-only; dependency-aware."
        ),
    )
    sub = parser.add_subparsers(dest="command", required=True)

    def add_common(p: argparse.ArgumentParser) -> None:
        p.add_argument(
            "--root",
            type=Path,
            default=None,
            help="Explicit MATH-AI-LAB project root (must contain 元数据规范.md and 01_知识库/).",
        )
        p.add_argument(
            "--format",
            choices=("text", "json"),
            default="text",
            help="Output format (default: text).",
        )
        p.add_argument(
            "--summary",
            action="store_true",
            help="Text summary only (incompatible with --format json).",
        )
        p.add_argument(
            "--verbose",
            action="store_true",
            help="Include INFO issues and extra document listing.",
        )
        p.add_argument(
            "--strict-warnings",
            action="store_true",
            help="Treat WARNING as failure for exit code (severity unchanged).",
        )

    check = sub.add_parser(
        "check",
        help="Validate Knowledge dependency and all Problems under 02_题目库/.",
    )
    add_common(check)

    check_file = sub.add_parser(
        "check-file",
        help="Validate one file with full Problem registry and Knowledge context.",
    )
    check_file.add_argument("path", type=Path, help="Path to a Problem Markdown file.")
    add_common(check_file)

    return parser


def exit_code(result, *, strict_warnings: bool) -> int:
    if result.summary.errors > 0:
        return 1
    if strict_warnings and result.summary.warnings > 0:
        return 1
    return 0


def run(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.format == "json" and args.summary:
        parser.error("--summary cannot be combined with --format json")

    try:
        if args.command == "check":
            result = validate_project(root=args.root)
        elif args.command == "check-file":
            result = validate_file(args.path, root=args.root)
        else:
            parser.error(f"Unknown command: {args.command}")
            return 2
    except DiscoveryError as exc:
        result = discovery_error_result(exc, args.root)
        if args.format == "json":
            sys.stdout.write(format_json(result))
        else:
            sys.stdout.write(format_text(result, summary_only=args.summary, verbose=args.verbose))
        return 1

    if args.format == "json":
        payload = format_json(result)
        sys.stdout.write(payload if payload.endswith("\n") else payload + "\n")
    else:
        sys.stdout.write(
            format_text(result, summary_only=args.summary, verbose=args.verbose)
        )

    return exit_code(result, strict_warnings=args.strict_warnings)


def main(argv: list[str] | None = None) -> None:
    raise SystemExit(run(argv))


if __name__ == "__main__":
    main()
