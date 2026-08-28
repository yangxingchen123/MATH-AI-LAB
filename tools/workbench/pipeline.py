"""Contest paper pipeline. Automates runnable steps; never claims a finished paper."""

from __future__ import annotations

from datetime import date
from pathlib import Path

import yaml

from tools.modeling.select import rank_model_candidates
from tools.open_data.discover import Fetcher
from tools.research_project.constants import REPO_ROOT
from tools.research_project.validator import validate_project

from .coverage import write_coverage_report
from .evidence_candidates import write_evidence_candidates
from .experiment import run_contest_experiment
from .find_data import find_contest_data

DEFAULT_ENGINES: tuple[str, ...] = ("soc", "soc_sensitivity", "soc_piecewise")

HUMAN_GATES: tuple[str, ...] = (
    "核对题面 OCR / 官方 PDF，不得补写乱码句",
    "核开放数据许可证后 ingest，再估参（替换 ASM-0006 假定瓦数）",
    "电压 / Peukert 仅在有开放 I–V 或多倍率数据时扩展，不自动写入",
    "人工改写 MCM 英文论文（Summary Sheet、引用、AI Use Report、≤25 页）",
    "人工审核；未授权不得发布 08_成果输出 PDF，不得写入 Knowledge",
)


def _safe_name(name: str) -> bool:
    if not name or name != name.strip():
        return False
    if any(item in name for item in ("/", "\\", "..", "\x00")):
        return False
    return True


def _step(name: str, status: str, detail: str = "") -> dict[str, str]:
    return {"name": name, "status": status, "detail": detail}


def _write_report(project: Path, report: dict) -> Path:
    dest = project / "documents" / "pipeline_report.md"
    dest.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Contest pipeline report",
        "",
        f"- generated: {date.today().isoformat()}",
        f"- status: {report.get('status')}",
        f"- paper_complete: {report.get('paper_complete')}",
        "",
        "本报告不是完稿论文。自动步骤可以复跑实验和检索候选数据；交卷内容必须人工完成。",
        "",
        "## Auto steps",
    ]
    for item in report.get("steps") or []:
        lines.append(f"- `{item.get('name')}`: {item.get('status')} — {item.get('detail')}")
    coverage = report.get("coverage") or {}
    lines.extend(
        [
            "",
            "## Coverage",
            f"- questions: {coverage.get('covered_count', 0)}/{coverage.get('question_count', 0)}",
            f"- ocr_unresolved: {coverage.get('ocr_unresolved')}",
            f"- literature_records_present: {coverage.get('literature_records_present')}",
            f"- evidence_candidates: {report.get('evidence_candidate_count', 0)}",
        ]
    )
    lines.extend(["", "## Human gates (not automated)"])
    for item in report.get("human_gates") or []:
        lines.append(f"- {item}")
    lines.append("")
    dest.write_text("\n".join(lines), encoding="utf-8", newline="\n")
    return dest


def run_contest_pipeline(
    *,
    name: str,
    repo_root: Path | None = None,
    fetcher: Fetcher | None = None,
    engines: tuple[str, ...] | list[str] | None = None,
    include_seeds: bool = True,
) -> dict:
    if not _safe_name(name):
        return {
            "status": "REJECTED",
            "core_impact": False,
            "paper_complete": False,
            "message": "name must be a single path segment",
            "steps": [],
            "human_gates": list(HUMAN_GATES),
        }
    root = Path(repo_root or REPO_ROOT)
    project = root / "07_项目" / name
    code = root / "05_代码" / name
    tex = root / "04_LATEX" / "数学建模" / name / f"{name}.tex"
    steps: list[dict[str, str]] = []
    if not project.is_dir() or not code.is_dir() or not tex.is_file():
        return {
            "status": "REJECTED",
            "core_impact": False,
            "paper_complete": False,
            "message": "contest scaffold missing (need 07_项目, 05_代码, and LaTeX entrypoint)",
            "steps": [_step("scaffold", "FAIL", "incomplete contest tree")],
            "human_gates": list(HUMAN_GATES),
        }
    steps.append(_step("scaffold", "PASS", "07/05/04 present"))

    check = validate_project(project)
    steps.append(
        _step(
            "dossier_check",
            "PASS" if check.ok else "FAIL",
            "ok" if check.ok else "; ".join(check.errors[:5]),
        )
    )

    candidates_path = code / "configs" / "candidates.yaml"
    if candidates_path.is_file():
        payload = yaml.safe_load(candidates_path.read_text(encoding="utf-8")) or {}
        ranked = rank_model_candidates(list(payload.get("candidates") or []))
        eligible = [item["name"] for item in ranked if item.get("eligible")]
        steps.append(
            _step(
                "select",
                "PASS" if eligible else "FAIL",
                f"eligible={eligible}",
            )
        )
    else:
        ranked = []
        steps.append(_step("select", "SKIPPED", "no candidates.yaml"))

    data = find_contest_data(
        name=name,
        repo_root=root,
        fetcher=fetcher,
        include_seeds=include_seeds,
    )
    steps.append(
        _step(
            "find_data",
            data.get("status", "FAIL"),
            f"open={data.get('open_count', 0)} review={data.get('needs_review_count', 0)}",
        )
    )

    chosen = tuple(engines or DEFAULT_ENGINES)
    for engine in chosen:
        outcome = run_contest_experiment(
            name=name,
            engine=engine,
            run_id=f"{engine}-pipeline-001",
            repo_root=root,
            skip_existing=True,
        )
        steps.append(
            _step(
                f"experiment:{engine}",
                outcome.status,
                outcome.message,
            )
        )

    cand_paths = write_evidence_candidates(project, code)
    steps.append(
        _step(
            "evidence_candidates",
            "PASS" if cand_paths else "SKIPPED",
            f"n={len(cand_paths)}",
        )
    )

    coverage, _cov_path = write_coverage_report(project, tex)
    steps.append(
        _step(
            "coverage",
            "PASS",
            f"{coverage['covered_count']}/{coverage['question_count']} questions; "
            f"ocr={coverage['ocr_unresolved']}",
        )
    )

    steps.append(
        _step("latex_draft", "PASS" if tex.is_file() else "FAIL", tex.name)
    )
    steps.append(_step("publish_pdf", "BLOCKED", "requires explicit user authorization"))

    literature = project / "literature.md"
    lit_text = literature.read_text(encoding="utf-8") if literature.is_file() else ""
    has_lit = "type=LITERATURE" in lit_text
    auto_fail = any(item["status"] in {"FAIL", "REJECTED"} for item in steps if item["name"] != "publish_pdf")
    status = "FAIL" if auto_fail else "INCOMPLETE"
    report = {
        "status": status,
        "core_impact": False,
        "paper_complete": False,
        "message": "auto steps finished; paper is not complete",
        "steps": steps,
        "human_gates": list(HUMAN_GATES),
        "literature_records_present": has_lit,
        "coverage": coverage,
        "evidence_candidate_count": len(cand_paths),
        "select": ranked,
    }
    path = _write_report(project, report)
    report["written"] = str(path)
    return report
