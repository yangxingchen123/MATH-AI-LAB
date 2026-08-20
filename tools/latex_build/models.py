"""Data models for LaTeX build automation."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path


class IssueSeverity(str, Enum):
    ERROR = "ERROR"
    WARNING = "WARNING"


class PublishStatus(str, Enum):
    CREATED = "CREATED"
    UPDATED = "UPDATED"
    UP_TO_DATE = "UP_TO_DATE"
    BLOCKED = "BLOCKED"
    SKIPPED = "SKIPPED"


@dataclass(frozen=True)
class BuildIssue:
    severity: IssueSeverity
    code: str
    message: str
    line: int | None = None
    source_hint: str | None = None


@dataclass(frozen=True)
class ResolvedLatexProject:
    project_dir: Path
    relative_project_path: Path
    main_tex: Path
    formal_pdf: Path


@dataclass(frozen=True)
class CompileResult:
    success: bool
    return_code: int
    compiler: str
    compiler_runs: int
    stdout: str
    stderr: str
    log_text: str
    built_pdf: Path | None
    issues: tuple[BuildIssue, ...] = ()


@dataclass(frozen=True)
class InspectionResult:
    blocking_errors: tuple[BuildIssue, ...]
    warnings: tuple[BuildIssue, ...]

    @property
    def publish_allowed(self) -> bool:
        return len(self.blocking_errors) == 0


@dataclass(frozen=True)
class PublishResult:
    status: PublishStatus
    formal_pdf: Path
    writes: int
    message: str = ""


@dataclass(frozen=True)
class LatexBuildResult:
    project: ResolvedLatexProject
    compile_result: CompileResult
    inspection_result: InspectionResult
    publish_result: PublishResult | None = None

    @property
    def blocking_error_count(self) -> int:
        return len(self.inspection_result.blocking_errors)

    @property
    def warning_count(self) -> int:
        return len(self.inspection_result.warnings)
