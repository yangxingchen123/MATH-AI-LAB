"""Lean formalization types. Not Frozen Schema."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class CorrespondenceResult:
    ok: bool
    errors: list[str] = field(default_factory=list)
    families: list[str] = field(default_factory=list)
