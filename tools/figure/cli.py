"""CLI for the v1.5 figure framework."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .doctor import doctor
from .gate import evaluate_gate
from .manifest import validate_manifest_file
from .renderer import (
    render_architecture,
    render_exact_function,
    render_network,
    render_numerical,
    render_sensitivity,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="python -m tools.figure")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("doctor")
    sub.add_parser("gate")
    val = sub.add_parser("validate-manifest")
    val.add_argument("--path", required=True)
    render = sub.add_parser("render")
    render.add_argument(
        "--family",
        required=True,
        choices=["numerical", "network", "function", "architecture", "sensitivity"],
    )
    render.add_argument("--output", required=True)
    render.add_argument("--run-id", default="pilot-run")
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
    if args.command == "doctor":
        report = doctor()
        sys.stdout.write(json.dumps(report, indent=2, sort_keys=True) + "\n")
        return 0 if report["status"] == "PASS" else 1
    if args.command == "gate":
        report = evaluate_gate()
        sys.stdout.write(json.dumps(report, indent=2, sort_keys=True) + "\n")
        return 0 if report["status"] == "PASS" else 1
    if args.command == "validate-manifest":
        result = validate_manifest_file(Path(args.path))
        sys.stdout.write(json.dumps({"ok": result.ok, "errors": result.errors}, indent=2) + "\n")
        return 0 if result.ok else 1
    dest = Path(args.output)
    mapping = {
        "numerical": lambda: render_numerical(dest, args.run_id),
        "network": lambda: render_network(dest, args.run_id),
        "function": lambda: render_exact_function(dest, args.run_id),
        "architecture": lambda: render_architecture(dest),
        "sensitivity": lambda: render_sensitivity(dest, args.run_id),
    }
    result = mapping[args.family]()
    sys.stdout.write(
        json.dumps({"figure_id": result.figure_id, "svg": str(result.svg_path)}, indent=2) + "\n"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
