"""Contest-modeling sidecar. Missing numpy is DEGRADED, not Core FAIL."""

from __future__ import annotations

import importlib
import importlib.util
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
VENDOR_ROOT = REPO_ROOT / "vendor" / "math-modeling-skills"
CURSOR_SKILL_ROOT = REPO_ROOT / ".cursor" / "skills"
CONTEST_REQUIREMENTS = REPO_ROOT / "tools" / "modeling" / "requirements-contest.txt"
CONTEST_ML_REQUIREMENTS = REPO_ROOT / "tools" / "modeling" / "requirements-contest-ml.txt"
INTEGRATED_AHP_TEMPLATE = (
    REPO_ROOT
    / "05_代码"
    / "_模板"
    / "数模竞赛_v1"
    / "python"
    / "evaluation"
    / "ahp_template.py"
)
VENDOR_AHP_TEMPLATE = (
    VENDOR_ROOT
    / "skills"
    / "math-modeling-solver"
    / "references"
    / "code-templates"
    / "python"
    / "evaluation"
    / "ahp_template.py"
)
AHP_TEMPLATE = INTEGRATED_AHP_TEMPLATE

REQUIRED_VENDOR_FILES: tuple[Path, ...] = (
    VENDOR_ROOT / "LICENSE",
    VENDOR_ROOT / "UPSTREAM.md",
    VENDOR_ROOT / "skills" / "math-modeling-solver" / "SKILL.md",
    VENDOR_ROOT / "skills" / "math-modeling-paper" / "SKILL.md",
    VENDOR_AHP_TEMPLATE,
)
REQUIRED_CURSOR_FILES: tuple[Path, ...] = (
    CURSOR_SKILL_ROOT / "math-modeling-lab" / "SKILL.md",
    CURSOR_SKILL_ROOT / "math-modeling-solver" / "SKILL.md",
    CURSOR_SKILL_ROOT / "math-modeling-solver" / "references" / "problem-decomposition.md",
    CURSOR_SKILL_ROOT / "math-modeling-paper" / "SKILL.md",
    CURSOR_SKILL_ROOT / "math-modeling-paper" / "references" / "cumcm-guide.md",
    INTEGRATED_AHP_TEMPLATE,
)
REQUIRED_CURSOR_SKILLS: tuple[str, ...] = (
    "math-modeling-lab",
    "math-modeling-solver",
    "math-modeling-paper",
)
CORE_MODULES: tuple[str, ...] = ("numpy", "scipy", "matplotlib", "pandas")
ML_MODULES: tuple[str, ...] = ("sklearn", "statsmodels", "seaborn", "xgboost")
INSTALL_HINT = "python -m pip install -r tools/modeling/requirements-contest.txt"


def probe_module(name: str) -> bool:
    try:
        importlib.import_module(name)
    except Exception:
        return False
    return True


def _files_ok(paths: tuple[Path, ...]) -> bool:
    return all(path.is_file() for path in paths)


def _cursor_skills_ok() -> bool:
    return _files_ok(REQUIRED_CURSOR_FILES)


def module_report(names: tuple[str, ...]) -> dict[str, bool]:
    return {name: probe_module(name) for name in names}


def doctor() -> dict[str, Any]:
    vendor = "PASS" if _files_ok(REQUIRED_VENDOR_FILES) else "FAIL"
    cursor_skills = "PASS" if _cursor_skills_ok() else "FAIL"
    core = module_report(CORE_MODULES)
    ml = module_report(ML_MODULES)
    core_ok = all(core.values())
    if vendor != "PASS" or cursor_skills != "PASS":
        status = "FAIL"
    elif core_ok:
        status = "PASS"
    else:
        status = "DEGRADED"
    missing_core = [name for name, ok in core.items() if not ok]
    missing_ml = [name for name, ok in ml.items() if not ok]
    return {
        "status": status,
        "core_impact": False,
        "vendor": vendor,
        "cursor_skills": cursor_skills,
        "core_modules": core,
        "ml_modules": ml,
        "missing_core": missing_core,
        "missing_ml": missing_ml,
        "install": INSTALL_HINT,
        "note": (
            "Contest templates are copied into .cursor/skills and 05_代码/_模板/数模竞赛_v1. "
            "numpy/scipy/matplotlib/pandas are a sidecar; do not add them to root requirements.txt. "
            "sklearn/statsmodels/seaborn/xgboost are optional ML extras."
        ),
    }


def doctor_text() -> tuple[str, int]:
    report = doctor()
    lines = [
        "Contest Modeling Sidecar",
        f"status: {report['status']}",
        f"core_impact: {str(report['core_impact']).lower()}",
        f"vendor: {report['vendor']}",
        f"cursor_skills: {report['cursor_skills']}",
        "core_modules: "
        + ", ".join(
            f"{name}={'OK' if ok else 'MISSING'}"
            for name, ok in report["core_modules"].items()
        ),
        "ml_modules: "
        + ", ".join(
            f"{name}={'OK' if ok else 'MISSING'}"
            for name, ok in report["ml_modules"].items()
        ),
        f"install: {report['install']}",
        report["note"],
    ]
    code = 0 if report["status"] in {"PASS", "DEGRADED"} else 1
    return "\n".join(lines) + "\n", code


def _load_ahp_module():
    spec = importlib.util.spec_from_file_location("mathailab_ahp_template", AHP_TEMPLATE)
    if spec is None or spec.loader is None:
        raise FileNotFoundError(str(AHP_TEMPLATE))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def smoke_ahp() -> dict[str, Any]:
    if not probe_module("numpy"):
        return {
            "status": "SKIPPED",
            "message": "numpy sidecar missing; " + INSTALL_HINT,
        }
    numpy = importlib.import_module("numpy")
    module = _load_ahp_module()
    matrix = numpy.array(
        [
            [1.0, 1.0 / 3.0, 1.0 / 5.0],
            [3.0, 1.0, 1.0 / 2.0],
            [5.0, 2.0, 1.0],
        ]
    )
    weights, _lambda_max, cr, consistent = module.ahp_weight(matrix)
    weight_sum = float(numpy.real(weights).sum())
    cr_value = float(numpy.real(cr))
    ok = abs(weight_sum - 1.0) < 1e-9 and cr_value < 0.1 and bool(consistent)
    return {
        "status": "SUCCEEDED" if ok else "FAILED",
        "weight_sum": weight_sum,
        "cr": cr_value,
        "consistent": bool(consistent),
        "message": "AHP template known-answer smoke",
    }


def smoke_text() -> tuple[str, int]:
    doctor_body, doctor_code = doctor_text()
    outcome = smoke_ahp()
    lines = [
        doctor_body.rstrip(),
        f"ahp_smoke: {outcome['status']}",
        outcome.get("message", ""),
    ]
    if outcome["status"] == "SUCCEEDED":
        lines.append(f"ahp_weight_sum: {outcome['weight_sum']}")
        lines.append(f"ahp_cr: {outcome['cr']}")
        return "\n".join(lines) + "\n", 0
    if outcome["status"] == "SKIPPED":
        return "\n".join(lines) + "\n", doctor_code
    return "\n".join(lines) + "\n", 1
