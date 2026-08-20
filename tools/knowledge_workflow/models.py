"""Workflow result models."""

from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field as dc_field
from typing import Any


@dataclass
class WorkflowIssue:
    source: str
    severity: str
    rule_id: str
    message: str
    file: str | None = None
    object_id: str | None = None
    field: str | None = None
    target_id: str | None = None
    details: dict[str, Any] = dc_field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "source": self.source,
            "severity": self.severity,
            "rule_id": self.rule_id,
            "message": self.message,
            "file": self.file,
            "object_id": self.object_id,
            "field": self.field,
            "target_id": self.target_id,
        }
        if self.details:
            payload["details"] = self.details
        return payload


@dataclass
class WorkflowStageResult:
    name: str
    status: str
    errors: int = 0
    warnings: int = 0
    detail: str | None = None
    issues: list[WorkflowIssue] = dc_field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "status": self.status,
            "errors": self.errors,
            "warnings": self.warnings,
            "issues": [i.to_dict() for i in self.issues],
        }
        if self.detail is not None:
            payload["detail"] = self.detail
        return payload


@dataclass
class WorkflowResult:
    result: str
    project_root: str
    target: str | None
    strict_warnings: bool
    stages: dict[str, WorkflowStageResult] = dc_field(default_factory=dict)
    command: str = ""
