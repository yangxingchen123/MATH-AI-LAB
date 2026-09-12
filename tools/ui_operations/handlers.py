"""Domain operations: thin wrappers over existing Layer 2 / validators."""

from __future__ import annotations

import re
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from tools.attempt_validator.ledger import allocate_next_attempt_id
from tools.knowledge_validator import validate_project as validate_knowledge_project
from tools.method_validator import validate_project as validate_method_project
from tools.normal_operation.operations import record_user_attempt_op
from tools.normal_operation.workflow import move_problem_to_workflow, workflow_from_relative
from tools.problem_solution.writer import find_problem_file
from tools.problem_validator import validate_project as validate_problem_project
from tools.problem_validator.constants import ID_PATTERN as P_PATTERN
from tools.knowledge_validator.constants import ID_PATTERN as K_PATTERN
from tools.method_validator.constants import ID_PATTERN as M_PATTERN
from tools.source_io.atomic import atomic_replace_text
from tools.workspace_indexer.constants import WORKFLOW_DIRS

from .constants import ASSISTANCE, OUTCOMES, PROMOTE_TYPES
from .documents import EDITABLE_TYPES, FROZEN_TYPES, locate, reassemble
from .ids import allocate_knowledge_id, allocate_method_id, allocate_problem_id
from .models import OperationResult, ValidationItem, fail
from .render import render_knowledge, render_method, render_problem

TZ_EAST = timezone(timedelta(hours=8))
FORBIDDEN_PAYLOAD = frozenset({"root", "path", "file", "command", "cwd", "shell"})
ID_RE = {
    "problem": re.compile(P_PATTERN),
    "knowledge": re.compile(K_PATTERN),
    "method": re.compile(M_PATTERN),
}


def now_attempted_at() -> str:
    now = datetime.now(TZ_EAST)
    offset = now.strftime("%z")
    return f"{now.strftime('%Y-%m-%dT%H:%M')}{offset[:3]}:{offset[3:]}"


def _as_str_list(value: Any) -> list[str] | None:
    if value is None or value == "":
        return None
    if not isinstance(value, list):
        return None
    out: list[str] = []
    for item in value:
        if not isinstance(item, str) or not item.strip():
            return None
        out.append(item.strip())
    return out or None


def _issues_from_summary(validator: str, result: Any) -> tuple[str, list[ValidationItem]]:
    items: list[ValidationItem] = []
    errors = getattr(getattr(result, "summary", None), "errors", 0) or 0
    warnings = getattr(getattr(result, "summary", None), "warnings", 0) or 0
    for issue in getattr(result, "issues", []) or []:
        level = getattr(getattr(issue, "severity", None), "value", None) or str(
            getattr(issue, "severity", "ERROR")
        )
        items.append(
            ValidationItem(
                level=str(level).upper(),
                validator=validator,
                message=getattr(issue, "message", str(issue)),
                source_path=getattr(issue, "file", None),
            )
        )
    if errors:
        status = "FAIL"
    elif warnings:
        status = "WARNING"
    else:
        status = "PASS"
    return status, items


def _reject_payload(payload: dict[str, Any], request_id: str, operation: str, preview: bool):
    if any(key in FORBIDDEN_PAYLOAD for key in payload):
        return fail(
            operation,
            request_id,
            preview=preview,
            error="payload must not include filesystem or shell fields",
        )
    return None


def _title_body(payload: dict[str, Any]) -> tuple[str | None, str]:
    title = payload.get("title")
    body = payload.get("body")
    if not isinstance(title, str) or not title.strip():
        return None, ""
    if body is None:
        body = ""
    if not isinstance(body, str):
        return None, ""
    return title.strip(), body


def record_attempt(root: Path, payload: dict[str, Any], *, preview: bool, request_id: str) -> OperationResult:
    blocked = _reject_payload(payload, request_id, "RecordAttempt", preview)
    if blocked:
        return blocked
    problem_id = payload.get("problemId") or payload.get("problem_id")
    narrative = payload.get("narrative")
    outcome = payload.get("outcome")
    part = payload.get("part")
    assistance = payload.get("assistance") or "independent"
    if not isinstance(problem_id, str) or not ID_RE["problem"].fullmatch(problem_id):
        return fail("RecordAttempt", request_id, preview=preview, error="invalid problemId")
    if not isinstance(narrative, str) or not narrative.strip():
        return fail("RecordAttempt", request_id, preview=preview, error="narrative is required")
    if outcome not in OUTCOMES:
        return fail("RecordAttempt", request_id, preview=preview, error="invalid outcome")
    if assistance not in ASSISTANCE:
        return fail("RecordAttempt", request_id, preview=preview, error="invalid assistance")
    if part is not None and (not isinstance(part, str) or not part.strip()):
        return fail("RecordAttempt", request_id, preview=preview, error="invalid part")
    if find_problem_file(root, problem_id) is None:
        return fail("RecordAttempt", request_id, preview=preview, error=f"Problem {problem_id} not found")

    attempt_id = allocate_next_attempt_id(root)
    record = {
        "schema_version": 1,
        "id": attempt_id,
        "type": "attempt",
        "problem": problem_id,
        "outcome": outcome,
        "assistance": assistance,
        "attempted_at": now_attempted_at(),
    }
    if isinstance(part, str) and part.strip():
        record["part"] = part.strip()

    planned = {
        "problem": problem_id,
        "attempt": attempt_id,
        "ledger": f"11_学习证据/尝试记录/{problem_id}.md",
        "outcome": outcome,
        "part": record.get("part"),
        "assistance": assistance,
    }
    if preview:
        return OperationResult(
            version=1,
            success=True,
            operation="RecordAttempt",
            preview=True,
            request_id=request_id,
            affected_objects=[problem_id, attempt_id],
            validation="NOT_RUN",
            planned=planned,
            changed_files=[],
            warnings=["Preview only. Confirm to append the Attempt ledger."],
        )

    result = record_user_attempt_op(
        root,
        problem_id=problem_id,
        record=record,
        narrative=narrative.strip(),
        include_verification=False,
    )
    if result.attempt.value != "CREATED":
        return fail(
            "RecordAttempt",
            request_id,
            preview=False,
            error=result.error or "record_user_attempt_op failed",
        )
    warnings: list[str] = []
    validation = "PASS"
    if result.finalize and getattr(result.finalize, "validation_errors", 0):
        validation = "WARNING"
        warnings.append("Attempt written; post-write finalize reported validator issues.")
    return OperationResult(
        version=1,
        success=True,
        operation="RecordAttempt",
        preview=False,
        request_id=request_id,
        affected_objects=[problem_id, attempt_id],
        validation=validation,
        planned=planned,
        changed_files=[result.attempt_ledger_path or planned["ledger"]],
        warnings=warnings,
    )


def move_workflow(root: Path, payload: dict[str, Any], *, preview: bool, request_id: str) -> OperationResult:
    blocked = _reject_payload(payload, request_id, "MoveProblemWorkflow", preview)
    if blocked:
        return blocked
    problem_id = payload.get("problemId") or payload.get("problem_id")
    target = payload.get("targetWorkflow") or payload.get("target_workflow")
    if not isinstance(problem_id, str) or not ID_RE["problem"].fullmatch(problem_id):
        return fail("MoveProblemWorkflow", request_id, preview=preview, error="invalid problemId")
    if target not in WORKFLOW_DIRS:
        return fail(
            "MoveProblemWorkflow",
            request_id,
            preview=preview,
            error="targetWorkflow must be 未解决 / 研究中 / 已解决",
        )
    path = find_problem_file(root, problem_id)
    if path is None:
        return fail("MoveProblemWorkflow", request_id, preview=preview, error=f"Problem {problem_id} not found")
    rel = path.resolve().relative_to(root).as_posix()
    before = workflow_from_relative(rel)
    dest = f"02_题目库/{target}/{path.name}"
    planned = {
        "problem": problem_id,
        "workflowDir": {"current": before, "target": target},
        "note": "This moves the Markdown file. YAML objectStatus is unchanged.",
        "from": rel,
        "to": dest,
    }
    if preview:
        changed = [] if before == target else [f"moved {rel} → {dest}"]
        return OperationResult(
            version=1,
            success=True,
            operation="MoveProblemWorkflow",
            preview=True,
            request_id=request_id,
            affected_objects=[problem_id],
            validation="NOT_RUN",
            planned=planned,
            changed_files=changed,
            warnings=[] if before != target else ["Already in the target workflow directory."],
        )

    moved = move_problem_to_workflow(root, problem_id, target_workflow=target)
    if moved.error:
        return fail("MoveProblemWorkflow", request_id, preview=False, error=moved.error)
    changed = []
    if moved.moved:
        changed = [f"moved {moved.from_path} → {moved.to_path}"]
    return OperationResult(
        version=1,
        success=True,
        operation="MoveProblemWorkflow",
        preview=False,
        request_id=request_id,
        affected_objects=[problem_id],
        validation="PASS",
        planned={**planned, "from": moved.from_path, "to": moved.to_path},
        changed_files=changed,
        warnings=[] if moved.moved else ["Already in the target workflow directory."],
    )


def _create_source(
    *,
    root: Path,
    dest: Path,
    text: str,
    validate,
    operation: str,
    object_id: str,
    preview: bool,
    request_id: str,
    planned: dict[str, Any],
) -> OperationResult:
    rel = dest.relative_to(root).as_posix()
    planned = {**planned, "destination": rel, "filesToCreate": [rel]}
    if dest.exists():
        return fail(operation, request_id, preview=preview, error=f"destination exists: {rel}")

    dest.parent.mkdir(parents=True, exist_ok=True)
    created = False
    try:
        atomic_replace_text(dest, text)
        created = True
        result = validate()
        status, issues = _issues_from_summary(operation, result)
        if status == "FAIL" or preview:
            if created:
                dest.unlink(missing_ok=True)
            if preview:
                return OperationResult(
                    version=1,
                    success=status != "FAIL",
                    operation=operation,
                    preview=True,
                    request_id=request_id,
                    affected_objects=[object_id],
                    validation=status,
                    planned=planned,
                    changed_files=[],
                    issues=issues,
                    error=None if status != "FAIL" else "preview validation failed",
                    warnings=["Preview only. Confirm to persist."] if status != "FAIL" else [],
                )
            return OperationResult(
                version=1,
                success=False,
                operation=operation,
                preview=False,
                request_id=request_id,
                affected_objects=[object_id],
                validation="FAIL",
                planned=planned,
                issues=issues,
                error="validator rejected the candidate; file was not kept",
            )
        return OperationResult(
            version=1,
            success=True,
            operation=operation,
            preview=False,
            request_id=request_id,
            affected_objects=[object_id],
            validation=status,
            planned=planned,
            changed_files=[rel],
            issues=issues,
        )
    except Exception:
        if created:
            dest.unlink(missing_ok=True)
        raise


def create_problem(root: Path, payload: dict[str, Any], *, preview: bool, request_id: str) -> OperationResult:
    blocked = _reject_payload(payload, request_id, "CreateProblem", preview)
    if blocked:
        return blocked
    title, body = _title_body(payload)
    if title is None:
        return fail("CreateProblem", request_id, preview=preview, error="title and body are required")
    parts = _as_str_list(payload.get("parts"))
    if payload.get("parts") not in (None, [], "") and parts is None:
        return fail("CreateProblem", request_id, preview=preview, error="parts must be a string list")
    knowledge = _as_str_list(payload.get("knowledge"))
    if payload.get("knowledge") not in (None, [], "") and knowledge is None:
        return fail("CreateProblem", request_id, preview=preview, error="knowledge must be a string list")
    object_id = allocate_problem_id(root)
    text = render_problem(
        object_id=object_id,
        title=title,
        body=body,
        parts=parts,
        knowledge=knowledge,
    )
    dest = root / "02_题目库" / "未解决" / f"{object_id}.md"
    return _create_source(
        root=root,
        dest=dest,
        text=text,
        validate=lambda: validate_problem_project(root=root),
        operation="CreateProblem",
        object_id=object_id,
        preview=preview,
        request_id=request_id,
        planned={
            "id": object_id,
            "title": title,
            "workflowDir": "未解决",
            "objectStatus": "draft",
        },
    )


def create_knowledge(root: Path, payload: dict[str, Any], *, preview: bool, request_id: str) -> OperationResult:
    blocked = _reject_payload(payload, request_id, "CreateKnowledge", preview)
    if blocked:
        return blocked
    title, body = _title_body(payload)
    if title is None:
        return fail("CreateKnowledge", request_id, preview=preview, error="title and body are required")
    domain = payload.get("domain")
    if domain is not None and not isinstance(domain, str):
        return fail("CreateKnowledge", request_id, preview=preview, error="domain must be a string")
    aliases = _as_str_list(payload.get("aliases"))
    if payload.get("aliases") not in (None, [], "") and aliases is None:
        return fail("CreateKnowledge", request_id, preview=preview, error="aliases must be a string list")
    object_id = allocate_knowledge_id(root)
    text = render_knowledge(
        object_id=object_id,
        title=title,
        body=body,
        domain=domain.strip() if isinstance(domain, str) and domain.strip() else None,
        aliases=aliases,
    )
    dest = root / "01_知识库" / f"{object_id}.md"
    return _create_source(
        root=root,
        dest=dest,
        text=text,
        validate=lambda: validate_knowledge_project(root=root),
        operation="CreateKnowledge",
        object_id=object_id,
        preview=preview,
        request_id=request_id,
        planned={"id": object_id, "title": title, "objectStatus": "draft"},
    )


def create_method(root: Path, payload: dict[str, Any], *, preview: bool, request_id: str) -> OperationResult:
    blocked = _reject_payload(payload, request_id, "CreateMethod", preview)
    if blocked:
        return blocked
    title, body = _title_body(payload)
    if title is None:
        return fail("CreateMethod", request_id, preview=preview, error="title and body are required")
    knowledge = _as_str_list(payload.get("knowledge"))
    if payload.get("knowledge") not in (None, [], "") and knowledge is None:
        return fail("CreateMethod", request_id, preview=preview, error="knowledge must be a string list")
    object_id = allocate_method_id(root)
    text = render_method(object_id=object_id, title=title, body=body, knowledge=knowledge)
    dest = root / "12_方法库" / f"{object_id}.md"
    return _create_source(
        root=root,
        dest=dest,
        text=text,
        validate=lambda: validate_method_project(root=root),
        operation="CreateMethod",
        object_id=object_id,
        preview=preview,
        request_id=request_id,
        planned={"id": object_id, "title": title, "objectStatus": "draft"},
    )


def _inbox_path(root: Path, inbox_id: str) -> Path | None:
    if not inbox_id or inbox_id != Path(inbox_id).name:
        return None
    if inbox_id in {".", ".."} or inbox_id.startswith("."):
        return None
    if "/" in inbox_id or "\\" in inbox_id:
        return None
    if inbox_id.lower() == "readme.md":
        return None
    inbox_dir = (root / "00_收件箱").resolve()
    path = (inbox_dir / inbox_id).resolve()
    try:
        path.relative_to(inbox_dir)
    except ValueError:
        return None
    if not path.is_file():
        return None
    return path


def promote_inbox(root: Path, payload: dict[str, Any], *, preview: bool, request_id: str) -> OperationResult:
    blocked = _reject_payload(payload, request_id, "PromoteInboxItem", preview)
    if blocked:
        return blocked
    inbox_id = payload.get("inboxId") or payload.get("inbox_id")
    target = payload.get("targetType") or payload.get("target_type")
    if not isinstance(inbox_id, str):
        return fail("PromoteInboxItem", request_id, preview=preview, error="inboxId is required")
    if target not in PROMOTE_TYPES:
        return fail(
            "PromoteInboxItem",
            request_id,
            preview=preview,
            error="targetType must be problem, knowledge, or method",
        )
    path = _inbox_path(root, inbox_id)
    if path is None:
        return fail("PromoteInboxItem", request_id, preview=preview, error="inbox item not found or not promotable")
    raw = path.read_text(encoding="utf-8")
    title = payload.get("title")
    body = payload.get("body")
    if not isinstance(title, str) or not title.strip():
        title = path.stem
    if not isinstance(body, str) or not body.strip():
        body = raw
    create_payload = {
        "title": title.strip(),
        "body": body,
        "parts": payload.get("parts"),
        "knowledge": payload.get("knowledge"),
        "domain": payload.get("domain"),
        "aliases": payload.get("aliases"),
    }
    if target == "problem":
        created = create_problem(root, create_payload, preview=preview, request_id=request_id)
    elif target == "knowledge":
        created = create_knowledge(root, create_payload, preview=preview, request_id=request_id)
    else:
        created = create_method(root, create_payload, preview=preview, request_id=request_id)
    created.operation = "PromoteInboxItem"
    created.planned = {
        **created.planned,
        "inboxId": inbox_id,
        "targetType": target,
        "inboxDisposition": "left in place",
    }
    created.warnings = list(created.warnings) + [
        "Inbox source was not moved or deleted. Existing inbox lifecycle has no promote-archive operation."
    ]
    return created


def update_markdown_body(root: Path, payload: dict[str, Any], *, preview: bool, request_id: str) -> OperationResult:
    blocked = _reject_payload(payload, request_id, "UpdateMarkdownBody", preview)
    if blocked:
        return blocked
    object_type = payload.get("objectType") or payload.get("object_type")
    object_id = payload.get("objectId") or payload.get("object_id")
    body = payload.get("body")
    if object_type not in EDITABLE_TYPES:
        return fail("UpdateMarkdownBody", request_id, preview=preview, error="objectType is not editable")
    if not isinstance(object_id, str) or not object_id.strip():
        return fail("UpdateMarkdownBody", request_id, preview=preview, error="objectId is required")
    if not isinstance(body, str):
        return fail("UpdateMarkdownBody", request_id, preview=preview, error="body must be a string")
    found = locate(root, str(object_type), object_id.strip())
    if found is None:
        return fail("UpdateMarkdownBody", request_id, preview=preview, error="document not found or not allowlisted")
    path, original, raw_yaml = found
    if object_type in FROZEN_TYPES and raw_yaml is None:
        return fail("UpdateMarkdownBody", request_id, preview=preview, error="Frozen object is missing YAML Front Matter")
    new_text = reassemble(raw_yaml, body) if raw_yaml is not None else _plain_markdown(body)
    rel = path.resolve().relative_to(root.resolve()).as_posix()
    planned = {
        "objectType": object_type,
        "objectId": object_id.strip(),
        "destination": rel,
        "yamlUnchanged": raw_yaml is not None,
        "note": "Only Markdown body is updated. YAML Front Matter is preserved.",
    }
    if new_text == original:
        return OperationResult(
            version=1,
            success=True,
            operation="UpdateMarkdownBody",
            preview=preview,
            request_id=request_id,
            affected_objects=[object_id.strip()],
            validation="NOT_RUN",
            planned=planned,
            changed_files=[],
            warnings=["No textual change."],
        )
    validators = {
        "problem": validate_problem_project,
        "knowledge": validate_knowledge_project,
        "method": validate_method_project,
    }
    if preview or object_type in FROZEN_TYPES:
        atomic_replace_text(path, new_text)
        restored = False
        try:
            if object_type in validators:
                result = validators[object_type](root=root)
                status, issues = _issues_from_summary("UpdateMarkdownBody", result)
            else:
                status, issues = "PASS", []
            if preview or status == "FAIL":
                atomic_replace_text(path, original)
                restored = True
            if preview:
                return OperationResult(
                    version=1,
                    success=status != "FAIL",
                    operation="UpdateMarkdownBody",
                    preview=True,
                    request_id=request_id,
                    affected_objects=[object_id.strip()],
                    validation=status,
                    planned=planned,
                    changed_files=[],
                    issues=issues,
                    error=None if status != "FAIL" else "preview validation failed",
                    warnings=["Preview only. Confirm to persist."] if status != "FAIL" else [],
                )
            if status == "FAIL":
                return OperationResult(
                    version=1,
                    success=False,
                    operation="UpdateMarkdownBody",
                    preview=False,
                    request_id=request_id,
                    affected_objects=[object_id.strip()],
                    validation="FAIL",
                    planned=planned,
                    issues=issues,
                    error="validator rejected the body; original file was restored",
                )
            return OperationResult(
                version=1,
                success=True,
                operation="UpdateMarkdownBody",
                preview=False,
                request_id=request_id,
                affected_objects=[object_id.strip()],
                validation=status,
                planned=planned,
                changed_files=[rel],
                issues=issues,
            )
        except Exception:
            if not restored:
                atomic_replace_text(path, original)
            raise
    atomic_replace_text(path, new_text)
    return OperationResult(
        version=1,
        success=True,
        operation="UpdateMarkdownBody",
        preview=False,
        request_id=request_id,
        affected_objects=[object_id.strip()],
        validation="PASS",
        planned=planned,
        changed_files=[rel],
    )


def _plain_markdown(body: str) -> str:
    text = body.replace("\r\n", "\n")
    if text and not text.endswith("\n"):
        text += "\n"
    return text
