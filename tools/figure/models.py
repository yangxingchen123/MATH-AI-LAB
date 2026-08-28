"""Figure domain types. Not Frozen Schema."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class FigureValidationResult:
    ok: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class FigureResult:
    figure_id: str
    family: str
    output_dir: Path
    svg_path: Path
    manifest_path: Path
    semantic_path: Path
    svg_sha256: str
    semantic_sha256: str
