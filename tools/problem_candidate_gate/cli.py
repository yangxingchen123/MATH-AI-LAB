"""CLI for Problem Candidate Gate v0.1. Read-only; no auto-fix, no ID allocation."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .discovery import DiscoveryError
from .readiness import check_file, check_project, status_project
from .report import format_json, format_text


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m tools.problem_candidate_gate",
        description=(
            "Problem Candidate Gate v0.1 — temporary pre-freeze quality gate "
            "for Problem Schema v1 Candidate. Not Problem Validator v1. "
            "Read-only: no --fix, no ID allocation, no status mutation."
        ),
    )
    sub = parser.add_subparsers(dest="command", required=True)

    def add_common(p: argparse.ArgumentParser) -> None:
        p.add_argument(
            "--root",
            type=Path,
            default=None,
            help="Explicit MATH-AI-LAB project root.",
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
            help="Include INFO issues.",
        )

    check = sub.add_parser("check", help="Mechanical Candidate check for all Problems under 02_题目库/.")
    add_common(check)

    check_file_p = sub.add_parser(
        "check-file",
        help="Mechanical check for one file with full Problem candidate context.",
    )
    check_file_p.add_argument("path", type=Path, help="Path to a Problem Markdown file.")
    add_common(check_file_p)

    status = sub.add_parser(
        "status",
        help="Candidate readiness: mechanical gates + manual review checklist.",
    )
    add_common(status)

    return parser


def exit_code(command: str, result) -> int:
    if command == "status":
        return 0 if result.readiness in {"READY_FOR_FINAL_REVIEW", "READY_WITH_WARNINGS"} else 1
    return 1 if result.summary.errors > 0 else 0


def run(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.format == "json" and args.summary:
        parser.error("--summary cannot be combined with --format json")

    include_readiness = args.command == "status"
    try:
        if args.command == "check":
            result = check_project(root=args.root, verbose=args.verbose)
        elif args.command == "check-file":
            result = check_file(args.path, root=args.root, verbose=args.verbose)
        else:
            result = status_project(root=args.root, verbose=args.verbose)
    except DiscoveryError as exc:
        sys.stderr.write(f"{exc.rule_id}: {exc.message}\n")
        return 1

    if args.format == "json":
        sys.stdout.write(format_json(result, include_readiness=include_readiness) + "\n")
    else:
        sys.stdout.write(
            format_text(
                result,
                summary_only=args.summary,
                verbose=args.verbose,
                include_readiness=include_readiness,
            )
        )
    return exit_code(args.command, result)


def main() -> None:
    sys.exit(run())
