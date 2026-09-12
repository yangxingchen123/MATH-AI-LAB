"""CLI for the read-only notebook UI."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from tools.problem_validator.discovery import resolve_project_root

from .catalog import build_catalog
from .launch import DEFAULT_HOST, DEFAULT_PORT, launch
from .serve import serve


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="python -m tools.studio")
    parser.add_argument("--root", type=Path, default=None)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("catalog")
    served = sub.add_parser("serve")
    served.add_argument("--host", default=DEFAULT_HOST)
    served.add_argument("--port", type=int, default=DEFAULT_PORT)
    opened = sub.add_parser("launch")
    opened.add_argument("--host", default=DEFAULT_HOST)
    opened.add_argument("--port", type=int, default=DEFAULT_PORT)
    opened.add_argument("--no-browser", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    root = resolve_project_root(args.root)
    if args.command == "catalog":
        sys.stdout.write(json.dumps(build_catalog(root), ensure_ascii=False, indent=2) + "\n")
        return 0
    if args.command == "serve":
        serve(root=root, host=args.host, port=args.port)
        return 0
    if args.command == "launch":
        result = launch(
            root=root,
            host=args.host,
            port=args.port,
            open_browser=not args.no_browser,
        )
        sys.stdout.write(f"{result['status']}  {result['url']}\n")
        return 0 if result["status"] in {"already_running", "started"} else 1
    return 1
