"""CLI for LaTeX build automation."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .report import exit_code, format_report
from .resolver import LatexBuildError
from .service import build_latex_project, check_latex_project


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m tools.latex_build",
        description="LaTeX build, inspection, and formal artifact publishing for MATH-AI-LAB.",
    )
    sub = parser.add_subparsers(dest="command", required=True)
    for name, help_text in (
        ("check", "Compile and inspect without publishing formal PDF."),
        ("build", "Compile, inspect, and publish formal PDF when allowed."),
    ):
        p = sub.add_parser(name, help=help_text)
        p.add_argument("project", type=str, help="LaTeX project directory under 04_LATEX/.")
        p.add_argument("--root", type=Path, default=None, help="MATH-AI-LAB repository root.")
    return parser


def run(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "check":
            result = check_latex_project(args.project, repo_root=args.root)
            print(format_report(result, mode="check"))
            return exit_code(result)
        if args.command == "build":
            result = build_latex_project(args.project, repo_root=args.root)
            print(format_report(result, mode="build"))
            return exit_code(result)
    except LatexBuildError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    parser.error(f"Unknown command: {args.command}")
    return 2


def main() -> None:
    raise SystemExit(run())
