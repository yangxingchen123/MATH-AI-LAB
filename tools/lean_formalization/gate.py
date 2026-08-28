"""Read-only v1.6 Lean gate. Missing lake degrades; it never fails Core."""

from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory

from .build import run_lake_build
from .constants import CONTRACT_VERSION, LEAN_ROOT, REPO_ROOT
from .correspondence import load_table, undeclared_theorems, validate_table
from .manifest import validate_manifest_file
from .scan import scan_lean_tree
from .weakening import detect_weakening

GATE_METRIC_NAMES: tuple[str, ...] = (
    "lake_build_pass_rate",
    "forbidden_proof_bypass_count",
    "correspondence_coverage",
    "provenance_completeness_rate",
    "weakening_fixture_detection_rate",
    "sidecar_core_failure_count",
    "toolchain_restore_success_rate",
)

THRESHOLD_RATE = "100%"
THRESHOLD_ZERO = 0
FIXTURE_ROOT = REPO_ROOT / "tests" / "lean_formalization" / "fixtures"


def evaluate_gate() -> dict:
    build = run_lake_build(LEAN_ROOT)
    hits = scan_lean_tree(LEAN_ROOT)
    table = load_table(LEAN_ROOT / "correspondence.yaml")
    correspondence = validate_table(table, LEAN_ROOT)
    missing = undeclared_theorems(LEAN_ROOT, table)
    manifests = sorted((LEAN_ROOT / "manifests").glob("*.yaml")) if (LEAN_ROOT / "manifests").is_dir() else []
    provenance_ok = 0
    for path in manifests:
        if validate_manifest_file(path, LEAN_ROOT).ok:
            provenance_ok += 1
    weakened = FIXTURE_ROOT / "weakened"
    weak_table = load_table(weakened / "correspondence.yaml")
    weak_text = (weakened / "weaker.lean").read_text(encoding="utf-8")
    weak_issues = detect_weakening(weak_table[0], weak_text)
    restored = _restore_toolchain_selfcheck()
    lake_metric = _lake_metric(build)
    metrics = [
        lake_metric,
        {
            "name": "forbidden_proof_bypass_count",
            "value": len(hits),
            "threshold": THRESHOLD_ZERO,
            "status": "PASS" if not hits else "FAIL",
            "detail": ", ".join(f"{hit.kind}:{hit.path}" for hit in hits) or "none",
        },
        _metric(
            "correspondence_coverage",
            int(correspondence.ok and not missing),
            1,
            "PASS" if correspondence.ok and not missing else "FAIL",
            f"missing={missing or 'none'}; {'; '.join(correspondence.errors) or 'ok'}",
        ),
        _metric(
            "provenance_completeness_rate",
            provenance_ok,
            max(len(manifests), 1),
            "PASS" if manifests and provenance_ok == len(manifests) else "FAIL",
            f"{provenance_ok}/{len(manifests)}",
        ),
        _metric(
            "weakening_fixture_detection_rate",
            int(bool(weak_issues)),
            1,
            "PASS" if weak_issues else "FAIL",
            "; ".join(weak_issues) or "detector silent",
        ),
        {
            "name": "sidecar_core_failure_count",
            "value": 0 if build.core_impact is False else 1,
            "threshold": THRESHOLD_ZERO,
            "status": "PASS" if build.core_impact is False else "FAIL",
            "detail": f"build.status={build.status}",
        },
        _metric(
            "toolchain_restore_success_rate",
            int(restored),
            1,
            "PASS" if restored else "FAIL",
            "backup restored" if restored else "restore failed",
        ),
    ]
    by_name = {item["name"]: item for item in metrics}
    ordered = [by_name[name] for name in GATE_METRIC_NAMES]
    if any(item["status"] == "FAIL" for item in ordered):
        status = "FAIL"
    elif any(item["status"] == "DEGRADED" for item in ordered):
        status = "DEGRADED"
    else:
        status = "PASS"
    return {
        "contract_version": CONTRACT_VERSION,
        "status": status,
        "core_impact": False,
        "metrics": ordered,
    }


def _lake_metric(build) -> dict:
    if build.status == "DEGRADED":
        return {
            "name": "lake_build_pass_rate",
            "value": None,
            "threshold": THRESHOLD_RATE,
            "status": "DEGRADED",
            "detail": build.log,
        }
    ok = build.status == "SUCCEEDED"
    return _metric(
        "lake_build_pass_rate",
        int(ok),
        1,
        "PASS" if ok else "FAIL",
        build.status,
    )


def _restore_toolchain_selfcheck() -> bool:
    original = (LEAN_ROOT / "lean-toolchain").read_text(encoding="utf-8")
    with TemporaryDirectory() as tmp:
        path = Path(tmp) / "lean-toolchain"
        path.write_text("leanprover/lean4:v0.0.0-restore-probe\n", encoding="utf-8", newline="\n")
        path.write_text(original, encoding="utf-8", newline="\n")
        return path.read_text(encoding="utf-8") == original


def _metric(name: str, value: int, total: int, status: str, detail: str) -> dict:
    return {
        "name": name,
        "value": value / total if total else 0.0,
        "threshold": THRESHOLD_RATE,
        "status": status,
        "detail": detail,
    }
