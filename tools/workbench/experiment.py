"""Run a stdlib modeling engine into a contest code outputs/ directory."""

from __future__ import annotations

import json
from pathlib import Path

from tools.modeling.runner import (
    run_lp_pilot,
    run_network_pilot,
    run_ode_pilot,
    run_ols_pilot,
    run_quadratic_pilot,
    run_sensitivity_pilot,
    run_soc_pilot,
    run_soc_piecewise_pilot,
    run_soc_sensitivity_pilot,
    run_stats_pilot,
    run_symbolic_pilot,
)
from tools.research_project.constants import REPO_ROOT

from .models import ExperimentResult

ENGINES = {
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


def _safe_name(name: str) -> bool:
    if not name or name != name.strip():
        return False
    if any(item in name for item in ("/", "\\", "..", "\x00")):
        return False
    return True


def run_contest_experiment(
    *,
    name: str,
    engine: str,
    run_id: str,
    repo_root: Path | None = None,
    skip_existing: bool = False,
) -> ExperimentResult:
    if not _safe_name(name) or not _safe_name(run_id):
        return ExperimentResult("REJECTED", "name and run-id must be single path segments")
    if engine not in ENGINES:
        return ExperimentResult("REJECTED", f"unknown engine: {engine}")
    root = Path(repo_root or REPO_ROOT)
    project = root / "07_项目" / name
    code = root / "05_代码" / name
    if not project.is_dir() or not code.is_dir():
        return ExperimentResult("REJECTED", "contest scaffold missing")
    output_root = code / "outputs"
    output_root.mkdir(parents=True, exist_ok=True)
    existing = output_root / run_id
    if skip_existing and (existing / "metrics.json").is_file():
        raw = json.loads((existing / "metrics.json").read_text(encoding="utf-8"))
        metrics = {
            key: float(value)
            for key, value in raw.items()
            if isinstance(value, (int, float))
        }
        return ExperimentResult(
            "SKIPPED",
            "run_id already exists",
            run_id=run_id,
            output_dir=str(existing),
            metrics=metrics,
        )
    try:
        outcome = ENGINES[engine](output_root, run_id)
    except FileExistsError as exc:
        return ExperimentResult("REJECTED", str(exc), run_id=run_id)
    return ExperimentResult(
        status=outcome.status,
        message=outcome.message,
        run_id=outcome.run_id,
        output_dir=outcome.output_dir,
        metrics=outcome.metrics,
    )
