"""Runtime status enums for Normal Operation orchestration."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from .models import FinalizeResult, LayerStatus


class PersistenceStatus(str, Enum):
    WRITTEN = "WRITTEN"
    CORRECTED = "CORRECTED"
    NO_OP = "NO_OP"
    FAILED = "FAILED"
    NOT_REQUESTED = "NOT_REQUESTED"


class AttemptRecordStatus(str, Enum):
    CREATED = "CREATED"
    NONE = "NONE"
    FAILED = "FAILED"


class ArtifactStatus(str, Enum):
    COMPLETE = "COMPLETE"
    FAILED = "FAILED"
    NOT_REQUESTED = "NOT_REQUESTED"


@dataclass
class OperationResult:
    """Ephemeral runtime result — not a Source Schema."""

    changed_types: list[str] = field(default_factory=list)
    persistence: PersistenceStatus = PersistenceStatus.NOT_REQUESTED
    attempt: AttemptRecordStatus = AttemptRecordStatus.NONE
    artifact: ArtifactStatus = ArtifactStatus.NOT_REQUESTED
    persistence_target: str | None = None
    persistence_path: str | None = None
    attempt_id: str | None = None
    attempt_ledger_path: str | None = None
    artifact_path: str | None = None
    error: str | None = None
    finalize: FinalizeResult | None = None
    reconcile: object | None = None
    canonical_coverage: str | None = None
    workflow: str | None = None
    latex: str | None = None
    pdf: str | None = None

    @property
    def persistence_pass(self) -> bool:
        return self.persistence in {
            PersistenceStatus.WRITTEN,
            PersistenceStatus.CORRECTED,
            PersistenceStatus.NO_OP,
            PersistenceStatus.NOT_REQUESTED,
        }

    @property
    def infra_pass(self) -> bool:
        if self.finalize is None and self.reconcile is None:
            return self.persistence != PersistenceStatus.FAILED and self.attempt != AttemptRecordStatus.FAILED
        if self.reconcile is not None and hasattr(self.reconcile, "overall_pass"):
            return bool(self.reconcile.overall_pass)
        if self.finalize is None:
            return self.persistence != PersistenceStatus.FAILED and self.attempt != AttemptRecordStatus.FAILED
        return self.finalize.overall_pass

    @property
    def workspace_sync_performed(self) -> bool:
        if self.reconcile is not None and hasattr(self.reconcile, "counters"):
            return self.reconcile.counters.workspace_syncs > 0
        return bool(self.finalize and self.finalize.workspace_sync_performed)

    def compact_lines(self) -> list[str]:
        lines = [
            f"Persistence: {self.persistence.value}",
            f"Attempt: {self.attempt.value}",
        ]
        if self.canonical_coverage:
            lines.append(f"Canonical Coverage: {self.canonical_coverage}")
        if self.workflow:
            lines.append(f"Workflow: {self.workflow}")
        if self.latex:
            lines.append(f"LaTeX: {self.latex}")
        if self.pdf:
            lines.append(f"PDF: {self.pdf}")
        if self.finalize:
            lines.append(f"Workspace: {self.finalize.workspace_final or 'N/A'}")
            lines.append(f"Verification: {self.finalize.verification_status.value}")
        elif self.reconcile is not None and getattr(self.reconcile, "finalize", None):
            fin = self.reconcile.finalize
            lines.append(f"Workspace: {fin.workspace_final or 'N/A'}")
            lines.append(f"Verification: {fin.verification_status.value}")
        else:
            lines.append("Workspace: NOT_RUN")
            lines.append("Verification: NOT_RUN")
        lines.append(f"Artifact: {self.artifact.value}")
        return lines
