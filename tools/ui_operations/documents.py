"""Resolve allowlisted documents by object id. Payload never includes a filesystem path key."""

from __future__ import annotations

from pathlib import Path

from tools.knowledge_validator.discovery import discover_markdown_files as discover_knowledge
from tools.method_validator.discovery import discover_markdown_files as discover_methods
from tools.problem_solution.writer import find_problem_file
from tools.problem_validator.parser import extract_front_matter, parse_yaml_mapping
from tools.research_project.constants import PROJECTS_DIRNAME, TEMPLATE_DIRNAME

FROZEN_TYPES = frozenset({"knowledge", "problem", "method"})
NOTE_TYPES = frozenset({"memory", "inbox", "prompts", "project"})
EDITABLE_TYPES = FROZEN_TYPES | NOTE_TYPES
NOTE_ROOTS = {
    "memory": "09_长期记忆",
    "inbox": "00_收件箱",
    "prompts": "10_提示词",
}
SKIP_DIR_NAMES = {"自动索引", "_模板", "vendor", ".git", "node_modules"}
RESERVED = frozenset({"K0000", "P0000", "M0000"})


def reassemble(raw_yaml: str, body: str) -> str:
    body = body.replace("\r\n", "\n")
    if body and not body.startswith("\n"):
        body = "\n" + body
    if body and not body.endswith("\n"):
        body += "\n"
    return f"---\n{raw_yaml.rstrip()}\n---\n{body}"


def locate(root: Path, object_type: str, object_id: str) -> tuple[Path, str, str | None] | None:
    """Return (path, original_text, raw_yaml_or_none)."""
    if object_type not in EDITABLE_TYPES:
        return None
    if not isinstance(object_id, str) or not object_id.strip():
        return None
    if object_id in RESERVED:
        return None
    if ".." in object_id.replace("\\", "/"):
        return None
    root = root.resolve()
    if object_type == "problem":
        path = find_problem_file(root, object_id)
        return _read_source(path) if path is not None else None
    if object_type == "knowledge":
        return _find_typed(root, discover_knowledge(root)[0], "knowledge", object_id)
    if object_type == "method":
        return _find_typed(root, discover_methods(root), "method", object_id)
    if object_type == "project":
        return _project_file(root, object_id)
    return _note_file(root, object_type, object_id)


def _find_typed(root: Path, paths: list[Path], expected_type: str, object_id: str):
    for path in paths:
        loaded = _read_source(path)
        if loaded is None:
            continue
        _path, text, raw = loaded
        if raw is None:
            continue
        data, issues = parse_yaml_mapping(raw)
        if issues or not data:
            continue
        if data.get("id") == object_id and data.get("type") == expected_type:
            return path, text, raw
    return None


def _project_file(root: Path, object_id: str):
    page = "research_dossier.md"
    name = object_id
    if object_id.endswith("/decisions"):
        name = object_id[: -len("/decisions")]
        page = "decisions.md"
    if "/" in name or "\\" in name or name == TEMPLATE_DIRNAME:
        return None
    path = (root / PROJECTS_DIRNAME / name / page).resolve()
    parent = (root / PROJECTS_DIRNAME / name).resolve()
    base = (root / PROJECTS_DIRNAME).resolve()
    try:
        path.relative_to(parent)
        parent.relative_to(base)
    except ValueError:
        return None
    if TEMPLATE_DIRNAME in path.parts or not path.is_file():
        return None
    return _read_source(path)


def _note_file(root: Path, object_type: str, object_id: str):
    allowed = NOTE_ROOTS[object_type]
    rel = object_id.replace("\\", "/").lstrip("/")
    if not rel.startswith(allowed + "/") and rel != allowed:
        return None
    path = (root / rel).resolve()
    try:
        path.relative_to((root / allowed).resolve())
        path.relative_to(root.resolve())
    except ValueError:
        return None
    if any(part in SKIP_DIR_NAMES for part in path.parts):
        return None
    if path.suffix.lower() != ".md" or not path.is_file():
        return None
    return _read_source(path)


def _read_source(path: Path | None):
    if path is None or not path.is_file():
        return None
    text = path.read_text(encoding="utf-8")
    raw, _body, issues = extract_front_matter(text)
    if issues:
        return None
    return path, text, raw
