"""CLI for Lean sidecar checks. Never writes production Source."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .build import run_lake_build
from .constants import LEAN_ROOT
from .correspondence import load_table, validate_table
from .doctor import doctor
from .gate import evaluate_gate
from .manifest import validate_manifest_file
from .scan import scan_lean_tree
from .verify import verify


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="python -m tools.lean_formalization")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("doctor")
    sub.add_parser("gate")
    sub.add_parser("build")
    sub.add_parser("verify")
    scan = sub.add_parser("scan")
    scan.add_argument("--root", default=str(LEAN_ROOT))
    table = sub.add_parser("check-correspondence")
    table.add_argument("--table", default=str(LEAN_ROOT / "correspondence.yaml"))
    table.add_argument("--project", default=str(LEAN_ROOT))
    manifest = sub.add_parser("check-manifest")
    manifest.add_argument("--path", required=True)
    manifest.add_argument("--project", default=str(LEAN_ROOT))
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
        return 0 if report["status"] in {"PASS", "DEGRADED"} else 1
    if args.command == "gate":
        report = evaluate_gate()
        sys.stdout.write(json.dumps(report, indent=2, sort_keys=True) + "\n")
        return 0 if report["status"] in {"PASS", "DEGRADED"} else 1
    if args.command == "build":
        result = run_lake_build(LEAN_ROOT, allow_install=True)
        sys.stdout.write(json.dumps(result.__dict__, indent=2) + "\n")
        if result.status == "SUCCEEDED":
            return 0
        if result.status == "DEGRADED":
            return 0
        return 1
    if args.command == "verify":
        report = verify()
        sys.stdout.write(json.dumps(report, indent=2, sort_keys=True) + "\n")
        return 0 if report["status"] in {"PASS", "DEGRADED"} else 1
    if args.command == "scan":
        hits = scan_lean_tree(Path(args.root))
        sys.stdout.write(json.dumps([hit.__dict__ for hit in hits], indent=2) + "\n")
        return 1 if hits else 0
    if args.command == "check-manifest":
        result = validate_manifest_file(Path(args.path), Path(args.project))
        sys.stdout.write(json.dumps({"ok": result.ok, "errors": result.errors}, indent=2) + "\n")
        return 0 if result.ok else 1
    entries = load_table(Path(args.table))
    result = validate_table(entries, Path(args.project))
    sys.stdout.write(
        json.dumps(
            {"ok": result.ok, "errors": result.errors, "families": result.families},
            indent=2,
        )
        + "\n"
    )
    return 0 if result.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
