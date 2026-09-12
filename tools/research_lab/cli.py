"""CLI for v2.2-lab research-lab Pilot. Never writes production Source."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .constants import PROBLEM_REGISTRY, PROBLEMS_DIR, REPO_ROOT, TASK_REGISTRY
from .conjecture import load_all_conjectures, validate_conjecture
from .cycle import run_cycle
from .doctor import doctor
from .evaluators.sum_free import evaluate_candidate
from .gate import evaluate_gate
from .inventory import scan_inventory, write_inventory
from .ledger import budget_for_layer
from .operate import operate
from .protocol import evaluate_session, load_protocol, route, validate_protocol
from .registry import list_problem_paths, load_record, validate_record
from .search import greedy_sum_free
from .transitions import advance
from .verify import verify


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="python -m tools.research_lab")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("doctor")
    sub.add_parser("gate")
    inventory = sub.add_parser("inventory")
    inventory.add_argument("--root", default=str(REPO_ROOT))
    inventory.add_argument("--write", dest="write_path", default=None)
    inventory.add_argument("--sidecar", dest="sidecar_path", default=None)
    evaluate = sub.add_parser("evaluate-sum-free")
    evaluate.add_argument("--n", type=int, required=True)
    evaluate.add_argument("--set", dest="values", required=True, help="comma-separated integers")
    search = sub.add_parser("search-sum-free")
    search.add_argument("--n", type=int, required=True)
    sub.add_parser("check-problem")
    sub.add_parser("verify")
    sub.add_parser("operate")
    sub.add_parser("protocol")
    routed = sub.add_parser("route")
    routed.add_argument("--kind", required=True)
    session = sub.add_parser("check-session")
    session.add_argument("--file", required=True)
    sub.add_parser("list-problems")
    sub.add_parser("list-conjectures")
    adv = sub.add_parser("advance")
    adv.add_argument("--file", required=True)
    adv.add_argument("--to", dest="new_stage", required=True)
    cycle = sub.add_parser("cycle")
    cycle.add_argument("--file", default=str(PROBLEM_REGISTRY))
    cycle.add_argument("--n", type=int, default=10)
    cycle.add_argument("--ledger", dest="ledger_path", default=None)
    cycle.add_argument("--failures", dest="failure_path", default=None)
    cycle.add_argument("--chain", dest="chain_path", default=None)
    reproduce = sub.add_parser("reproduce")
    reproduce.add_argument("--file", required=True)
    reproduce.add_argument("--problem", default=str(PROBLEM_REGISTRY))
    journal = sub.add_parser("journal")
    journal.add_argument("--file", default=str(PROBLEM_REGISTRY))
    sub.add_parser("prior-art-matrix")
    funnel = sub.add_parser("funnel")
    funnel.add_argument("--file", default=str(PROBLEM_REGISTRY))
    funnel.add_argument("--n", type=int, default=10)
    funnel.add_argument("--limit", type=int, default=16)
    funnel.add_argument("--layer", default="C0")
    sub.add_parser("backlog")
    sub.add_parser("review-statements")
    retrieve = sub.add_parser("retrieve")
    retrieve.add_argument("--query", required=True)
    sub.add_parser("recipe")
    pipeline = sub.add_parser("pipeline")
    pipeline.add_argument("--file", default=str(PROBLEM_REGISTRY))
    pipeline.add_argument("--n", type=int, default=5)
    sub.add_parser("adapters")
    task = sub.add_parser("check-task")
    task.add_argument("--file", default=str(TASK_REGISTRY))
    sub.add_parser("lemma-graph")
    repair = sub.add_parser("repair")
    repair.add_argument("--file", default=str(PROBLEM_REGISTRY))
    repair.add_argument("--n", type=int, default=5)
    repair.add_argument("--reason", default="not_sum_free")
    sub.add_parser("risks")
    cost = sub.add_parser("cost-report")
    cost.add_argument("--ledger", dest="ledger_path", default=None)
    explore = sub.add_parser("explore")
    explore.add_argument("--failures", dest="failure_path", default=None)
    explore.add_argument("--format", choices=("json", "markdown"), default="json")
    explore.add_argument("--id", dest="object_id", default=None)
    explore.add_argument("--list", action="store_true")
    search_fail = sub.add_parser("search-failure")
    search_fail.add_argument("--query", required=True)
    search_fail.add_argument("--failures", dest="failure_path", default=None)
    search_explore = sub.add_parser("search-explore")
    search_explore.add_argument("--query", required=True)
    search_explore.add_argument("--failures", dest="failure_path", default=None)
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
        report = doctor()
        sys.stdout.write(json.dumps(report, indent=2, sort_keys=True) + "\n")
        return 0 if report["status"] in {"PASS", "DEGRADED"} else 1
    if args.command == "gate":
        report = evaluate_gate()
        sys.stdout.write(json.dumps(report, indent=2, sort_keys=True) + "\n")
        return 0 if report["status"] == "PASS" else 1
    if args.command == "inventory":
        report = scan_inventory(Path(args.root))
        if args.write_path:
            try:
                write_inventory(report, Path(args.write_path))
            except ValueError as exc:
                sys.stdout.write(json.dumps({"ok": False, "error": str(exc)}) + "\n")
                return 1
        if args.sidecar_path:
            from .closeout import write_sidecar

            try:
                write_sidecar(Path(args.sidecar_path), report)
            except ValueError as exc:
                sys.stdout.write(json.dumps({"ok": False, "error": str(exc)}) + "\n")
                return 1
        sys.stdout.write(json.dumps(report, indent=2, sort_keys=True) + "\n")
        return 0 if report["key_roots_complete"] else 1
    if args.command == "search-sum-free":
        found = greedy_sum_free(args.n)
        report = evaluate_candidate(args.n, found)
        report["candidate"] = sorted(found)
        sys.stdout.write(json.dumps(report, indent=2, sort_keys=True) + "\n")
        return 0 if report.get("optimal") else 1
    if args.command == "check-problem":
        errors = validate_record(load_record(PROBLEM_REGISTRY))
        payload = {"ok": errors == [], "errors": errors, "path": str(PROBLEM_REGISTRY)}
        sys.stdout.write(json.dumps(payload, indent=2, sort_keys=True) + "\n")
        return 0 if errors == [] else 1
    if args.command == "verify":
        report = verify()
        sys.stdout.write(json.dumps(report, indent=2, sort_keys=True) + "\n")
        return 0 if report["status"] in {"PASS", "DEGRADED"} else 1
    if args.command == "operate":
        report = operate()
        sys.stdout.write(json.dumps(report, indent=2, sort_keys=True) + "\n")
        return 0 if report["status"] in {"PASS", "DEGRADED"} else 1
    if args.command == "protocol":
        contract = load_protocol()
        errors = validate_protocol(contract)
        payload = {"ok": errors == [], "errors": errors, "protocol": contract}
        sys.stdout.write(json.dumps(payload, indent=2, sort_keys=True) + "\n")
        return 0 if payload["ok"] else 1
    if args.command == "route":
        report = route(args.kind)
        sys.stdout.write(json.dumps(report, indent=2, sort_keys=True) + "\n")
        return 0 if report.get("ok") else 1
    if args.command == "check-session":
        import yaml

        data = yaml.safe_load(Path(args.file).read_text(encoding="utf-8")) or {}
        report = evaluate_session(data)
        sys.stdout.write(json.dumps(report, indent=2, sort_keys=True) + "\n")
        return 0 if report.get("ok") else 1
    if args.command == "list-problems":
        rows = []
        for path in list_problem_paths(PROBLEMS_DIR):
            record = load_record(path)
            rows.append(
                {
                    "id": record.get("id"),
                    "stage": record.get("stage"),
                    "path": str(path),
                    "ok": validate_record(record) == [],
                }
            )
        sys.stdout.write(json.dumps({"problems": rows}, indent=2, sort_keys=True) + "\n")
        return 0 if rows and all(item["ok"] for item in rows) else 1
    if args.command == "list-conjectures":
        rows = []
        for item in load_all_conjectures():
            rows.append(
                {
                    "id": item.get("id"),
                    "problem_id": item.get("problem_id"),
                    "status": item.get("status"),
                    "ok": validate_conjecture(item) == [],
                }
            )
        sys.stdout.write(json.dumps({"conjectures": rows}, indent=2, sort_keys=True) + "\n")
        return 0 if rows and all(item["ok"] for item in rows) else 1
    if args.command == "advance":
        record = load_record(Path(args.file))
        updated, errors = advance(record, args.new_stage)
        payload = {"ok": updated is not None, "errors": errors, "record": updated}
        sys.stdout.write(json.dumps(payload, indent=2, sort_keys=True) + "\n")
        return 0 if updated is not None else 1
    if args.command == "cycle":
        from .evidence import append_chain

        report = run_cycle(
            load_record(Path(args.file)),
            n=args.n,
            budget=budget_for_layer("C0"),
            ledger_path=Path(args.ledger_path) if args.ledger_path else None,
            failure_path=Path(args.failure_path) if args.failure_path else None,
        )
        if args.chain_path:
            try:
                sealed = report.get("chain")
                if not isinstance(sealed, dict):
                    raise ValueError("cycle produced no chain record")
                append_chain(Path(args.chain_path), sealed)
            except ValueError as exc:
                sys.stdout.write(json.dumps({"ok": False, "error": str(exc)}) + "\n")
                return 1
        sys.stdout.write(json.dumps(report, indent=2, sort_keys=True) + "\n")
        return 0 if report.get("ok") else 1
    if args.command == "reproduce":
        from .evidence import load_chain, reproduce

        rows = load_chain(Path(args.file))
        if not rows:
            sys.stdout.write(json.dumps({"ok": False, "errors": ["empty_chain"]}) + "\n")
            return 1
        report = reproduce(load_record(Path(args.problem)), rows[-1])
        sys.stdout.write(json.dumps(report, indent=2, sort_keys=True) + "\n")
        return 0 if report.get("ok") else 1
    if args.command == "journal":
        from .journal import evaluate_journal

        report = evaluate_journal(load_record(Path(args.file)))
        sys.stdout.write(json.dumps(report, indent=2, sort_keys=True) + "\n")
        return 0 if report.get("paper_ready") else 1
    if args.command == "prior-art-matrix":
        from .prior_art import build_matrix

        report = build_matrix()
        sys.stdout.write(json.dumps(report, indent=2, sort_keys=True) + "\n")
        return 0 if report.get("ok") else 1
    if args.command == "funnel":
        from .funnel import run_funnel

        report = run_funnel(
            load_record(Path(args.file)),
            n=args.n,
            limit=args.limit,
            layer=args.layer,
        )
        sys.stdout.write(json.dumps(report, indent=2, sort_keys=True) + "\n")
        return 0 if report.get("ok") else 1
    if args.command == "backlog":
        from .backlog import evaluate_backlog

        report = evaluate_backlog()
        sys.stdout.write(json.dumps(report, indent=2, sort_keys=True) + "\n")
        return 0 if report.get("ok") else 1
    if args.command == "review-statements":
        from .closeout import review_nl_lean

        report = review_nl_lean()
        sys.stdout.write(json.dumps(report, indent=2, sort_keys=True) + "\n")
        return 0 if report.get("ok") else 1
    if args.command == "retrieve":
        from .premises import retrieve_premises

        report = retrieve_premises(args.query)
        sys.stdout.write(json.dumps(report, indent=2, sort_keys=True) + "\n")
        return 0 if report.get("candidate") else 1
    if args.command == "recipe":
        from .closeout import reproduction_recipe

        report = reproduction_recipe()
        sys.stdout.write(json.dumps(report, indent=2, sort_keys=True) + "\n")
        return 0
    if args.command == "pipeline":
        from .pipeline import run_pipeline

        report = run_pipeline(load_record(Path(args.file)), n=args.n)
        sys.stdout.write(json.dumps(report, indent=2, sort_keys=True) + "\n")
        return 0 if report.get("ok") else 1
    if args.command == "adapters":
        from .adapters import PLUGIN_STATUS, invoke

        report = {name: invoke(name) for name in PLUGIN_STATUS}
        sys.stdout.write(json.dumps(report, indent=2, sort_keys=True) + "\n")
        return 0 if all(item["called"] is False for item in report.values()) else 1
    if args.command == "check-task":
        from .task import load_task, validate_task

        errors = validate_task(load_task(Path(args.file)))
        payload = {"ok": errors == [], "errors": errors, "path": str(args.file)}
        sys.stdout.write(json.dumps(payload, indent=2, sort_keys=True) + "\n")
        return 0 if errors == [] else 1
    if args.command == "lemma-graph":
        from .lemmas import lemma_graph

        report = lemma_graph()
        sys.stdout.write(json.dumps(report, indent=2, sort_keys=True) + "\n")
        return 0 if report.get("ok") else 1
    if args.command == "repair":
        from .repair import local_repair

        report = local_repair(load_record(Path(args.file)), n=args.n, failed_reason=args.reason)
        sys.stdout.write(json.dumps(report, indent=2, sort_keys=True) + "\n")
        return 0 if report.get("ok") else 1
    if args.command == "risks":
        from .risks import evaluate_risks

        report = evaluate_risks()
        sys.stdout.write(json.dumps(report, indent=2, sort_keys=True) + "\n")
        return 0 if report.get("ok") else 1
    if args.command == "cost-report":
        from .cost_report import cost_report

        report = cost_report(Path(args.ledger_path) if args.ledger_path else None)
        sys.stdout.write(json.dumps(report, indent=2, sort_keys=True) + "\n")
        return 0
    if args.command == "explore":
        from .exploration import briefing_markdown, explore_briefing, list_index, lookup_index

        failure_path = Path(args.failure_path) if args.failure_path else None
        if getattr(args, "list", False):
            rows = list_index(failure_path=failure_path)
            if getattr(args, "format", "json") == "markdown":
                lines = [
                    "# 探索目录",
                    "",
                    "只读。status=candidate。无 embedding。",
                    "",
                    "| id | group | title |",
                    "| --- | --- | --- |",
                ]
                for row in rows:
                    lines.append(
                        f"| `{row.get('id')}` | {row.get('group')} | {row.get('title')} |"
                    )
                sys.stdout.write("\n".join(lines) + "\n")
            else:
                sys.stdout.write(json.dumps(rows, indent=2, sort_keys=True) + "\n")
            return 0
        object_id = getattr(args, "object_id", None)
        if object_id:
            item = lookup_index(object_id, failure_path=failure_path)
            if item is None:
                sys.stderr.write(f"exploration item not found: {object_id}\n")
                return 1
            if getattr(args, "format", "json") == "markdown":
                sys.stdout.write(str(item.get("body") or ""))
            else:
                sys.stdout.write(json.dumps(item, indent=2, sort_keys=True) + "\n")
            return 0
        report = explore_briefing(failure_path=failure_path)
        if getattr(args, "format", "json") == "markdown":
            sys.stdout.write(briefing_markdown(report))
        else:
            sys.stdout.write(json.dumps(report, indent=2, sort_keys=True) + "\n")
        return 0 if report.get("wrote_canonical") is False and report.get("health", {}).get("ok") else 1
    if args.command == "search-failure":
        from .exploration import search_failures

        report = search_failures(
            args.query,
            failure_path=Path(args.failure_path) if args.failure_path else None,
        )
        sys.stdout.write(json.dumps(report, indent=2, sort_keys=True) + "\n")
        return 0
    if args.command == "search-explore":
        from .exploration import search_explore

        report = search_explore(
            args.query,
            failure_path=Path(args.failure_path) if args.failure_path else None,
        )
        sys.stdout.write(json.dumps(report, indent=2, sort_keys=True) + "\n")
        return 0
    values = {int(part.strip()) for part in args.values.split(",") if part.strip()}
    report = evaluate_candidate(args.n, values)
    sys.stdout.write(json.dumps(report, indent=2, sort_keys=True) + "\n")
    return 0 if report["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
