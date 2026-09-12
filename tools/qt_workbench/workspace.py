"""In-process workspace listing. Reuses studio catalog. No HTTP."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from tools.studio.catalog import build_catalog, get_document
from tools.studio.render import attach_reading

from .nav import FILE_KINDS, STUDIO_KINDS

SKIP_DIR_NAMES = {"自动索引", "_模板", "vendor", ".git", "node_modules", ".pytest_cache"}

FILE_ROOTS: dict[str, str] = {
    "memory": "09_长期记忆",
    "inbox": "00_收件箱",
    "prompts": "10_提示词",
    "references": "03_参考资料",
    "outputs": "08_成果输出",
}

KIND_LABELS = {
    "knowledge": "审核知识",
    "problem": "习题 / 定理",
    "method": "可复用程序",
    "project": "研究项目",
    "lab": "实验室校准",
    "memory": "长期记忆",
    "inbox": "收件箱",
    "prompts": "提示词",
    "references": "参考资料",
    "outputs": "成果输出",
    "lean": "Lean 对照",
    "exploration": "数学探索",
}


def snapshot(root: Path) -> dict[str, Any]:
    catalog = build_catalog(root)
    return {
        "writes": False,
        "transport": "in-process",
        "trees": catalog["trees"],
        "counts": {
            "knowledge": _count_tree(catalog["trees"].get("knowledge") or []),
            "problems": _count_tree(catalog["trees"].get("problems") or []),
            "methods": _count_tree(catalog["trees"].get("methods") or []),
            "projects": _count_tree(catalog["trees"].get("project") or []),
            "lab": _count_tree(catalog["trees"].get("lab") or []),
        },
    }


def list_objects(root: Path, kind: str) -> list[dict[str, Any]]:
    if kind in STUDIO_KINDS:
        catalog = build_catalog(root)
        key = {
            "knowledge": "knowledge",
            "problem": "problems",
            "method": "methods",
            "project": "project",
            "lab": "lab",
        }[kind]
        return _flatten(catalog["trees"].get(key) or [])
    if kind in FILE_KINDS:
        return list_files(root, FILE_ROOTS[kind])
    if kind == "lean":
        return list_lean(root)
    if kind == "exploration":
        from tools.research_lab.exploration import exploration_index

        return exploration_index()
    return []


def list_attempts(root: Path, problem_id: str) -> list[dict[str, Any]]:
    if not isinstance(problem_id, str) or not problem_id or ".." in problem_id:
        return []
    from tools.attempt_validator.constants import ATTEMPT_DIR_NAME
    from tools.attempt_validator.ledger import load_ledger_file

    path = root / ATTEMPT_DIR_NAME / f"{problem_id}.md"
    if not path.is_file():
        return []
    loaded = load_ledger_file(path, root)
    rows: list[dict[str, Any]] = []
    for record in loaded.attempts:
        aid = record.get("id")
        if not isinstance(aid, str):
            continue
        rows.append(
            {
                "id": aid,
                "part": record.get("part"),
                "outcome": record.get("outcome"),
                "assistance": record.get("assistance"),
                "attempted_at": record.get("attempted_at"),
                "narrative": loaded.sections.get(aid, ""),
            }
        )
    return rows


def search_exploration(query: str) -> list[dict[str, Any]]:
    needle = query.strip().lower()
    if not needle:
        return []
    from tools.research_lab.exploration import exploration_index

    hits: list[dict[str, Any]] = []
    for row in exploration_index():
        blob = "\n".join(str(row.get(key) or "") for key in ("id", "title", "group", "body"))
        if needle not in blob.lower():
            continue
        hits.append(
            {
                "id": row.get("id"),
                "title": row.get("title"),
                "group": row.get("group"),
            }
        )
    return hits


def inbox_promote_id(object_id: str) -> str | None:
    if not isinstance(object_id, str) or not object_id or ".." in object_id.replace("\\", "/"):
        return None
    path = Path(object_id)
    parts = path.parts
    if len(parts) == 2 and parts[0] == FILE_ROOTS["inbox"]:
        name = parts[1]
    elif len(parts) == 1:
        name = parts[0]
    else:
        return None
    if name.lower() == "readme.md":
        return None
    return name


def get_object(root: Path, kind: str, object_id: str) -> dict[str, Any] | None:
    if not isinstance(object_id, str) or not object_id or ".." in object_id.replace("\\", "/"):
        return None
    if kind in STUDIO_KINDS:
        studio_kind = "today" if kind == "home" else kind
        return get_document(root, studio_kind, object_id)
    if kind in FILE_KINDS:
        return read_file_document(root, object_id, KIND_LABELS[kind])
    if kind == "lean":
        return get_lean_document(root, object_id)
    if kind == "exploration":
        from tools.research_lab.exploration import lookup_index

        row = lookup_index(object_id)
        if row is None:
            return None
        return {
            "id": object_id,
            "title": row.get("title") or object_id,
            "kind_label": row.get("group") or KIND_LABELS["exploration"],
            "path": "packages/domain-exploration",
            "body": row.get("body") or "",
        }
    return None


def list_files(root: Path, relative: str, *, limit: int = 200) -> list[dict[str, Any]]:
    base = (root / relative).resolve()
    root_resolved = root.resolve()
    try:
        base.relative_to(root_resolved)
    except ValueError:
        return []
    if not base.is_dir():
        return []
    rows: list[dict[str, Any]] = []
    for path in sorted(base.rglob("*")):
        if len(rows) >= limit:
            break
        if not path.is_file():
            continue
        if any(part in SKIP_DIR_NAMES for part in path.parts):
            continue
        if path.suffix.lower() not in {".md", ".pdf", ".yaml", ".yml", ".txt"}:
            continue
        rel = path.relative_to(root_resolved).as_posix()
        rows.append({"id": rel, "title": path.stem, "group": path.parent.name})
    return rows


def read_file_document(root: Path, relative: str, kind_label: str) -> dict[str, Any] | None:
    path = _safe_file(root, relative)
    if path is None:
        return None
    if path.suffix.lower() == ".pdf":
        body = f"PDF 文件。请在仓库中打开：\n\n`{relative}`"
    else:
        body = path.read_text(encoding="utf-8")
    return attach_reading(
        {
            "kind": "document",
            "id": relative,
            "title": path.stem,
            "path": relative,
            "body": body,
            "kind_label": kind_label,
            "writes": False,
        }
    )


def list_lean(root: Path) -> list[dict[str, Any]]:
    table = _load_correspondence(root)
    rows: list[dict[str, Any]] = []
    for item in table:
        oid = item.get("id")
        if not isinstance(oid, str):
            continue
        rows.append(
            {
                "id": oid,
                "title": str(item.get("natural_language") or oid),
                "group": str(item.get("family") or "lean"),
            }
        )
    return rows


def get_lean_document(root: Path, object_id: str) -> dict[str, Any] | None:
    for item in _load_correspondence(root):
        if item.get("id") != object_id:
            continue
        ref = item.get("natural_language_ref")
        body = ""
        path = f"06_LEAN形式化/correspondence.yaml#{object_id}"
        if isinstance(ref, str):
            statement = _safe_file(root, f"06_LEAN形式化/{ref}")
            if statement is not None:
                body = statement.read_text(encoding="utf-8")
                path = f"06_LEAN形式化/{ref}"
        if not body:
            body = (
                f"{item.get('natural_language') or object_id}\n\n"
                f"lean_file: `{item.get('lean_file')}`\n\n"
                "对照表条目不等于已验证。"
            )
        return attach_reading(
            {
                "kind": "document",
                "id": object_id,
                "title": str(item.get("natural_language") or object_id),
                "path": path,
                "body": body,
                "kind_label": "Lean 对照",
                "yaml_status": None,
                "writes": False,
            }
        )
    return None


def _load_correspondence(root: Path) -> list[dict[str, Any]]:
    path = root / "06_LEAN形式化" / "correspondence.yaml"
    if not path.is_file():
        return []
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    theorems = data.get("theorems")
    if not isinstance(theorems, list):
        return []
    return [row for row in theorems if isinstance(row, dict)]


def _safe_file(root: Path, relative: str) -> Path | None:
    if not relative or ".." in Path(relative).parts:
        return None
    path = (root / relative).resolve()
    try:
        path.relative_to(root.resolve())
    except ValueError:
        return None
    return path if path.is_file() else None


def _flatten(groups: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for group in groups:
        label = str(group.get("label") or "")
        for item in group.get("items") or []:
            if not isinstance(item, dict) or not item.get("id"):
                continue
            jump = item.get("jump")
            rows.append(
                {
                    "id": item["id"],
                    "title": str(item.get("title") or item["id"]),
                    "group": label,
                    "jump": jump,
                }
            )
    return rows


def _count_tree(groups: list[dict[str, Any]]) -> int:
    return sum(len(group.get("items") or []) for group in groups)
