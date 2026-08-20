"""CLI for the MATH-AI-LAB Verification Contract."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .profiles import PROFILE_ALL, PROFILE_CORE, PROFILE_LATEX_SMOKE
from .report import exit_code, format_report
from .runner import VerificationUsageError, run_verification


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m tools.verification",
        description="Unified verification contract for local runs, Agent closeout, and GitHub Actions.",
    )
    parser.add_argument("--verbose", action="store_true", help="Show environment and check details.")
    parser.add_argument("--root", type=Path, default=None, help="Explicit repository root.")
    sub = parser.add_subparsers(dest="profile", required=True)
    sub.add_parser(PROFILE_CORE, help="Source + derived + pytest (read-only).")
    latex = sub.add_parser(PROFILE_LATEX_SMOKE, help="LaTeX check smoke (no publish).")
    latex.add_argument("project", type=str, help="LaTeX project directory under 04_LATEX/.")
    all_p = sub.add_parser(PROFILE_ALL, help="core + latex-smoke.")
    all_p.add_argument("project", type=str, help="LaTeX project directory under 04_LATEX/.")
    return parser


def run(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    latex_project = getattr(args, "project", None)
    try:
        result = run_verification(
            args.profile,
            root=args.root,
            latex_project=latex_project,
            verbose=args.verbose,
        )
    except VerificationUsageError as exc:
        parser.error(str(exc))
        return 2
    text = format_report(result, verbose=args.verbose)
    sys.stdout.write(text if text.endswith("\n") else text + "\n")
    return exit_code(result)


def main(argv: list[str] | None = None) -> None:
    raise SystemExit(run(argv))


if __name__ == "__main__":
    main()
