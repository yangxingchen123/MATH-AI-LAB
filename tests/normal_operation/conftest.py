"""Shared helpers for Normal Operation acceptance tests."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from tools.attempt_validator.discovery import discover_ledger_files
from tools.attempt_validator.ledger import load_ledger_file
from tools.knowledge_validator.discovery import discover_markdown_files as discover_knowledge_files
from tools.method_validator.discovery import discover_markdown_files as discover_method_files
from tools.problem_solution.slots import parse_canonical_slots, parse_legacy_part_slots
from tools.problem_validator.discovery import discover_markdown_files as discover_problem_files
from tools.problem_validator.parser import extract_front_matter, parse_yaml_mapping
from tools.workspace_indexer import check_index


@dataclass
class ProjectSnapshot:
    problem_ids: set[str]
    attempt_ids: set[str]
    knowledge_ids: set[str]
    method_ids: set[str]
    solution_targets: set[str]
    workspace_state: str


def _ids_from_discovered(paths: list[Path], id_key: str = "id") -> set[str]:
    out: set[str] = set()
    for path in paths:
        text = path.read_text(encoding="utf-8")
        raw, _, _ = extract_front_matter(text)
        if raw is None:
            continue
        data, issues = parse_yaml_mapping(raw)
        if issues or not data:
            continue
        val = data.get(id_key)
        if isinstance(val, str):
            out.add(val)
    return out


def snapshot_project(root: Path) -> ProjectSnapshot:
    root = root.resolve()
    problems = discover_problem_files(root)[0]
    problem_ids = _ids_from_discovered(problems)
    knowledge_ids = _ids_from_discovered(discover_knowledge_files(root)[0])
    method_dir = root / "12_方法库"
    if method_dir.is_dir():
        method_ids = _ids_from_discovered(discover_method_files(root))
    else:
        method_ids = set()

    attempt_ids: set[str] = set()
    for ledger in discover_ledger_files(root):
        loaded = load_ledger_file(ledger, root)
        for record in loaded.attempts:
            aid = record.get("id")
            if isinstance(aid, str):
                attempt_ids.add(aid)

    solution_targets: set[str] = set()
    for path in problems:
        text = path.read_text(encoding="utf-8")
        raw_yaml, body, _ = extract_front_matter(text)
        data, issues = parse_yaml_mapping(raw_yaml) if raw_yaml else (None, [])
        pid = data.get("id") if data and not issues else None
        for slot in parse_canonical_slots(body).slots:
            solution_targets.add(slot.target)
        if isinstance(pid, str):
            for slot in parse_legacy_part_slots(body, pid):
                solution_targets.add(slot.target)

    ws = check_index(root=root)
    return ProjectSnapshot(
        problem_ids=problem_ids,
        attempt_ids=attempt_ids,
        knowledge_ids=knowledge_ids,
        method_ids=method_ids,
        solution_targets=solution_targets,
        workspace_state=ws.result.value,
    )


def delta(before: ProjectSnapshot, after: ProjectSnapshot) -> dict[str, int]:
    return {
        "problems": len(after.problem_ids - before.problem_ids),
        "attempts": len(after.attempt_ids - before.attempt_ids),
        "knowledge": len(after.knowledge_ids - before.knowledge_ids),
        "methods": len(after.method_ids - before.method_ids),
        "solution_targets": len(after.solution_targets - before.solution_targets),
    }
