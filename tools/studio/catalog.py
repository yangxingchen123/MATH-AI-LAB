"""Read-only object catalog. IDs come from YAML, never from raw paths."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from tools.knowledge_validator.discovery import discover_markdown_files as discover_knowledge
from tools.knowledge_validator.parser import parse_markdown_file as parse_knowledge
from tools.method_validator.discovery import discover_markdown_files as discover_methods
from tools.method_validator.parser import parse_markdown_file as parse_method
from tools.problem_validator.discovery import discover_markdown_files as discover_problems
from tools.problem_validator.parser import parse_markdown_file as parse_problem
from tools.research_project.constants import PROJECTS_DIRNAME, TEMPLATE_DIRNAME

from .constants import (
    LAB_PROBLEMS_DIR,
    PROBLEM_DIR,
    RESERVED_IDS,
    WORKFLOW_DIRS,
)
from .render import attach_reading


def build_catalog(root: Path) -> dict[str, Any]:
    problems = _scan_problems(root)
    knowledge = _scan_knowledge(root)
    methods = _scan_methods(root)
    projects = _scan_projects(root)
    lab = _scan_lab(root)
    return {
        "writes": False,
        "contract": "studio-0.1",
        "trees": {
            "today": _today_tree(problems, projects),
            "problems": _problem_tree(problems),
            "knowledge": _knowledge_tree(knowledge),
            "methods": [
                {
                    "label": "方法",
                    "items": [{"id": row["id"], "title": row["title"]} for row in methods],
                }
            ]
            if methods
            else [],
            "project": _project_tree(projects),
            "lab": _lab_tree(lab),
        },
    }


def get_document(root: Path, kind: str, doc_id: str) -> dict[str, Any] | None:
    if not isinstance(doc_id, str) or not doc_id or ".." in doc_id.replace("\\", "/"):
        return None
    if kind == "today" and doc_id == "brief":
        return _today_brief(root)
    if kind == "problem" and doc_id == "draft":
        return {
            "kind": "draft",
            "id": "draft",
            "title": "新题",
            "path": "02_题目库/题目模板.md",
            "kind_label": "先分流",
            "body": "",
            "writes": False,
        }
    if kind == "problem":
        return _find_typed(root, _scan_problems(root), doc_id, "习题 / 定理")
    if kind == "knowledge":
        return _find_typed(root, _scan_knowledge(root), doc_id, "审核知识")
    if kind == "method":
        return _find_typed(root, _scan_methods(root), doc_id, "可复用程序")
    if kind == "project":
        return _project_document(root, doc_id)
    if kind == "lab":
        return _lab_document(root, doc_id)
    return None


def workflow_dir_of(relative_path: str) -> str:
    parts = Path(relative_path).parts
    if len(parts) >= 2 and parts[0] == PROBLEM_DIR and parts[1] in WORKFLOW_DIRS:
        return parts[1]
    return ""


def _scan_problems(root: Path) -> list[dict[str, Any]]:
    included, _excluded = discover_problems(root)
    rows: list[dict[str, Any]] = []
    for path in included:
        parsed = parse_problem(path, root)
        row = _from_parse(parsed, expected_type="problem")
        if row is None:
            continue
        row["workflow_dir"] = workflow_dir_of(parsed.relative_path)
        row["parts"] = [str(p) for p in (row["data"].get("parts") or [])]
        knowledge = row["data"].get("knowledge")
        row["knowledge"] = list(knowledge) if isinstance(knowledge, list) else None
        rows.append(row)
    return rows


def _scan_knowledge(root: Path) -> list[dict[str, Any]]:
    included, _excluded = discover_knowledge(root)
    rows: list[dict[str, Any]] = []
    for path in included:
        parsed = parse_knowledge(path, root)
        row = _from_parse(parsed, expected_type="knowledge")
        if row is None:
            continue
        row["domain"] = str(row["data"].get("domain") or "未分组")
        rows.append(row)
    return rows


def _scan_methods(root: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for path in discover_methods(root):
        parsed = parse_method(path, root)
        row = _from_parse(parsed, expected_type="method")
        if row is not None:
            rows.append(row)
    return rows


def _scan_projects(root: Path) -> list[dict[str, Any]]:
    base = root / PROJECTS_DIRNAME
    if not base.is_dir():
        return []
    rows: list[dict[str, Any]] = []
    for child in sorted(base.iterdir(), key=lambda p: p.name):
        if not child.is_dir() or child.name == TEMPLATE_DIRNAME:
            continue
        dossier = child / "research_dossier.md"
        if not dossier.is_file():
            continue
        rows.append(
            {
                "id": child.name,
                "title": child.name,
                "path": f"{PROJECTS_DIRNAME}/{child.name}/research_dossier.md",
                "pages": _project_pages(child),
            }
        )
    return rows


def _scan_lab(root: Path) -> list[dict[str, Any]]:
    base = Path(root) / "tools" / "research_lab" / "problems"
    if not base.is_dir():
        base = LAB_PROBLEMS_DIR
    if not base.is_dir():
        return []
    rows: list[dict[str, Any]] = []
    for path in sorted(base.glob("*.yaml")):
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        oid = data.get("id")
        if not isinstance(oid, str) or oid in RESERVED_IDS:
            continue
        rows.append(
            {
                "id": oid,
                "title": str(data.get("title") or oid),
                "path": path.relative_to(root).as_posix() if _under(path, root) else path.name,
                "stage": data.get("stage"),
                "data": data,
                "body": path.read_text(encoding="utf-8"),
            }
        )
    return rows


def _from_parse(parsed: Any, expected_type: str) -> dict[str, Any] | None:
    data = parsed.data
    if not isinstance(data, dict) or data.get("type") != expected_type:
        return None
    oid = data.get("id")
    if not isinstance(oid, str) or oid in RESERVED_IDS:
        return None
    return {
        "id": oid,
        "title": str(data.get("title") or oid),
        "yaml_status": data.get("status"),
        "path": parsed.relative_path,
        "body": getattr(parsed, "body", "") or _markdown_body(parsed.path),
        "data": data,
    }


def _markdown_body(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    from tools.problem_validator.parser import extract_front_matter

    raw, body, _issues = extract_front_matter(text)
    return body if raw is not None else text


def _find_typed(
    root: Path, rows: list[dict[str, Any]], doc_id: str, kind_label: str
) -> dict[str, Any] | None:
    for row in rows:
        if row["id"] == doc_id:
            return _public_doc(row, kind_label)
    return None


def _public_doc(row: dict[str, Any], kind_label: str) -> dict[str, Any]:
    doc = {
        "kind": "document",
        "id": row["id"],
        "title": row["title"],
        "yaml_status": row.get("yaml_status"),
        "path": row["path"],
        "body": row.get("body") or "",
        "kind_label": kind_label,
        "writes": False,
    }
    if "workflow_dir" in row:
        doc["workflow_dir"] = row["workflow_dir"]
    if "parts" in row:
        doc["parts"] = row["parts"]
    if "knowledge" in row:
        doc["knowledge"] = row["knowledge"]
    if "stage" in row:
        doc["stage"] = row["stage"]
    return attach_reading(doc)


def _project_pages(project: Path) -> list[str]:
    pages = []
    if (project / "research_dossier.md").is_file():
        pages.append("dossier")
    if (project / "decisions.md").is_file():
        pages.append("decisions")
    return pages


def _project_document(root: Path, doc_id: str) -> dict[str, Any] | None:
    page = "research_dossier.md"
    name = doc_id
    if doc_id.endswith("/decisions"):
        name = doc_id[: -len("/decisions")]
        page = "decisions.md"
    if "/" in name or "\\" in name or name == TEMPLATE_DIRNAME:
        return None
    path = (root / PROJECTS_DIRNAME / name / page).resolve()
    parent = (root / PROJECTS_DIRNAME / name).resolve()
    projects = (root / PROJECTS_DIRNAME).resolve()
    try:
        path.relative_to(parent)
        parent.relative_to(projects)
    except ValueError:
        return None
    if TEMPLATE_DIRNAME in path.parts or not path.is_file():
        return None
    rel = path.relative_to(root.resolve()).as_posix()
    return attach_reading(
        {
            "kind": "document",
            "id": doc_id,
            "title": name if page == "research_dossier.md" else f"{name} / decisions",
            "path": rel,
            "body": path.read_text(encoding="utf-8"),
            "kind_label": "竞赛建模",
            "writes": False,
        }
    )


def _lab_document(root: Path, doc_id: str) -> dict[str, Any] | None:
    if doc_id == "operate":
        return attach_reading({
            "kind": "document",
            "id": "operate",
            "title": "运行条件，不是新定理",
            "path": "10_提示词/Research_Lab_Usage_Guide.md",
            "kind_label": "系统 / 运行条件",
            "writes": False,
            "body": (
                "实验室分两层，不要混。\n\n"
                "| 层 | 命令 | 做什么 |\n"
                "| --- | --- | --- |\n"
                "| 运行条件 | `operate` | 根目录、协议、lockfile、禁令 |\n"
                "| 思路 | `protocol` / `route` | 种类分流；卡住必须写障碍 |\n"
                "| 循环 | `cycle` / `funnel` | 状态机与 C0 候选 |\n"
                "| 校准 | `verify` | 复现已知界，不是默认交付 |\n\n"
                "优化系统、运行条件、继续实验室且没有新题面时，"
                "禁止再写 P00xx、再加 Lean 定理、再跑一遍 P001 演示。\n"
            ),
        })
    for row in _scan_lab(root):
        if row["id"] == doc_id:
            return _public_doc(row, "实验室校准")
    return None


def _today_brief(root: Path) -> dict[str, Any]:
    projects = _scan_projects(root)
    focus = projects[0]["title"] if projects else "无进行中项目"
    return attach_reading({
        "kind": "document",
        "id": "brief",
        "title": "先做当前项目，不要再开新题",
        "path": "09_长期记忆/项目进度.md",
        "kind_label": "索引",
        "writes": False,
        "body": (
            f"当前焦点：{focus}。竞赛建模走 Dossier，不进题目库。\n\n"
            "今日页只当索引。从左侧跳到对象。\n\n"
            "| 种类 | 主产出 | 不要做成 |\n"
            "| --- | --- | --- |\n"
            "| 习题 / 定理 | 本题解答 | 小教材或竞赛整卷 |\n"
            "| 竞赛建模 | 可检验模型 + Dossier | 一道 Pxxxx |\n"
            "| 系统 / 运行条件 | 协议 · Gate | 又一道演示题 |\n"
        ),
    })


def _today_tree(problems: list[dict[str, Any]], projects: list[dict[str, Any]]) -> list[dict[str, Any]]:
    current = [{"id": "brief", "title": "今日简报"}]
    if projects:
        current.append({"id": projects[0]["id"], "title": projects[0]["title"], "jump": "project"})
    recent = [{"id": row["id"], "title": row["title"], "jump": "problems"} for row in problems[:2]]
    groups = [{"label": "进行中", "items": current}]
    if recent:
        groups.append({"label": "最近", "items": recent})
    return groups


def _problem_tree(problems: list[dict[str, Any]]) -> list[dict[str, Any]]:
    order = ("研究中", "未解决", "已解决")
    buckets = {name: [] for name in order}
    other: list[dict[str, str]] = []
    for row in problems:
        item = {"id": row["id"], "title": row["title"]}
        wf = row.get("workflow_dir")
        if wf in buckets:
            buckets[wf].append(item)
        else:
            other.append(item)
    groups = [{"label": name, "items": buckets[name]} for name in order if buckets[name]]
    if other:
        groups.append({"label": "其他", "items": other})
    groups.append({"label": "起草", "items": [{"id": "draft", "title": "新题（先分流）"}]})
    return groups


def _knowledge_tree(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    buckets: dict[str, list[dict[str, str]]] = {}
    for row in rows:
        domain = str(row.get("domain") or "未分组")
        buckets.setdefault(domain, []).append({"id": row["id"], "title": row["title"]})
    return [{"label": key, "items": buckets[key]} for key in sorted(buckets)]


def _project_tree(projects: list[dict[str, Any]]) -> list[dict[str, Any]]:
    groups = []
    for row in projects:
        items = [{"id": row["id"], "title": "research_dossier"}]
        if "decisions" in row.get("pages", []):
            items.append({"id": f"{row['id']}/decisions", "title": "decisions"})
        groups.append({"label": row["title"], "items": items})
    return groups


def _lab_tree(lab: list[dict[str, Any]]) -> list[dict[str, Any]]:
    groups = [{"label": "运行条件", "items": [{"id": "operate", "title": "分层与禁令"}]}]
    if lab:
        groups.append(
            {
                "label": "校准",
                "items": [{"id": row["id"], "title": row["title"]} for row in lab],
            }
        )
    return groups


def _under(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except ValueError:
        return False
