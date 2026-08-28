"""CLI for v2.1 controlled multi-agent research."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .gate import evaluate_gate
from .orchestrator import dump_audit, run_task


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="python -m tools.collaboration")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("gate")
    run = sub.add_parser("run")
    run.add_argument("--root", required=True)
    run.add_argument("--task-id", default="task-001")
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
    if args.command == "gate":
        report = evaluate_gate()
        sys.stdout.write(json.dumps(report, indent=2, sort_keys=True) + "\n")
        return 0 if report["status"] == "PASS" else 1
    audit = run_task(Path(args.root), task_id=args.task_id)
    sys.stdout.write(dump_audit(audit))
    return 0 if audit.final_status in {"SUCCEEDED", "PARTIAL"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
