"""CLI for open-license dataset discovery. Candidate list only."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .discover import discover_open_data, write_candidates


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m tools.open_data")
    sub = parser.add_subparsers(dest="command", required=True)
    search = sub.add_parser("search")
    search.add_argument("--query", action="append", default=None)
    search.add_argument("--project", type=Path, default=None)
    search.add_argument("--no-seeds", action="store_true")
    args = parser.parse_args(argv)
    report = discover_open_data(
        queries=tuple(args.query) if args.query else None,
        include_seeds=not args.no_seeds,
    )
    if args.project is not None:
        path = write_candidates(Path(args.project), report)
        report = dict(report)
        report["written"] = str(path)
    sys.stdout.write(json.dumps(report, indent=2, ensure_ascii=False) + "\n")
    return 0 if report["status"] in {"PASS", "DEGRADED"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
