"""CLI: JSON stdin → JSON stdout. --root is for tests / local server, never the browser."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from tools.knowledge_validator.discovery import resolve_project_root

from .gateway import doctor, run_operation


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m tools.ui_operations")
    parser.add_argument("command", choices=["run", "doctor"], help="run a request or print capability")
    parser.add_argument(
        "--root",
        default=None,
        help="Project root. Server/tests set this. Clients must not send it.",
    )
    args = parser.parse_args(argv)

    if args.command == "doctor":
        json.dump(doctor(), sys.stdout, ensure_ascii=False)
        sys.stdout.write("\n")
        return 0

    raw = sys.stdin.read()
    try:
        request = json.loads(raw) if raw.strip() else {}
    except json.JSONDecodeError as exc:
        json.dump(
            {
                "version": 1,
                "success": False,
                "operation": "Unknown",
                "preview": False,
                "request_id": "",
                "error": f"invalid JSON: {exc}",
                "validation": "FAIL",
            },
            sys.stdout,
            ensure_ascii=False,
        )
        sys.stdout.write("\n")
        return 2

    if args.root:
        root = Path(args.root).resolve()
    else:
        root = resolve_project_root(None, Path.cwd())

    result = run_operation(root, request if isinstance(request, dict) else {})
    json.dump(result.to_dict(), sys.stdout, ensure_ascii=False)
    sys.stdout.write("\n")
    return 0 if result.success else 1
