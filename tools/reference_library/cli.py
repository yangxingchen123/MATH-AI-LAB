"""CLI for 03_参考资料 identity ingest."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .ingest import doctor, ingest_contest, ingest_paper


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m tools.reference_library")
    parser.add_argument("--root", type=Path, default=None)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("doctor")
    ingest = sub.add_parser("ingest-paper")
    ingest.add_argument("--slug", required=True)
    ingest.add_argument("--title", required=True)
    ingest.add_argument("--domain", required=True)
    ingest.add_argument("--pdf", type=Path, default=None)
    contest = sub.add_parser("ingest-contest")
    contest.add_argument("--contest", required=True)
    contest.add_argument("--slug", required=True)
    contest.add_argument("--title", required=True)
    contest.add_argument("--pdf", type=Path, default=None)
    args = parser.parse_args(argv)
    if args.command == "doctor":
        report = doctor(repo_root=args.root)
        sys.stdout.write(json.dumps(report, indent=2, sort_keys=True) + "\n")
        return 0 if report["status"] in {"PASS", "DEGRADED"} else 1
    if args.command == "ingest-contest":
        result = ingest_contest(
            contest=args.contest,
            slug=args.slug,
            title=args.title,
            pdf=args.pdf,
            repo_root=args.root,
        )
    else:
        result = ingest_paper(
            slug=args.slug,
            title=args.title,
            domain=args.domain,
            pdf=args.pdf,
            repo_root=args.root,
        )
    sys.stdout.write(
        json.dumps(
            {
                "status": result.status,
                "path": str(result.path) if result.path else None,
                "message": result.message,
                "parse_status": result.parse_status,
                "source_sha256": result.source_sha256,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n"
    )
    return 0 if result.status in {"WRITTEN", "NO_OP"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
