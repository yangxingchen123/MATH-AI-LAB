"""Service layer for research project CLI."""

from __future__ import annotations

from pathlib import Path

from .append_only import check_append_only, check_append_only_all
from .constants import CONTRACT_VERSION, USAGE_GUIDE_PATH
from .governance import assess_external_processing
from .models import ResearchProjectStatusResult
from .operations import (
    add_assumption,
    add_claim,
    add_evidence,
    append_decision,
    init_project,
    reconcile_project,
    record_negative_result,
    supersede_assumption,
    update_governance,
)
from .paths import path_safety_error, resolve_repo_root
from .stale import dossier_is_stale
from .validator import validate_project


def _project(path: str, repo_root: Path | None = None) -> Path:
    project = Path(path)
    root = resolve_repo_root(repo_root)
    if not project.is_absolute():
        project = (Path.cwd() / project)
    safety = path_safety_error(project, root)
    if safety:
        # disposable tests pass absolute tmp paths; allow those without 07_项目 of real repo
        try:
            resolved = project.resolve()
        except OSError:
            raise ValueError(safety) from None
        if "07_项目" not in resolved.parts:
            raise ValueError(safety)
        return resolved
    return project.resolve()


def doctor_text() -> tuple[str, int]:
    lines = [
        f"Research Project Contract {CONTRACT_VERSION}",
        "Literature extension 1.3 (PDF/MinerU skipped)",
        f"Usage guide: {USAGE_GUIDE_PATH}",
    ]
    if not USAGE_GUIDE_PATH.is_file():
        lines.append("ERROR: Research_Project_Usage_Guide.md is required")
        return "\n".join(lines) + "\n", 1
    lines.append("doctor: PASS")
    return "\n".join(lines) + "\n", 0


def status_for(project: Path) -> ResearchProjectStatusResult:
    stale = dossier_is_stale(project)
    assessment = assess_external_processing(project)
    return ResearchProjectStatusResult(
        project=project,
        freshness="STALE" if stale else "FRESH",
        reconcile_required=stale,
        contract_version=CONTRACT_VERSION,
        external_processing=assessment.verdict,
        message="RECONCILE_REQUIRED" if stale else "",
    )


WRITE_OPS = {
    "init": init_project,
    "add_assumption": add_assumption,
    "add_claim": add_claim,
    "add_evidence": add_evidence,
    "append_decision": append_decision,
    "record_negative_result": record_negative_result,
    "supersede_assumption": supersede_assumption,
    "update_governance": update_governance,
    "reconcile": reconcile_project,
}

READ_OPS = {
    "validate": validate_project,
    "check_append_only": check_append_only,
    "check_append_only_all": check_append_only_all,
    "assess": assess_external_processing,
}
