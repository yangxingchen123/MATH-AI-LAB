"""CLI for v2.0 retrieval."""

from __future__ import annotations

import argparse
import json
import sys

from .engine import cited_answer
from .evalset import eval_corpus
from .gate import evaluate_gate


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="python -m tools.retrieval")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("gate")
    ask = sub.add_parser("ask")
    ask.add_argument("--query", required=True)
    ask.add_argument("--principal", default="PUBLIC")
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
    result = cited_answer(args.query, eval_corpus(), args.principal)
    sys.stdout.write(json.dumps(result, indent=2, sort_keys=True) + "\n")
    return 0 if result["status"] != "INSUFFICIENT_EVIDENCE" else 2


if __name__ == "__main__":
    raise SystemExit(main())
