"""Atomic canonical Solution upsert with Problem validation."""

from __future__ import annotations

from pathlib import Path

from tools.problem_validator import validate_file
from tools.problem_validator.discovery import discover_markdown_files, relative_to_root
from tools.problem_validator.parser import extract_front_matter, parse_yaml_mapping
from tools.source_io.atomic import atomic_replace_text

from .models import SolutionUpsertResult, UpsertAction
from .slots import count_slots_for_target, parse_canonical_slots, upsert_body


def find_problem_file(project_root: Path, problem_id: str) -> Path | None:
    project_root = project_root.resolve()
    for path in discover_markdown_files(project_root)[0]:
        text = path.read_text(encoding="utf-8")
        raw_yaml, _, _ = extract_front_matter(text)
        if raw_yaml is None:
            continue
        data, issues = parse_yaml_mapping(raw_yaml)
        if issues or not data:
            continue
        if data.get("id") == problem_id and data.get("type") == "problem":
            return path
    return None


def _reassemble(raw_yaml: str, body: str) -> str:
    return f"---\n{raw_yaml.rstrip()}\n---\n{body}"


def upsert_canonical_solution(
    project_root: Path,
    *,
    problem_id: str,
    content: str,
    part: str | None = None,
) -> SolutionUpsertResult:
    project_root = project_root.resolve()
    path = find_problem_file(project_root, problem_id)
    if path is None:
        return SolutionUpsertResult(
            action=UpsertAction.NO_OP,
            target=problem_id if part is None else f"{problem_id}/{part}",
            problem_id=problem_id,
            problem_path="",
            written=False,
            error=f"Problem {problem_id} not found",
        )

    rel = relative_to_root(path, project_root)
    target = problem_id if part is None else f"{problem_id}/{part}"
    original_text = path.read_text(encoding="utf-8")
    raw_yaml, body, _ = extract_front_matter(original_text)
    if raw_yaml is None:
        return SolutionUpsertResult(
            action=UpsertAction.NO_OP,
            target=target,
            problem_id=problem_id,
            problem_path=rel,
            written=False,
            error="Problem file missing YAML frontmatter",
        )

    dup_before = count_slots_for_target(body, problem_id=problem_id, part=part)
    if dup_before > 1:
        return SolutionUpsertResult(
            action=UpsertAction.NO_OP,
            target=target,
            problem_id=problem_id,
            problem_path=rel,
            written=False,
            duplicate_slots=[target],
            error=f"duplicate solution slots for {target}",
        )

    try:
        new_body, action_str = upsert_body(
            body,
            problem_id=problem_id,
            part=part,
            content=content,
        )
    except ValueError as exc:
        return SolutionUpsertResult(
            action=UpsertAction.NO_OP,
            target=target,
            problem_id=problem_id,
            problem_path=rel,
            written=False,
            error=str(exc),
        )

    action = UpsertAction(action_str)
    if action == UpsertAction.NO_OP:
        return SolutionUpsertResult(
            action=action,
            target=target,
            problem_id=problem_id,
            problem_path=rel,
            written=False,
        )

    candidate_text = _reassemble(raw_yaml, new_body)
    dup_after = parse_canonical_slots(new_body).duplicate_targets
    if dup_after:
        return SolutionUpsertResult(
            action=UpsertAction.NO_OP,
            target=target,
            problem_id=problem_id,
            problem_path=rel,
            written=False,
            duplicate_slots=dup_after,
            error="candidate would create duplicate canonical slots",
        )

    original_text = path.read_text(encoding="utf-8")
    atomic_replace_text(path, candidate_text)
    try:
        result = validate_file(path, root=project_root)
        if result.summary.errors > 0:
            atomic_replace_text(path, original_text)
            return SolutionUpsertResult(
                action=UpsertAction.NO_OP,
                target=target,
                problem_id=problem_id,
                problem_path=rel,
                written=False,
                error="candidate Problem validation failed",
            )
    except Exception:
        atomic_replace_text(path, original_text)
        raise

    return SolutionUpsertResult(
        action=action,
        target=target,
        problem_id=problem_id,
        problem_path=rel,
        written=True,
    )
