"""CLI for tools.research_project. main() catches SystemExit."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .append_only import check_append_only, check_append_only_all
from .gate import evaluate_gate
from .literature_gate import evaluate_literature_gate
from .models import ResearchProjectOperationKind
from .operations import (
    add_assumption,
    add_claim,
    add_evidence,
    add_literature,
    add_novelty,
    add_review,
    append_decision,
    init_project,
    reconcile_project,
    record_negative_result,
    supersede_assumption,
    update_governance,
)
from .paths import resolve_repo_root
from .report import format_assessment, format_operation, format_status, format_validation
from .service import doctor_text, status_for
from .validator import validate_project
from .governance import assess_external_processing


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m tools.research_project",
        description="v1.1 research project control plane with v1.3 literature extension",
    )
    parser.add_argument("--root", type=Path, default=None)
    sub = parser.add_subparsers(dest="command", required=True)

    check = sub.add_parser("check", help="validate a research project")
    check.add_argument("--project", required=True)

    status = sub.add_parser("status", help="show freshness and governance summary")
    status.add_argument("--project", required=True)

    sub.add_parser("doctor", help="contract health-check")

    append = sub.add_parser("check-append-only", help="decision append-only guard")
    append.add_argument("--project")
    append.add_argument("--all", action="store_true")
    append.add_argument("--base-ref")

    assess = sub.add_parser(
        "assess-external-processing",
        help="PROJECT_POLICY_PREFLIGHT assessment",
    )
    assess.add_argument("--project", required=True)

    gate = sub.add_parser("gate", help="evaluate v1.1 gate metrics")
    gate.add_argument("--format", choices=("json", "text"), default="text")
    lit_gate = sub.add_parser("literature-gate", help="evaluate v1.3 literature metrics")
    lit_gate.add_argument("--format", choices=("json", "text"), default="text")

    init = sub.add_parser("init", help="create a research project scaffold")
    init.add_argument("--project", required=True)
    init.add_argument("--title", required=True)
    init.add_argument(
        "--kind",
        default="research",
        choices=("research", "contest_modeling", "literature"),
    )

    def _candidate_cmd(name: str, help_text: str) -> None:
        cmd = sub.add_parser(name, help=help_text)
        cmd.add_argument("--project", required=True)
        cmd.add_argument("--candidate", required=True)

    _candidate_cmd("add-assumption", "add an ASSUMPTION record")
    _candidate_cmd("add-claim", "add a CLAIM record")
    _candidate_cmd("add-evidence", "add an EVIDENCE record and backlink")
    _candidate_cmd("append-decision", "append a DECISION record")
    _candidate_cmd("record-negative-result", "record a NEGATIVE_RESULT")
    _candidate_cmd("update-governance", "replace GOV-0001 or append AI_CONTRIBUTION")
    _candidate_cmd("add-literature", "add a LITERATURE identity record")
    _candidate_cmd("add-novelty", "add a NOVELTY matrix row")
    _candidate_cmd("add-review", "add a REVIEW record")

    supersede = sub.add_parser("supersede-assumption", help="supersede an ACTIVE assumption")
    supersede.add_argument("--project", required=True)
    supersede.add_argument("--ref", required=True)
    supersede.add_argument("--candidate", required=True)

    reconcile = sub.add_parser("reconcile", help="refresh Generated dossier region")
    reconcile.add_argument("--project", required=True)
    return parser


def _print(text: str) -> None:
    sys.stdout.write(text if text.endswith("\n") else text + "\n")


def _op_exit(kind: ResearchProjectOperationKind) -> int:
    return 0 if kind in {ResearchProjectOperationKind.WRITTEN, ResearchProjectOperationKind.NO_OP} else 1


def run(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    repo_root = resolve_repo_root(args.root)
    command = args.command

    if command == "doctor":
        text, code = doctor_text()
        _print(text)
        return code
    if command == "gate":
        payload = evaluate_gate()
        if args.format == "json":
            _print(json.dumps(payload, indent=2, sort_keys=False))
        else:
            _print(json.dumps(payload, indent=2, sort_keys=False))
        return 0 if payload["status"] == "PASS" else 1
    if command == "literature-gate":
        payload = evaluate_literature_gate()
        _print(json.dumps(payload, indent=2, sort_keys=False))
        return 0 if payload["status"] == "PASS" else 1
    if command == "check":
        result = validate_project(Path(args.project))
        _print(format_validation(result))
        return 0 if result.ok else 1
    if command == "status":
        result = status_for(Path(args.project))
        _print(format_status(result))
        return 0
    if command == "check-append-only":
        if args.all:
            if not args.base_ref:
                _print("FAIL\nERROR: --all requires --base-ref\n")
                return 1
            result = check_append_only_all(repo_root, args.base_ref)
        else:
            if not args.project or not args.base_ref:
                _print("FAIL\nERROR: --project and --base-ref are required\n")
                return 1
            result = check_append_only(Path(args.project), args.base_ref)
        _print(format_validation(result))
        return 0 if result.ok else 1
    if command == "assess-external-processing":
        result = assess_external_processing(Path(args.project))
        _print(format_assessment(result))
        return 0 if result.verdict == "ALLOWED" else 1
    if command == "init":
        result = init_project(
            Path(args.project), args.title, repo_root=repo_root, kind=args.kind
        )
        _print(format_operation(result))
        return _op_exit(result.kind)
    if command == "add-assumption":
        result = add_assumption(Path(args.project), Path(args.candidate))
        _print(format_operation(result))
        return _op_exit(result.kind)
    if command == "add-claim":
        result = add_claim(Path(args.project), Path(args.candidate))
        _print(format_operation(result))
        return _op_exit(result.kind)
    if command == "add-evidence":
        result = add_evidence(Path(args.project), Path(args.candidate))
        _print(format_operation(result))
        return _op_exit(result.kind)
    if command == "append-decision":
        result = append_decision(Path(args.project), Path(args.candidate))
        _print(format_operation(result))
        return _op_exit(result.kind)
    if command == "record-negative-result":
        result = record_negative_result(Path(args.project), Path(args.candidate))
        _print(format_operation(result))
        return _op_exit(result.kind)
    if command == "update-governance":
        result = update_governance(Path(args.project), Path(args.candidate))
        _print(format_operation(result))
        return _op_exit(result.kind)
    if command == "add-literature":
        result = add_literature(Path(args.project), Path(args.candidate))
        _print(format_operation(result))
        return _op_exit(result.kind)
    if command == "add-novelty":
        result = add_novelty(Path(args.project), Path(args.candidate))
        _print(format_operation(result))
        return _op_exit(result.kind)
    if command == "add-review":
        result = add_review(Path(args.project), Path(args.candidate))
        _print(format_operation(result))
        return _op_exit(result.kind)
    if command == "supersede-assumption":
        result = supersede_assumption(Path(args.project), args.ref, Path(args.candidate))
        _print(format_operation(result))
        return _op_exit(result.kind)
    if command == "reconcile":
        result = reconcile_project(Path(args.project))
        _print(format_operation(result))
        return _op_exit(result.kind)
    parser.error(f"unknown command: {command}")
    return 2


def main(argv: list[str] | None = None) -> int:
    try:
        return run(argv)
    except SystemExit as exc:
        if exc.code is None:
            return 0
        if isinstance(exc.code, int):
            return exc.code
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
