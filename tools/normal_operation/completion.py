"""Canonical coverage inspection (runtime-only, not Schema)."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from tools.problem_solution.slots import normalize_target, parse_canonical_slots
from tools.problem_solution.writer import find_problem_file
from tools.problem_validator.parser import extract_front_matter, parse_yaml_mapping


@dataclass
class CompletionInspection:
    problem_id: str
    problem_path: str
    required_targets: list[str] = field(default_factory=list)
    present_targets: list[str] = field(default_factory=list)
    missing_targets: list[str] = field(default_factory=list)
    duplicate_targets: list[str] = field(default_factory=list)
    complete: bool = False
    error: str | None = None


def required_targets_for_problem(problem_id: str, parts: list[str] | None) -> list[str]:
    if not parts:
        return [normalize_target(problem_id, None)]
    return [normalize_target(problem_id, p) for p in parts]


def _parts_from_data(data: dict) -> list[str] | None:
    parts = data.get("parts")
    if parts is None:
        return None
    if not isinstance(parts, list):
        return None
    return [str(p).strip() for p in parts if str(p).strip()]


def inspect_problem_completion(root: Path | str, problem_id: str) -> CompletionInspection:
    """Inspect canonical Solution coverage. Attempts are never evidence."""
    project_root = Path(root).resolve()
    path = find_problem_file(project_root, problem_id)
    if path is None:
        return CompletionInspection(
            problem_id=problem_id,
            problem_path="",
            error=f"Problem {problem_id} not found",
        )

    rel = path.resolve().relative_to(project_root).as_posix()
    text = path.read_text(encoding="utf-8")
    raw_yaml, body, _ = extract_front_matter(text)
    if raw_yaml is None:
        return CompletionInspection(
            problem_id=problem_id,
            problem_path=rel,
            error="missing YAML frontmatter",
        )
    data, issues = parse_yaml_mapping(raw_yaml)
    if issues or not data:
        return CompletionInspection(
            problem_id=problem_id,
            problem_path=rel,
            error="YAML parse failed",
        )

    parts = _parts_from_data(data)
    required = required_targets_for_problem(problem_id, parts)
    canonical = parse_canonical_slots(body)
    present_set = {slot.target for slot in canonical.slots}
    present = [t for t in required if t in present_set]
    duplicates = list(canonical.duplicate_targets)
    for target in required:
        count = sum(1 for s in canonical.slots if s.target == target)
        if count > 1 and target not in duplicates:
            duplicates.append(target)

    missing = [t for t in required if t not in present]
    return CompletionInspection(
        problem_id=problem_id,
        problem_path=rel,
        required_targets=required,
        present_targets=present,
        missing_targets=missing,
        duplicate_targets=duplicates,
        complete=len(missing) == 0 and len(duplicates) == 0 and len(required) > 0,
    )
