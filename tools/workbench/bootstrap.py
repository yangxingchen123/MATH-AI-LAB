"""One-command contest modeling scaffold. Does not write Knowledge or PDF."""

from __future__ import annotations

import shutil
from pathlib import Path

from tools.research_project.constants import REPO_ROOT
from tools.research_project.models import ResearchProjectOperationKind
from tools.research_project.operations import init_project
from tools.research_project.validator import validate_project

from .models import BootstrapResult

CODE_TEMPLATE = REPO_ROOT / "05_代码" / "_模板" / "建模实验_v1"
LATEX_TEMPLATE = REPO_ROOT / "04_LATEX" / "模板" / "数学建模论文模板_v1" / "国赛论文.tex"


def _safe_name(name: str) -> bool:
    if not name or name != name.strip():
        return False
    if any(item in name for item in ("/", "\\", "..", "\x00")):
        return False
    return True


def bootstrap_contest(
    *,
    name: str,
    title: str,
    repo_root: Path | None = None,
) -> BootstrapResult:
    if not _safe_name(name):
        return BootstrapResult("REJECTED", "name must be a single path segment")
    root = Path(repo_root or REPO_ROOT)
    project = root / "07_项目" / name
    code = root / "05_代码" / name
    latex_dir = root / "04_LATEX" / "数学建模" / name
    tex = latex_dir / f"{name}.tex"
    if project.exists() and code.exists() and tex.is_file():
        check = validate_project(project)
        if check.ok:
            return BootstrapResult("NO_OP", "contest scaffold already present", project, code, latex_dir)
        return BootstrapResult("REJECTED", "; ".join(check.errors) or "incomplete contest scaffold")
    if project.exists() or code.exists() or latex_dir.exists():
        return BootstrapResult("REJECTED", "partial contest scaffold already exists")
    created = init_project(project, title, repo_root=root, kind="contest_modeling")
    if created.kind != ResearchProjectOperationKind.WRITTEN:
        return BootstrapResult("REJECTED", created.message)
    shutil.copytree(CODE_TEMPLATE, code)
    latex_dir.mkdir(parents=True)
    text = LATEX_TEMPLATE.read_text(encoding="utf-8").replace("论文标题", title)
    tex.write_text(text, encoding="utf-8", newline="\n")
    plan = project / "experiment_plan.md"
    extra = (
        f"\n- 代码工程: `05_代码/{name}/`\n"
        f"- LaTeX: `04_LATEX/数学建模/{name}/{name}.tex`\n"
    )
    if plan.is_file():
        plan.write_text(plan.read_text(encoding="utf-8") + extra, encoding="utf-8", newline="\n")
    return BootstrapResult("WRITTEN", "created contest dossier, code, and LaTeX scaffold", project, code, latex_dir)
