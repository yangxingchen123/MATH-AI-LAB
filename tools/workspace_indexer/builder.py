"""Build WorkspaceSnapshot from validated registries and filesystem."""

from __future__ import annotations

from pathlib import Path

from tools.attempt_validator.models import AttemptDocument, ValidationResult as AttemptValidationResult
from tools.derived_evidence.builder import (
    DerivedEvidenceBuildError,
    build_derived_evidence_from_validation_results,
)
from tools.derived_evidence.knowledge_projection import build_knowledge_associated_evidence
from tools.knowledge_relations import build_knowledge_relations
from tools.knowledge_validator.models import KnowledgeDocument, ValidationResult as KnowledgeValidationResult
from tools.method_validator.models import MethodDocument, ValidationResult as MethodValidationResult
from tools.problem_validator.models import ProblemDocument, ValidationResult as ProblemValidationResult

from .constants import ASSISTANCE_OMITTED_LABEL, IMAGE_EXTENSIONS, LATEX_DIR, OUTCOME_VALUES, OUTPUT_DIR, WORKFLOW_DIRS
from .models import (
    AttemptIndexRow,
    KnowledgeIndexRow,
    MethodIndexRow,
    OutputIndexRow,
    ProblemIndexRow,
    WorkspaceSnapshot,
)


def operational_workflow_from_path(relative_path: str) -> str:
    parts = relative_path.replace("\\", "/").split("/")
    if len(parts) >= 2 and parts[0] == "02_题目库" and parts[1] in WORKFLOW_DIRS:
        return parts[1]
    return "其他"


def _status_counts(items: list[str]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for status in sorted(set(items)):
        counts[status] = sum(1 for s in items if s == status)
    return counts


def _workflow_counts_from_problems(rows: list[ProblemIndexRow]) -> dict[str, int]:
    counts: dict[str, int] = {name: 0 for name in sorted(WORKFLOW_DIRS)}
    for row in rows:
        wf = row.operational_workflow
        counts[wf] = counts.get(wf, 0) + 1
    return {k: v for k, v in counts.items() if v > 0}


def _assistance_label(data: dict) -> str:
    if "assistance" not in data:
        return ASSISTANCE_OMITTED_LABEL
    return str(data["assistance"])


def _target_label(data: dict) -> str:
    if "part" not in data:
        return "whole"
    part = data["part"]
    if isinstance(part, str) and part.strip():
        return f"part {part.strip()}"
    return "whole"


def _attempt_rows(documents: list[AttemptDocument]) -> list[AttemptIndexRow]:
    rows: list[AttemptIndexRow] = []
    for doc in sorted(documents, key=lambda d: d.object_id or ""):
        if not doc.object_id:
            continue
        attempted_at = doc.data.get("attempted_at")
        rows.append(
            AttemptIndexRow(
                object_id=doc.object_id,
                problem_id=str(doc.data.get("problem") or ""),
                target=_target_label(doc.data),
                outcome=str(doc.data.get("outcome") or ""),
                assistance=_assistance_label(doc.data),
                attempted_at=str(attempted_at) if attempted_at is not None else "",
                source_path=doc.source_display,
            )
        )
    return rows


def _outcome_counts(rows: list[AttemptIndexRow]) -> dict[str, int]:
    counts = {name: 0 for name in OUTCOME_VALUES}
    for row in rows:
        if row.outcome in counts:
            counts[row.outcome] += 1
    return counts


def _assistance_counts(rows: list[AttemptIndexRow]) -> dict[str, int]:
    counts = {
        "independent": 0,
        "assisted": 0,
        ASSISTANCE_OMITTED_LABEL: 0,
    }
    for row in rows:
        if row.assistance in counts:
            counts[row.assistance] += 1
    return counts


def _problem_attempt_counts(rows: list[AttemptIndexRow]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for row in rows:
        counts[row.problem_id] = counts.get(row.problem_id, 0) + 1
    return counts


def _knowledge_rows(documents: list[KnowledgeDocument]) -> list[KnowledgeIndexRow]:
    rows: list[KnowledgeIndexRow] = []
    for doc in sorted(documents, key=lambda d: d.object_id or ""):
        if not doc.object_id:
            continue
        rows.append(
            KnowledgeIndexRow(
                object_id=doc.object_id,
                title=str(doc.data.get("title") or ""),
                status=str(doc.status or ""),
                domain=str(doc.domain or ""),
                source_path=doc.relative_path,
            )
        )
    return rows


def _problem_rows(
    documents: list[ProblemDocument],
    *,
    attempt_counts: dict[str, int],
) -> list[ProblemIndexRow]:
    rows: list[ProblemIndexRow] = []
    for doc in sorted(documents, key=lambda d: d.object_id or ""):
        if not doc.object_id:
            continue
        parts_val = doc.parts
        if isinstance(parts_val, list):
            parts_str = ", ".join(str(p) for p in parts_val)
        else:
            parts_str = ""
        pid = doc.object_id
        rows.append(
            ProblemIndexRow(
                object_id=pid,
                title=str(doc.data.get("title") or ""),
                yaml_status=str(doc.status or ""),
                operational_workflow=operational_workflow_from_path(doc.relative_path),
                parts=parts_str,
                attempt_count=attempt_counts.get(pid, 0),
                source_path=doc.relative_path,
            )
        )
    return rows


def _method_knowledge_label(data: dict) -> str:
    if "knowledge" not in data:
        return "—"
    knowledge = data["knowledge"]
    if isinstance(knowledge, list):
        return ", ".join(str(item) for item in knowledge)
    return str(knowledge)


def _method_rows(documents: list[MethodDocument]) -> list[MethodIndexRow]:
    rows: list[MethodIndexRow] = []
    for doc in sorted(documents, key=lambda d: d.object_id or ""):
        if not doc.object_id:
            continue
        rows.append(
            MethodIndexRow(
                object_id=doc.object_id,
                title=str(doc.data.get("title") or ""),
                status=str(doc.status or ""),
                knowledge=_method_knowledge_label(doc.data),
                source_path=doc.relative_path,
            )
        )
    return rows


def _scan_outputs(project_root: Path) -> tuple[list[OutputIndexRow], int, int]:
    base = project_root / OUTPUT_DIR
    rows: list[OutputIndexRow] = []
    pdf_count = 0
    image_count = 0
    if not base.is_dir():
        return rows, pdf_count, image_count

    for path in sorted(base.rglob("*")):
        if not path.is_file():
            continue
        rel = path.relative_to(project_root).as_posix()
        suffix = path.suffix.lower()
        if suffix == ".pdf":
            kind = "pdf"
            pdf_count += 1
        elif suffix in IMAGE_EXTENSIONS:
            kind = "image"
            image_count += 1
        else:
            kind = "other"
        rows.append(
            OutputIndexRow(
                relative_path=rel,
                kind=kind,
                filename=path.name,
            )
        )
    return rows, pdf_count, image_count


def _count_latex_projects(project_root: Path) -> int:
    base = project_root / LATEX_DIR
    if not base.is_dir():
        return 0
    count = 0
    for main_tex in sorted(base.rglob("main.tex")):
        rel = main_tex.relative_to(base).as_posix()
        if rel.startswith("模板/"):
            continue
        count += 1
    return count


def build_workspace_snapshot(
    project_root: Path,
    *,
    knowledge_result: KnowledgeValidationResult,
    problem_result: ProblemValidationResult,
    attempt_result: AttemptValidationResult,
    method_result: MethodValidationResult,
) -> WorkspaceSnapshot:
    knowledge_docs = [d for d in knowledge_result.documents if d.object_id]
    problem_docs = [d for d in problem_result.documents if d.object_id]
    attempt_docs = [d for d in attempt_result.documents if d.object_id]
    method_docs = [d for d in method_result.documents if d.object_id]

    attempt_rows = _attempt_rows(attempt_docs)
    attempt_counts = _problem_attempt_counts(attempt_rows)
    knowledge_rows = _knowledge_rows(knowledge_docs)
    problem_rows = _problem_rows(problem_docs, attempt_counts=attempt_counts)
    method_rows = _method_rows(method_docs)
    output_rows, pdf_count, image_count = _scan_outputs(project_root)

    try:
        derived_evidence = build_derived_evidence_from_validation_results(
            problem_result,
            attempt_result,
        )
    except DerivedEvidenceBuildError as exc:
        raise DerivedEvidenceBuildError(str(exc)) from exc

    knowledge_registry = {d.object_id: d for d in knowledge_docs if d.object_id}
    problem_registry = {d.object_id: d for d in problem_docs if d.object_id}
    attempt_registry = dict(attempt_result.registry) if attempt_result.registry else {
        d.object_id: d for d in attempt_docs if d.object_id
    }

    try:
        knowledge_associated_evidence = build_knowledge_associated_evidence(
            knowledge_registry,
            problem_registry,
            attempt_registry,
            derived_evidence,
        )
    except DerivedEvidenceBuildError as exc:
        raise DerivedEvidenceBuildError(str(exc)) from exc

    knowledge_relations = build_knowledge_relations(
        knowledge_registry,
        problem_registry,
        {d.object_id: d for d in method_docs if d.object_id},
    )

    return WorkspaceSnapshot(
        project_root=project_root,
        knowledge_rows=knowledge_rows,
        problem_rows=problem_rows,
        attempt_rows=attempt_rows,
        method_rows=method_rows,
        output_rows=output_rows,
        knowledge_status_counts=_status_counts([r.status for r in knowledge_rows]),
        problem_yaml_status_counts=_status_counts([r.yaml_status for r in problem_rows]),
        problem_workflow_counts=_workflow_counts_from_problems(problem_rows),
        problem_attempt_counts=attempt_counts,
        attempt_outcome_counts=_outcome_counts(attempt_rows),
        attempt_assistance_counts=_assistance_counts(attempt_rows),
        method_status_counts=_status_counts([r.status for r in method_rows]),
        latex_project_count=_count_latex_projects(project_root),
        pdf_count=pdf_count,
        image_count=image_count,
        derived_evidence=derived_evidence,
        knowledge_associated_evidence=knowledge_associated_evidence,
        knowledge_relations=knowledge_relations,
    )
