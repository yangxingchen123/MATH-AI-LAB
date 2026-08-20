"""CLI for Normal Operation v1."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from tools.knowledge_validator.discovery import resolve_project_root

from .closure_check import scan_closure_drift
from .completion import inspect_problem_completion
from .finalizer import finalize
from .reconcile import reconcile_problem


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m tools.normal_operation")
    sub = parser.add_subparsers(dest="command", required=True)

    fin = sub.add_parser("finalize", help="Run deterministic post-mutation finalization")
    fin.add_argument("--root", type=Path, default=None, help="Project root")
    fin.add_argument(
        "--changed",
        required=True,
        help="Comma-separated changed types: problem,attempt,knowledge,method",
    )
    fin.add_argument(
        "--no-verification",
        action="store_true",
        help="Skip verification core (validators + workspace only)",
    )
    fin.add_argument("--problem", dest="problem_hint", default=None, help="Optional problem ID hint")

    rec = sub.add_parser("reconcile", help="Reconcile Problem closure + artifact")
    rec.add_argument("--root", type=Path, default=None)
    rec.add_argument("--problem", required=True)
    rec.add_argument("--domain", default=None, help="Artifact domain (runtime only)")
    rec.add_argument("--no-close", action="store_true")
    rec.add_argument("--no-artifact", action="store_true")
    rec.add_argument("--no-verification", action="store_true")

    chk = sub.add_parser("check-closure", help="Inspect canonical / workflow / artifact state")
    chk.add_argument("--root", type=Path, default=None)
    chk.add_argument("--problem", default=None)
    chk.add_argument("--all", action="store_true")
    chk.add_argument("--domain", default=None)

    args = parser.parse_args(argv)
    root = resolve_project_root(args.root)

    if args.command == "finalize":
        result = finalize(
            root=root,
            changed=args.changed,
            include_verification=not args.no_verification,
        )
        print("Normal Operation Finalize")
        print(f"Changed: {', '.join(result.changed_types)}")
        print(f"Validation: {result.validation_status.value}")
        print(f"Workspace initial: {result.workspace_initial}")
        print(f"Workspace sync: {'yes' if result.workspace_sync_performed else 'no'}")
        print(f"Workspace final: {result.workspace_final}")
        print(f"Workspace check: {result.workspace_check_status.value}")
        print(f"Verification: {result.verification_status.value}")
        print(f"Duration: {result.duration_seconds:.2f}s")
        if result.suggested_action:
            print(f"Suggested: {result.suggested_action}")
        return 0 if result.overall_pass else 1

    if args.command == "reconcile":
        result = reconcile_problem(
            root,
            problem_id=args.problem,
            auto_close=not args.no_close,
            auto_artifact=not args.no_artifact,
            artifact_domain=args.domain,
            include_verification=not args.no_verification,
        )
        print(f"{args.problem}")
        print(f"Canonical: {'COMPLETE' if result.completion.complete else 'INCOMPLETE'}")
        if result.completion.missing_targets:
            print(f"Missing: {', '.join(result.completion.missing_targets)}")
        print(f"Workflow: {result.workflow_after}")
        if result.artifact:
            print(f"LaTeX: {result.artifact.latex.value}")
            print(f"PDF: {result.artifact.pdf.value}")
            if result.artifact.paths:
                print(f"TeX: {result.artifact.paths.entry_tex}")
                print(f"PDF path: {result.artifact.paths.formal_pdf}")
        print(
            "Counters: "
            f"moves={result.counters.workflow_moves} "
            f"latex_writes={result.counters.latex_writes} "
            f"builds={result.counters.builds} "
            f"pdf_replaces={result.counters.pdf_replaces} "
            f"syncs={result.counters.workspace_syncs}"
        )
        if result.error:
            print(f"Error: {result.error}")
            return 1
        return 0 if result.overall_pass else 1

    if args.command == "check-closure":
        if args.all:
            scan = scan_closure_drift(root)
            print(f"Problems scanned: {scan.total_problems}")
            print(f"Drift items: {len(scan.items)}")
            for item in scan.items:
                print(f"- {item.problem_id} [{item.category}] {item.suggested_action}")
            print(f"Errors: {len(scan.errors)}")
            print(f"Warnings: {len(scan.warnings)}")
            return 0 if len(scan.errors) == 0 else 1
        if not args.problem:
            print("--problem or --all required", file=sys.stderr)
            return 2
        insp = inspect_problem_completion(root, args.problem)
        print(args.problem)
        print(f"Canonical: {'COMPLETE' if insp.complete else 'INCOMPLETE'}")
        for t in insp.required_targets:
            status = "PRESENT" if t in insp.present_targets else "MISSING"
            print(f"  {t}: {status}")
        if insp.missing_targets:
            print(f"Missing: {', '.join(insp.missing_targets)}")
        from .artifact import inspect_artifact
        from .workflow import workflow_from_relative
        from tools.problem_solution.writer import find_problem_file

        path = find_problem_file(root, args.problem)
        if path:
            rel = path.resolve().relative_to(root.resolve()).as_posix()
            print(f"Workflow: {workflow_from_relative(rel)}")
        art = inspect_artifact(root, problem_id=args.problem, artifact_domain=args.domain)
        print(f"LaTeX: {art.latex.value}")
        print(f"PDF: {art.pdf.value}")
        return 0 if insp.complete or not insp.error else 1

    return 1


if __name__ == "__main__":
    sys.exit(main())
