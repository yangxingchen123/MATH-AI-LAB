"""Dispatch a versioned OperationRequest. Root is never taken from the payload."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

from .constants import CONTRACT_VERSION, OPERATIONS
from .handlers import (
    create_knowledge,
    create_method,
    create_problem,
    move_workflow,
    promote_inbox,
    record_attempt,
    update_markdown_body,
)
from .models import OperationResult, fail

Handler = Callable[..., OperationResult]

HANDLERS: dict[str, Handler] = {
    "RecordAttempt": record_attempt,
    "MoveProblemWorkflow": move_workflow,
    "CreateProblem": create_problem,
    "CreateKnowledge": create_knowledge,
    "CreateMethod": create_method,
    "PromoteInboxItem": promote_inbox,
    "UpdateMarkdownBody": update_markdown_body,
}


def doctor() -> dict[str, Any]:
    return {
        "version": CONTRACT_VERSION,
        "writes": True,
        "operations": sorted(OPERATIONS),
    }


def run_operation(root: Path | str, request: dict[str, Any]) -> OperationResult:
    project_root = Path(root).resolve()
    request_id = str(request.get("requestId") or request.get("request_id") or "")
    operation = request.get("operation")
    preview = bool(request.get("preview"))
    version = request.get("version", CONTRACT_VERSION)
    payload = request.get("payload")

    if version != CONTRACT_VERSION:
        return fail(
            str(operation or "Unknown"),
            request_id,
            preview=preview,
            error=f"unsupported contract version {version!r}",
        )
    if operation not in OPERATIONS:
        return fail(
            str(operation or "Unknown"),
            request_id,
            preview=preview,
            error="operation is not on the whitelist",
        )
    if payload is None:
        payload = {}
    if not isinstance(payload, dict):
        return fail(str(operation), request_id, preview=preview, error="payload must be an object")
    if "root" in request or "cwd" in request:
        return fail(str(operation), request_id, preview=preview, error="request must not set root")

    handler = HANDLERS[str(operation)]
    return handler(project_root, payload, preview=preview, request_id=request_id)
