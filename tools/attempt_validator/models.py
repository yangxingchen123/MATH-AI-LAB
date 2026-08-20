"""Data models for Attempt Validator v1."""

from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field as dc_field
from enum import Enum
from pathlib import Path
from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from tools.problem_validator.models import ValidationResult as ProblemValidationResult


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
        sev_order = {Severity.ERROR: 0, Severity.WARNING: 1, Severity.INFO: 2}
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
    body: str = ""


@dataclass
class AttemptDocument:
    path: Path
    relative_path: str
    data: dict[str, Any]
    body: str = ""
    object_id: str | None = None
    parse_ok: bool = True
    record_anchor: str | None = None

    @property
    def metadata(self) -> dict[str, Any]:
        return self.data

    @property
    def source_display(self) -> str:
        if self.record_anchor:
            return f"{self.relative_path} :: {self.record_anchor}"
        return self.relative_path

    @property
    def schema_version(self) -> Any:
        return self.data.get("schema_version")

    @property
    def id(self) -> str | None:
        return self.object_id

    @property
    def type(self) -> Any:
        return self.data.get("type")

    @property
    def problem(self) -> Any:
        return self.data.get("problem")

    @property
    def part(self) -> Any:
        return self.data.get("part")

    @property
    def outcome(self) -> Any:
        return self.data.get("outcome")

    @property
    def assistance(self) -> Any:
        return self.data.get("assistance")

    @property
    def attempted_at(self) -> Any:
        return self.data.get("attempted_at")

    @property
    def corrections(self) -> Any:
        return self.data.get("corrections")


@dataclass
class DependencySummary:
    healthy: bool = True
    errors: int = 0
    warnings: int = 0
    problem_objects: int = 0
    result: str = "PASS"


@dataclass
class ValidationSummary:
    markdown_files: int = 0
    attempt_objects: int = 0
    errors: int = 0
    warnings: int = 0
    info: int = 0
    result: str = "PASS"


@dataclass
class ValidationResult:
    project_root: Path
    summary: ValidationSummary
    issues: list[ValidationIssue] = dc_field(default_factory=list)
    documents: list[AttemptDocument] = dc_field(default_factory=list)
    registry: dict[str, AttemptDocument] = dc_field(default_factory=dict)
    dependency: DependencySummary = dc_field(default_factory=DependencySummary)
    focus_relative_path: str | None = None
    problem_result: ProblemValidationResult | None = None

    def add_issue(self, issue: ValidationIssue) -> None:
        self.issues.append(issue)

    def finalize(self) -> None:
        self.issues.sort(key=lambda i: i.sort_key())
        self.summary.errors = sum(1 for i in self.issues if i.severity == Severity.ERROR)
        self.summary.warnings = sum(1 for i in self.issues if i.severity == Severity.WARNING)
        self.summary.info = sum(1 for i in self.issues if i.severity == Severity.INFO)
        self.summary.result = "FAIL" if self.summary.errors else "PASS"
