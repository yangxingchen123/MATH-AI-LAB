"""Report Lean toolchain availability without blocking Core."""

from __future__ import annotations

from .build import lake_available, lake_executable, run_lake_build, toolchain_present
from .constants import CONTRACT_VERSION, LEAN_ROOT
from .correspondence import load_table, validate_table
from .scan import scan_lean_tree


def doctor() -> dict:
    build = run_lake_build(LEAN_ROOT)
    hits = scan_lean_tree(LEAN_ROOT)
    table = load_table(LEAN_ROOT / "correspondence.yaml")
    correspondence = validate_table(table, LEAN_ROOT)
    if build.status == "SUCCEEDED" and not hits and correspondence.ok:
        status = "PASS"
    elif build.status in {"FAILED", "CANCELLED"}:
        status = "FAIL"
    else:
        status = "DEGRADED"
    return {
        "status": status,
        "core_impact": False,
        "lake": "available" if lake_available() else "missing",
        "lake_path": lake_executable(),
        "toolchain_present": toolchain_present(),
        "build_status": build.status,
        "sorry_admit_axiom": len(hits),
        "correspondence_ok": correspondence.ok,
        "project_root": str(LEAN_ROOT),
        "contract_version": CONTRACT_VERSION,
        "note": "Uses ~/.elan/bin when PATH has no lake (VS Code Lean 4 default). Sidecar failure must not fail Core.",
    }
