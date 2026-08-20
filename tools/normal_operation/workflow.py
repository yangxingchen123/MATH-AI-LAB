"""Filesystem workflow moves for formal Problems (directory only; YAML status untouched)."""

from __future__ import annotations

import shutil
from dataclasses import dataclass
from pathlib import Path

from tools.problem_solution.writer import find_problem_file
from tools.workspace_indexer.constants import WORKFLOW_DIRS


@dataclass
class WorkflowMoveResult:
    moved: bool
    from_path: str
    to_path: str
    workflow_before: str
    workflow_after: str
    error: str | None = None


def workflow_from_relative(relative_path: str) -> str:
    parts = relative_path.replace("\\", "/").split("/")
    if len(parts) >= 2 and parts[0] == "02_题目库" and parts[1] in WORKFLOW_DIRS:
        return parts[1]
    return "其他"


def move_problem_to_workflow(
    root: Path | str,
    problem_id: str,
    *,
    target_workflow: str,
) -> WorkflowMoveResult:
    """Move Problem Markdown into 02_题目库/<target_workflow>/."""
    project_root = Path(root).resolve()
    if target_workflow not in WORKFLOW_DIRS:
        return WorkflowMoveResult(
            moved=False,
            from_path="",
            to_path="",
            workflow_before="",
            workflow_after="",
            error=f"invalid workflow {target_workflow!r}",
        )

    path = find_problem_file(project_root, problem_id)
    if path is None:
        return WorkflowMoveResult(
            moved=False,
            from_path="",
            to_path="",
            workflow_before="",
            workflow_after="",
            error=f"Problem {problem_id} not found",
        )

    rel = path.resolve().relative_to(project_root).as_posix()
    before = workflow_from_relative(rel)
    if before == target_workflow:
        return WorkflowMoveResult(
            moved=False,
            from_path=rel,
            to_path=rel,
            workflow_before=before,
            workflow_after=before,
        )

    dest_dir = project_root / "02_题目库" / target_workflow
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / path.name
    if dest.exists():
        return WorkflowMoveResult(
            moved=False,
            from_path=rel,
            to_path=dest.relative_to(project_root).as_posix(),
            workflow_before=before,
            workflow_after=before,
            error=f"destination collision: {dest.name}",
        )

    shutil.move(str(path), str(dest))
    new_rel = dest.resolve().relative_to(project_root).as_posix()
    return WorkflowMoveResult(
        moved=True,
        from_path=rel,
        to_path=new_rel,
        workflow_before=before,
        workflow_after=target_workflow,
    )
