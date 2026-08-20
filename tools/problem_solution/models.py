"""Runtime models for canonical Solution upsert."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class UpsertAction(str, Enum):
    CREATE = "CREATE"
    UPDATE = "UPDATE"
    NO_OP = "NO_OP"


@dataclass(frozen=True)
class SolutionSlot:
    target: str
    content: str
    start: int
    end: int
    canonical: bool


@dataclass
class SolutionUpsertResult:
    action: UpsertAction
    target: str
    problem_id: str
    problem_path: str
    written: bool = False
    duplicate_slots: list[str] = field(default_factory=list)
    error: str | None = None
