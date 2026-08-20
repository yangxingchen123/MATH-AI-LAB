"""Internal data models for Problem Candidate Gate v0.1."""

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
class GateIssue:
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
    issues: list[GateIssue] = dc_field(default_factory=list)
    raw_yaml: str | None = None
    body: str = ""


@dataclass
class ProblemDocument:
    path: Path
    relative_path: str
    data: dict[str, Any]
    body: str = ""
    object_id: str | None = None
    status: str | None = None
    created: date | None = None
    updated: date | None = None
    parse_ok: bool = True


@dataclass
class GateSummary:
    markdown_files: int = 0
    problem_candidates: int = 0
    excluded_files: int = 0
    skipped_files: int = 0
    errors: int = 0
    warnings: int = 0
    info: int = 0
    result: str = "PASS"


@dataclass
class GateResult:
    project_root: Path
    summary: GateSummary
    issues: list[GateIssue] = dc_field(default_factory=list)
    documents: list[ProblemDocument] = dc_field(default_factory=list)
    focus_relative_path: str | None = None
    knowledge_dependency_ok: bool = True
    readiness: str | None = None
    manual_review_items: list[str] = dc_field(default_factory=list)

    def add_issue(self, issue: GateIssue) -> None:
        self.issues.append(issue)

    def finalize(self) -> None:
        self.issues.sort(key=lambda i: i.sort_key())
        self.summary.errors = sum(1 for i in self.issues if i.severity == Severity.ERROR)
        self.summary.warnings = sum(1 for i in self.issues if i.severity == Severity.WARNING)
        self.summary.info = sum(1 for i in self.issues if i.severity == Severity.INFO)
        self.summary.result = "FAIL" if self.summary.errors else "PASS"
        if self.summary.errors:
            self.readiness = "NOT_READY"
        elif self.summary.warnings:
            self.readiness = "READY_WITH_WARNINGS"
        else:
            self.readiness = "READY_FOR_FINAL_REVIEW"
