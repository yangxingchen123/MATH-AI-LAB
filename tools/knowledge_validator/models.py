"""Internal data models for Knowledge Validator."""

from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field as dc_field
from datetime import date
from enum import Enum
from pathlib import Path
from typing import Any


class Severity(str, Enum):
    ERROR = "ERROR"
    WARNING = "WARNING"
    INFO = "INFO"


@dataclass(frozen=True)
class ValidationIssue:
    severity: Severity
    rule_id: str
    message: str
    file: str | None = None
    object_id: str | None = None
    field: str | None = None
    target_id: str | None = None
    details: dict[str, Any] = dc_field(default_factory=dict)

    def sort_key(self) -> tuple:
        sev_order = {
            Severity.ERROR: 0,
            Severity.WARNING: 1,
            Severity.INFO: 2,
        }
        return (
            sev_order[self.severity],
            self.file or "",
            self.object_id or "",
            self.rule_id,
            self.field or "",
            self.target_id or "",
            self.message,
        )


@dataclass
class ParseResult:
    path: Path
    relative_path: str
    has_front_matter: bool
    data: dict[str, Any] | None = None
    issues: list[ValidationIssue] = dc_field(default_factory=list)
    raw_yaml: str | None = None


@dataclass
class KnowledgeDocument:
    path: Path
    relative_path: str
    data: dict[str, Any]
    object_id: str | None = None
    status: str | None = None
    created: date | None = None
    updated: date | None = None
    aliases: list[str] | None = None
    domain: str | None = None
    prerequisites: list[str] | None = None
    related: list[str] | None = None
    parse_ok: bool = True


@dataclass
class ValidationSummary:
    markdown_files: int = 0
    knowledge_objects: int = 0
    excluded_files: int = 0
    skipped_files: int = 0
    errors: int = 0
    warnings: int = 0
    info: int = 0
    result: str = "PASS"


@dataclass
class ValidationResult:
    project_root: Path
    summary: ValidationSummary
    issues: list[ValidationIssue] = dc_field(default_factory=list)
    documents: list[KnowledgeDocument] = dc_field(default_factory=list)
    focus_relative_path: str | None = None

    def add_issue(self, issue: ValidationIssue) -> None:
        self.issues.append(issue)

    def finalize(self) -> None:
        self.issues.sort(key=lambda i: i.sort_key())
        self.summary.errors = sum(1 for i in self.issues if i.severity == Severity.ERROR)
        self.summary.warnings = sum(1 for i in self.issues if i.severity == Severity.WARNING)
        self.summary.info = sum(1 for i in self.issues if i.severity == Severity.INFO)
        self.summary.result = "FAIL" if self.summary.errors else "PASS"
