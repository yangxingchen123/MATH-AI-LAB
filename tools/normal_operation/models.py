"""Runtime models for Normal Operation finalization."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class LayerStatus(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    SKIPPED = "SKIPPED"
    BLOCKED = "BLOCKED"


@dataclass
class FinalizeResult:
    changed_types: list[str]
    validation_status: LayerStatus = LayerStatus.SKIPPED
    validation_errors: int = 0
    workspace_initial: str | None = None
    workspace_sync_performed: bool = False
    workspace_final: str | None = None
    workspace_check_status: LayerStatus = LayerStatus.SKIPPED
    workspace_errors: int = 0
    workspace_warnings: int = 0
    verification_status: LayerStatus = LayerStatus.SKIPPED
    duration_seconds: float = 0.0
    suggested_action: str | None = None
    issues: list[str] = field(default_factory=list)

    @property
    def overall_pass(self) -> bool:
        return (
            self.validation_status != LayerStatus.FAIL
            and self.workspace_check_status != LayerStatus.FAIL
            and self.verification_status != LayerStatus.FAIL
        )
