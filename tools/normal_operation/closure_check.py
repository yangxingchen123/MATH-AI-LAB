"""Read-only closure drift checker (not wired into verification core yet)."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from tools.problem_validator import validate_project
from tools.problem_solution.writer import find_problem_file

from .artifact import FreshnessState, inspect_artifact
from .completion import inspect_problem_completion
from .workflow import workflow_from_relative


@dataclass
class DriftItem:
    problem_id: str
    problem_path: str
    category: str
    suggested_action: str


@dataclass
class DriftScanResult:
    items: list[DriftItem] = field(default_factory=list)
    total_problems: int = 0

    @property
    def errors(self) -> list[DriftItem]:
        error_cats = {
            "COMPLETE_UNCLOSED",
            "CLOSED_ARTIFACT_MISSING",
            "CLOSED_ARTIFACT_STALE",
            "DUPLICATE_CANONICAL",
        }
        return [i for i in self.items if i.category in error_cats]

    @property
    def warnings(self) -> list[DriftItem]:
        warn_cats = {"CLOSED_INCOMPLETE", "INCOMPLETE"}
        return [i for i in self.items if i.category in warn_cats]


def scan_closure_drift(root: Path | str) -> DriftScanResult:
    project_root = Path(root).resolve()
    pv = validate_project(root=project_root)
    result = DriftScanResult(total_problems=len(pv.documents))
    for doc in pv.documents:
        pid = doc.id
        if not pid:
            continue
        path = str(Path(doc.path).resolve().relative_to(project_root).as_posix())
        wf = workflow_from_relative(doc.relative_path)
        completion = inspect_problem_completion(project_root, pid)
        if completion.duplicate_targets:
            result.items.append(
                DriftItem(
                    problem_id=pid,
                    problem_path=path,
                    category="DUPLICATE_CANONICAL",
                    suggested_action="remove duplicate canonical slots",
                )
            )
        if wf == "研究中" and completion.complete:
            result.items.append(
                DriftItem(
                    problem_id=pid,
                    problem_path=path,
                    category="COMPLETE_UNCLOSED",
                    suggested_action="reconcile_problem (auto archive + artifact)",
                )
            )
        if wf == "已解决" and not completion.complete:
            result.items.append(
                DriftItem(
                    problem_id=pid,
                    problem_path=path,
                    category="CLOSED_INCOMPLETE",
                    suggested_action="restore to 研究中 only if user authorizes; else fill missing targets",
                )
            )
        if wf == "已解决" and completion.complete:
            art = inspect_artifact(project_root, problem_id=pid)
            if art.latex == FreshnessState.MISSING or art.pdf == FreshnessState.MISSING:
                result.items.append(
                    DriftItem(
                        problem_id=pid,
                        problem_path=path,
                        category="CLOSED_ARTIFACT_MISSING",
                        suggested_action="reconcile_problem (materialize/build)",
                    )
                )
            elif art.latex == FreshnessState.STALE or art.pdf == FreshnessState.STALE:
                result.items.append(
                    DriftItem(
                        problem_id=pid,
                        problem_path=path,
                        category="CLOSED_ARTIFACT_STALE",
                        suggested_action="reconcile_problem (regenerate/build)",
                    )
                )
        if not completion.complete and wf != "已解决":
            result.items.append(
                DriftItem(
                    problem_id=pid,
                    problem_path=path,
                    category="INCOMPLETE",
                    suggested_action=f"AI fill missing: {completion.missing_targets}",
                )
            )
    return result
