"""Read-only v1.5 figure gate. Does not write production Source."""

from __future__ import annotations

import json
from pathlib import Path
from tempfile import TemporaryDirectory

from tools.artifact_consistency.checks import check_latex_figures
from tools.modeling.runner import run_network_pilot, run_quadratic_pilot

from .checks import check_ai_misuse, check_semantic
from .constants import GATE_METRIC_NAMES
from .manifest import load_manifest, validate_manifest
from .renderer import (
    render_architecture,
    render_exact_function,
    render_network,
    render_numerical,
)

THRESHOLD_RATE = "100%"
THRESHOLD_ZERO = 0


def evaluate_gate() -> dict:
    with TemporaryDirectory() as tmp:
        root = Path(tmp)
        net_run = run_network_pilot(root / "runs", "net-pilot-001")
        opt_run = run_quadratic_pilot(root / "runs", "opt-pilot-001")
        figures = [
            render_numerical(root / "figs", opt_run.run_id),
            render_network(root / "figs", net_run.run_id),
            render_exact_function(root / "figs", opt_run.run_id),
            render_architecture(root / "figs"),
        ]
        rebuild_ok = 0
        semantic_ok = 0
        access_ok = 0
        provenance_ok = 0
        export_edits = 0
        for figure in figures:
            manifest = load_manifest(figure.manifest_path)
            valid = validate_manifest(manifest)
            semantic = json.loads(figure.semantic_path.read_text(encoding="utf-8"))
            svg_text = figure.svg_path.read_text(encoding="utf-8")
            semantic_check = check_semantic(manifest, svg_text, semantic)
            listed = {
                item.get("ref"): item.get("sha256")
                for item in manifest.get("outputs") or []
                if isinstance(item, dict)
            }
            if listed.get("figure.svg") != figure.svg_sha256:
                export_edits += 1
            if valid.ok and manifest.get("claim_refs") and manifest.get("source_code"):
                if figure.family == "architecture" or manifest.get("run_refs"):
                    provenance_ok += 1
            if semantic_check.ok:
                semantic_ok += 1
            checks = manifest.get("semantic_checks") or {}
            if checks.get("grayscale") and checks.get("color_vision"):
                access_ok += 1
            rebuilt = _rebuild(figure.family, root / "rebuild", figure.figure_id)
            if rebuilt == figure.svg_sha256:
                rebuild_ok += 1
        ai_fail = check_ai_misuse(
            {
                "family": "numerical_uncertainty",
                "engine": {"name": "ai-image"},
            }
        )
        latex_root = root / "latex"
        latex_root.mkdir()
        (latex_root / "paper.tex").write_text("\\includegraphics{orphan.png}\n", encoding="utf-8")
        latex_blocked = not check_latex_figures(latex_root, root / "figs").ok
    metrics = [
        _metric("four_pilot_provenance_coverage", provenance_ok, 4),
        _metric("rebuild_success_rate", rebuild_ok, 4),
        _metric("semantic_check_pass_rate", semantic_ok, 4),
        _metric("grayscale_colorvision_pass_rate", access_ok, 4),
        {
            "name": "export_only_edit_count",
            "value": export_edits,
            "threshold": THRESHOLD_ZERO,
            "status": "PASS" if export_edits == 0 else "FAIL",
            "detail": "manifest output hash matches SVG bytes",
        },
        {
            "name": "unprovenanced_latex_count",
            "value": 0 if latex_blocked else 1,
            "threshold": THRESHOLD_ZERO,
            "status": "PASS" if latex_blocked else "FAIL",
            "detail": "detector blocked orphan includegraphics"
            if latex_blocked
            else "orphan includegraphics was not blocked",
        },
        {
            "name": "ai_as_exact_count",
            "value": 0 if not ai_fail.ok else 1,
            "threshold": THRESHOLD_ZERO,
            "status": "PASS" if not ai_fail.ok else "FAIL",
            "detail": "; ".join(ai_fail.errors) or "detector silent",
        },
    ]
    by_name = {item["name"]: item for item in metrics}
    ordered = [by_name[name] for name in GATE_METRIC_NAMES]
    status = "PASS" if all(item["status"] == "PASS" for item in ordered) else "FAIL"
    return {"contract_version": "1.5", "status": status, "metrics": ordered}


def _rebuild(family: str, root: Path, figure_id: str) -> str:
    mapping = {
        "numerical_uncertainty": lambda: render_numerical(root, "opt-pilot-001", figure_id),
        "network": lambda: render_network(root, "net-pilot-001", figure_id),
        "exact_function": lambda: render_exact_function(root, "opt-pilot-001", figure_id),
        "architecture": lambda: render_architecture(root, figure_id),
    }
    return mapping[family]().svg_sha256


def _metric(name: str, value: int, total: int) -> dict:
    status = "PASS" if total and value == total else "FAIL"
    return {
        "name": name,
        "value": value / total if total else 0.0,
        "threshold": THRESHOLD_RATE,
        "status": status,
        "detail": f"{value}/{total}",
    }
