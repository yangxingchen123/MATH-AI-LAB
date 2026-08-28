"""Workbench orchestration CLI. Candidate scaffolds only."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .attach import attach_contest_md
from .bootstrap import bootstrap_contest
from .coverage import run_contest_coverage
from .experiment import ENGINES, run_contest_experiment
from .find_data import find_contest_data
from .pipeline import run_contest_pipeline
from .status import capability_status


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m tools.workbench")
    parser.add_argument("--root", type=Path, default=None)
    sub = parser.add_subparsers(dest="command", required=True)
    boot = sub.add_parser("bootstrap")
    boot.add_argument("--kind", required=True, choices=("contest_modeling",))
    boot.add_argument("--name", required=True)
    boot.add_argument("--title", required=True)
    attach = sub.add_parser("attach-md")
    attach.add_argument("--contest", required=True)
    attach.add_argument("--slug", required=True)
    attach.add_argument("--md", type=Path, required=True)
    run = sub.add_parser("run-experiment")
    run.add_argument("--name", required=True)
    run.add_argument("--engine", required=True, choices=sorted(ENGINES))
    run.add_argument("--run-id", required=True)
    find = sub.add_parser("find-data")
    find.add_argument("--name", required=True)
    find.add_argument("--query", action="append", default=None)
    find.add_argument("--no-seeds", action="store_true")
    pipe = sub.add_parser("contest-pipeline")
    pipe.add_argument("--name", required=True)
    cov = sub.add_parser("coverage")
    cov.add_argument("--name", required=True)
    sub.add_parser("status")
    args = parser.parse_args(argv)
    if args.command == "status":
        report = capability_status()
        sys.stdout.write(json.dumps(report, indent=2, ensure_ascii=False) + "\n")
        return 0 if report["status"] in {"PASS", "DEGRADED"} else 1
    if args.command == "attach-md":
        result = attach_contest_md(
            contest=args.contest,
            slug=args.slug,
            md=args.md,
            repo_root=args.root,
        )
        sys.stdout.write(
            json.dumps(
                {
                    "status": result.status,
                    "message": result.message,
                    "path": str(result.path) if result.path else None,
                    "derived_sha256": result.derived_sha256,
                },
                indent=2,
                ensure_ascii=False,
            )
            + "\n"
        )
        return 0 if result.status in {"WRITTEN", "NO_OP"} else 1
    if args.command == "run-experiment":
        outcome = run_contest_experiment(
            name=args.name,
            engine=args.engine,
            run_id=args.run_id,
            repo_root=args.root,
        )
        sys.stdout.write(
            json.dumps(
                {
                    "status": outcome.status,
                    "message": outcome.message,
                    "run_id": outcome.run_id,
                    "output_dir": outcome.output_dir,
                    "metrics": outcome.metrics,
                },
                indent=2,
                ensure_ascii=False,
            )
            + "\n"
        )
        return 0 if outcome.status == "SUCCEEDED" else 1
    if args.command == "find-data":
        report = find_contest_data(
            name=args.name,
            queries=tuple(args.query) if args.query else None,
            repo_root=args.root,
            include_seeds=not args.no_seeds,
        )
        sys.stdout.write(json.dumps(report, indent=2, ensure_ascii=False) + "\n")
        return 0 if report["status"] in {"PASS", "DEGRADED"} else 1
    if args.command == "contest-pipeline":
        report = run_contest_pipeline(name=args.name, repo_root=args.root)
        sys.stdout.write(json.dumps(report, indent=2, ensure_ascii=False) + "\n")
        return 0 if report["status"] in {"INCOMPLETE", "DEGRADED", "PASS"} else 1
    if args.command == "coverage":
        report = run_contest_coverage(name=args.name, repo_root=args.root)
        sys.stdout.write(json.dumps(report, indent=2, ensure_ascii=False) + "\n")
        return 0 if report["status"] in {"INCOMPLETE", "DEGRADED", "PASS"} else 1
    result = bootstrap_contest(name=args.name, title=args.title, repo_root=args.root)
    sys.stdout.write(
        json.dumps(
            {
                "status": result.status,
                "message": result.message,
                "project": str(result.project) if result.project else None,
                "code": str(result.code) if result.code else None,
                "latex": str(result.latex) if result.latex else None,
            },
            indent=2,
            ensure_ascii=False,
        )
        + "\n"
    )
    return 0 if result.status in {"WRITTEN", "NO_OP"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
