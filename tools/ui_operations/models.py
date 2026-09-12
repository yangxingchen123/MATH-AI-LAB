"""Structured OperationRequest / OperationResult. Not a Source Schema."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class ValidationItem:
    level: str
    validator: str
    message: str
    source_path: str | None = None


@dataclass
class OperationResult:
    version: int
    success: bool
    operation: str
    preview: bool
    request_id: str
    affected_objects: list[str] = field(default_factory=list)
    validation: str = "NOT_RUN"
    warnings: list[str] = field(default_factory=list)
    changed_files: list[str] = field(default_factory=list)
    created_artifacts: list[str] = field(default_factory=list)
    planned: dict[str, Any] = field(default_factory=dict)
    issues: list[ValidationItem] = field(default_factory=list)
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["issues"] = [asdict(item) for item in self.issues]
        return data


def fail(
    operation: str,
    request_id: str,
    *,
    preview: bool,
    error: str,
    validation: str = "FAIL",
    issues: list[ValidationItem] | None = None,
) -> OperationResult:
    return OperationResult(
        version=1,
        success=False,
        operation=operation,
        preview=preview,
        request_id=request_id,
        validation=validation,
        error=error,
        issues=issues or [],
    )
