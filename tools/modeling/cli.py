"""CLI for the stdlib modeling framework."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .doctor import doctor_text
from .manifest import validate_manifest_file
from .runner import (
    run_network_pilot,
    run_ode_pilot,
    run_lp_pilot,
    run_ols_pilot,
    run_quadratic_pilot,
    run_sensitivity_pilot,
    run_soc_pilot,
    run_soc_piecewise_pilot,
    run_soc_sensitivity_pilot,
    run_stats_pilot,
    run_symbolic_pilot,
)
from .select import rank_model_candidates


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="python -m tools.modeling")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("doctor")
    validate = sub.add_parser("validate-manifest")
    validate.add_argument("--path", required=True)
    run = sub.add_parser("run")
    run.add_argument(
        "--engine",
        required=True,
        choices=(
            "network",
            "quadratic",
            "symbolic",
            "ode",
            "ols",
            "sensitivity",
            "stats",
            "lp",
            "soc",
            "soc_sensitivity",
            "soc_piecewise",
        ),
    )
    run.add_argument("--output-root", required=True)
    run.add_argument("--run-id", required=True)
    select = sub.add_parser("select")
    select.add_argument("--path", required=True)
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
        text, code = doctor_text()
        sys.stdout.write(text)
        return code
    if args.command == "validate-manifest":
        result = validate_manifest_file(Path(args.path))
        if result.ok:
            sys.stdout.write("PASS\n")
            return 0
        sys.stdout.write("FAIL\n" + "\n".join(result.errors) + "\n")
        return 1
    if args.command == "run":
        root = Path(args.output_root)
        engines = {
            "network": run_network_pilot,
            "quadratic": run_quadratic_pilot,
            "symbolic": run_symbolic_pilot,
            "ode": run_ode_pilot,
            "ols": run_ols_pilot,
            "sensitivity": run_sensitivity_pilot,
            "stats": run_stats_pilot,
            "lp": run_lp_pilot,
            "soc": run_soc_pilot,
            "soc_sensitivity": run_soc_sensitivity_pilot,
            "soc_piecewise": run_soc_piecewise_pilot,
        }
        outcome = engines[args.engine](root, args.run_id)
        sys.stdout.write(json.dumps(outcome.__dict__, indent=2) + "\n")
        return 0 if outcome.status == "SUCCEEDED" else 1
    if args.command == "select":
        import yaml

        payload = yaml.safe_load(Path(args.path).read_text(encoding="utf-8")) or {}
        ranked = rank_model_candidates(list(payload.get("candidates") or []))
        sys.stdout.write(json.dumps(ranked, indent=2, ensure_ascii=False) + "\n")
        return 0 if any(item["eligible"] for item in ranked) else 1
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
