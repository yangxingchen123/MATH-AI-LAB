"""Contest question / paper-pack coverage audit. Does not write Evidence or PDF."""

from __future__ import annotations

import re
from pathlib import Path

from tools.research_project.constants import REPO_ROOT

from .evidence_candidates import write_evidence_candidates

QUESTION_RE = re.compile(
    r"^(\d+)\.\s+\*\*(.+?)\*\*",
    re.MULTILINE,
)
HINTS: dict[str, tuple[str, ...]] = {
    "1": ("soc", "连续时间", "energy", "clm-0001"),
    "2": ("tte", "time-to-empty", "放空", "clm-0001"),
    "3": ("驱动", "order", "burst", "clm-0004", "差异"),
    "4": ("弹性", "elas_", "share", "clm-0002", "影响"),
    "5": ("敏感", "piecewise", "假设", "clm-0002"),
    "6": ("建议", "recommend", "clm-0003"),
}
TEX_MARKERS: tuple[str, ...] = (
    "abstract",
    "assumption",
    "model",
    "sensitivity",
    "conclusion",
)


def parse_questions(problem_text: str) -> list[dict[str, str]]:
    return [
        {
            "id": f"Q{match.group(1)}",
            "title": match.group(2).strip(),
            "number": match.group(1),
        }
        for match in QUESTION_RE.finditer(problem_text)
    ]


def _blob(project: Path) -> str:
    parts: list[str] = []
    for name in (
        "evidence.md",
        "assumptions.md",
        "decisions.md",
        "model_selection.md",
        "research_dossier.md",
    ):
        path = project / name
        if path.is_file():
            parts.append(path.read_text(encoding="utf-8"))
    return "\n".join(parts).lower()


def audit_contest_coverage(project: Path, tex: Path | None = None) -> dict:
    project = Path(project)
    problem = project / "problem.md"
    problem_text = problem.read_text(encoding="utf-8") if problem.is_file() else ""
    questions = parse_questions(problem_text)
    blob = _blob(project)
    covered = []
    for item in questions:
        hints = HINTS.get(item["number"], (item["title"].lower(),))
        hit = any(token.lower() in blob for token in hints) or item["title"].lower() in blob
        row = dict(item)
        row["covered"] = hit
        covered.append(row)
    lit = project / "literature.md"
    lit_text = lit.read_text(encoding="utf-8") if lit.is_file() else ""
    tex_text = Path(tex).read_text(encoding="utf-8").lower() if tex and Path(tex).is_file() else ""
    missing_tex = [marker for marker in TEX_MARKERS if marker not in tex_text]
    n_covered = sum(1 for item in covered if item["covered"])
    return {
        "questions": covered,
        "covered_count": n_covered,
        "question_count": len(covered),
        "ocr_unresolved": "ocr" in problem_text.lower() or "乱码" in problem_text,
        "literature_records_present": "type=LITERATURE" in lit_text,
        "missing_tex_markers": missing_tex,
        "paper_pack_missing": [
            name
            for name, present in (
                ("summary_sheet", "summary" in tex_text),
                ("ai_use_report", "ai use" in tex_text or "aiuse" in tex_text.replace(" ", "")),
                ("bibliography", "thebibliography" in tex_text or "bibliography" in tex_text),
            )
            if not present
        ],
        "paper_complete": False,
    }


def write_coverage_report(project: Path, tex: Path | None = None) -> tuple[dict, Path]:
    report = audit_contest_coverage(project, tex)
    dest = Path(project) / "documents" / "coverage.md"
    dest.parent.mkdir(parents=True, exist_ok=True)
    missing_tex = ", ".join(report["missing_tex_markers"]) or "none"
    missing_pack = ", ".join(report["paper_pack_missing"]) or "none"
    lines = [
        "# Contest coverage",
        "",
        f"- covered: {report['covered_count']}/{report['question_count']}",
        f"- ocr_unresolved: {report['ocr_unresolved']}",
        f"- literature_records_present: {report['literature_records_present']}",
        f"- missing_tex_markers: {missing_tex}",
        f"- paper_pack_missing: {missing_pack}",
        f"- paper_complete: {report['paper_complete']}",
        "",
        "本文件是问号/论文包审计，不是完稿。不得据此发布 PDF 或写入 Knowledge。",
        "",
        "## Questions",
    ]
    for item in report["questions"]:
        flag = "COVERED" if item["covered"] else "GAP"
        lines.append(f"- {item['id']} [{flag}]: {item['title']}")
    lines.append("")
    dest.write_text("\n".join(lines), encoding="utf-8", newline="\n")
    return report, dest


def run_contest_coverage(
    *,
    name: str,
    repo_root: Path | None = None,
    write_candidates: bool = True,
) -> dict:
    root = Path(repo_root or REPO_ROOT)
    project = root / "07_项目" / name
    code = root / "05_代码" / name
    tex = root / "04_LATEX" / "数学建模" / name / f"{name}.tex"
    if not project.is_dir():
        return {
            "status": "REJECTED",
            "paper_complete": False,
            "message": "project missing",
        }
    candidates: list[Path] = []
    if write_candidates and code.is_dir():
        candidates = write_evidence_candidates(project, code)
    report, path = write_coverage_report(project, tex if tex.is_file() else None)
    report["status"] = "INCOMPLETE"
    report["written"] = str(path)
    report["evidence_candidates"] = [str(item) for item in candidates]
    report["message"] = "coverage audit written; paper is not complete"
    return report
