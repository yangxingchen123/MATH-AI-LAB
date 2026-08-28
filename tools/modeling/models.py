"""Domain types for the modeling framework. Not Frozen Schema."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class ManifestValidationResult:
    ok: bool
    errors: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class RunResult:
    run_id: str
    status: str
    metrics: dict[str, float]
    output_dir: str
    message: str
