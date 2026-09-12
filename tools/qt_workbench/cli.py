"""CLI for the Qt desktop workbench."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from tools.problem_validator.discovery import resolve_project_root

from .doctor import doctor
from .gpt_client import dispatch


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="python -m tools.qt_workbench")
    parser.add_argument("--root", type=Path, default=None)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("doctor")
    sub.add_parser("launch")
    sub.add_parser("gpt-status")
    sub.add_parser("gpt-test")
    gpt = sub.add_parser("gpt")
    gpt.add_argument(
        "--stdin",
        action="store_true",
        default=True,
        help="从 stdin 读 JSON：action=status|connect|chat",
    )
    return parser


def launch(root: Path) -> int:
    from .bootstrap import notify_error, write_log

    write_log(f"launch root={root} exe={sys.executable}")
    report = doctor()
    if not report["pyside"]:
        from .bootstrap import notify_missing_pyside

        notify_missing_pyside()
        return 1
    try:
        from .window import run

        return run(root)
    except Exception as exc:
        import traceback

        from .bootstrap import log_path

        write_log(traceback.format_exc())
        notify_error(
            "MATH-AI-LAB",
            f"工作台启动失败。\n\n{exc}\n\n日志：{log_path()}",
        )
        return 1


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command in {"gpt-status", "gpt-test", "gpt"}:
        root = args.root.expanduser().resolve() if args.root is not None else resolve_project_root(None)
    else:
        root = resolve_project_root(args.root)
    if args.command == "doctor":
        sys.stdout.write(json.dumps(doctor(), ensure_ascii=False, indent=2) + "\n")
        return 0
    if args.command == "launch":
        return launch(root)
    if args.command == "gpt-status":
        sys.stdout.write(json.dumps(dispatch(root, {"action": "status"}), ensure_ascii=False, indent=2) + "\n")
        return 0
    if args.command == "gpt-test":
        result = dispatch(root, {"action": "connect"})
        sys.stdout.write(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
        return 0 if result.get("ok") else 1
    if args.command == "gpt":
        raw = sys.stdin.read()
        try:
            payload = json.loads(raw) if raw.strip() else {}
        except json.JSONDecodeError:
            sys.stderr.write("stdin 不是合法 JSON\n")
            return 1
        if not isinstance(payload, dict):
            sys.stderr.write("stdin JSON 必须是对象\n")
            return 1
        result = dispatch(root, payload)
        sys.stdout.write(json.dumps(result, ensure_ascii=False) + "\n")
        if payload.get("action") == "status":
            return 0
        return 0 if result.get("ok") else 1
    return 1
