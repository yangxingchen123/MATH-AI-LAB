"""One-shot Lean sidecar verification. Never writes Knowledge."""

from __future__ import annotations

from pathlib import Path

from .build import run_lake_build
from .constants import LEAN_ROOT
from .correspondence import load_table, undeclared_theorems, validate_table
from .gate import evaluate_gate
from .scan import scan_lean_tree


def verify(project_root: Path | None = None) -> dict:
    root = Path(project_root or LEAN_ROOT)
    hits = scan_lean_tree(root)
    table = load_table(root / "correspondence.yaml")
    correspondence = validate_table(table, root)
    undeclared = undeclared_theorems(root, table)
    build = run_lake_build(root)
    gate = evaluate_gate()
    source_ok = not hits and correspondence.ok and not undeclared
    if not source_ok:
        status = "FAIL"
    elif build.status == "DEGRADED":
        status = "DEGRADED"
    elif build.status == "SUCCEEDED" and gate["status"] == "PASS":
        status = "PASS"
    elif build.status in {"FAILED", "CANCELLED"} or gate["status"] == "FAIL":
        status = "FAIL"
    else:
        status = "DEGRADED"
    return {
        "status": status,
        "core_impact": False,
        "scan_ok": not hits,
        "sorry_admit_axiom": len(hits),
        "correspondence_ok": correspondence.ok,
        "undeclared": undeclared,
        "build_status": build.status,
        "gate_status": gate["status"],
    }
