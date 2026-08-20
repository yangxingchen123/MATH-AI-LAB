"""Atomic text replacement for official Source files."""

from __future__ import annotations

import os
import uuid
from collections.abc import Callable
from pathlib import Path


class AtomicWriteError(Exception):
    def __init__(self, message: str, *, rule_id: str = "SRC-IO-E001") -> None:
        super().__init__(message)
        self.message = message
        self.rule_id = rule_id


def atomic_replace_text(official_path: Path, candidate_text: str) -> None:
    """Replace official file with candidate text using temp file + os.replace."""
    official_path = official_path.resolve()
    official_path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = official_path.with_name(f".{official_path.name}.{uuid.uuid4().hex}.tmp")
    try:
        data = candidate_text.encode("utf-8")
        with temp_path.open("wb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_path, official_path)
    except OSError as exc:
        if temp_path.exists():
            temp_path.unlink(missing_ok=True)
        raise AtomicWriteError(f"Atomic replace failed for {official_path}: {exc}") from exc
    finally:
        if temp_path.exists():
            temp_path.unlink(missing_ok=True)


def write_candidate_then_replace(
    official_path: Path,
    candidate_text: str,
    *,
    validate: Callable[[str], object],
) -> object:
    """Validate candidate, then atomically replace official file.

    ``validate(candidate_text)`` must raise on invalid candidate or return a result object.
    Official file is unchanged when validation fails.
    """
    official_path = official_path.resolve()
    original = official_path.read_text(encoding="utf-8") if official_path.is_file() else None
    try:
        result = validate(candidate_text)
    except Exception:
        if original is not None and official_path.is_file():
            current = official_path.read_text(encoding="utf-8")
            if current != original:
                atomic_replace_text(official_path, original)
        raise
    atomic_replace_text(official_path, candidate_text)
    return result
