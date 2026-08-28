"""Read-only capability dashboard. Never writes Source."""

from __future__ import annotations

from tools.figure.doctor import doctor as figure_doctor
from tools.lean_formalization.doctor import doctor as lean_doctor
from tools.modeling.doctor import doctor_text as modeling_doctor
from tools.open_data.catalogs import SEED_HITS
from tools.reference_library.ingest import doctor as reference_doctor
from tools.research_project.service import doctor_text as research_doctor


def capability_status() -> dict:
    modeling_text, modeling_code = modeling_doctor()
    research_text, research_code = research_doctor()
    figure = figure_doctor()
    lean = lean_doctor()
    reference = reference_doctor()
    capabilities = [
        {
            "name": "modeling",
            "status": "PASS" if modeling_code == 0 else "FAIL",
            "detail": "stdlib known-answer pilots",
        },
        {
            "name": "figure",
            "status": figure.get("status", "FAIL"),
            "detail": figure.get("engine", ""),
        },
        {
            "name": "lean",
            "status": lean.get("status", "FAIL"),
            "detail": f"build={lean.get('build_status')}",
        },
        {
            "name": "research_project",
            "status": "PASS" if research_code == 0 else "FAIL",
            "detail": "v1.1 contract",
        },
        {
            "name": "reference_library",
            "status": reference.get("status", "FAIL"),
            "detail": "identity ingest; PDF parse sidecar",
        },
        {
            "name": "open_data",
            "status": "PASS",
            "detail": f"catalog discovery sidecar; {len(SEED_HITS)} seed landing pages",
        },
    ]
    statuses = {item["status"] for item in capabilities}
    if "FAIL" in statuses:
        overall = "FAIL"
    elif "DEGRADED" in statuses:
        overall = "DEGRADED"
    else:
        overall = "PASS"
    gaps = []
    if lean.get("status") != "PASS":
        gaps.append("Lean Sidecar is not PASS; lake/toolchain may be missing or build failed.")
    if reference.get("status") != "PASS":
        gaps.append("03_参考资料 taxonomy is incomplete.")
    gaps.append("PDF→MD (MinerU) is a Sidecar and is not installed.")
    gaps.append("Vector retrieval and solver Sidecars are not installed.")
    gaps.append("Open-data search writes candidates only; it does not estimate parameters or ingest literature.")
    gaps.append("Coverage audit writes documents/coverage.md; it does not complete the paper or append official evidence.")
    return {
        "status": overall,
        "core_impact": False,
        "capabilities": capabilities,
        "gaps": gaps,
        "note": "Dashboard only. Does not write Knowledge, Attempt, or formal PDF.",
    }
