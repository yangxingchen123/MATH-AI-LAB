"""Transactional publish of generated index snapshot."""

from __future__ import annotations

import os
import shutil
import uuid
from pathlib import Path

from .constants import INDEX_DIR_NAME, INDEX_DIR_RELATIVE, MANAGED_FILES
from .models import IndexerIssue, RenderedIndex


class PublishError(Exception):
    def __init__(self, message: str, rule_id: str = "KI-PUBLISH-001") -> None:
        super().__init__(message)
        self.message = message
        self.rule_id = rule_id


def index_dir_path(project_root: Path) -> Path:
    return project_root / INDEX_DIR_RELATIVE


def read_current_index_files(project_root: Path) -> dict[str, str] | None:
    """Return current managed file contents, or None if index dir missing."""
    index_dir = index_dir_path(project_root)
    if not index_dir.is_dir():
        return None
    out: dict[str, str] = {}
    for name in MANAGED_FILES:
        path = index_dir / name
        if not path.is_file():
            continue
        out[name] = path.read_text(encoding="utf-8")
    return out


def files_match_expected(current: dict[str, str] | None, expected: RenderedIndex) -> bool:
    if current is None:
        return False
    if set(current.keys()) != set(expected.files.keys()):
        return False
    for name, text in expected.files.items():
        if current.get(name) != text:
            return False
    # Also ensure no unexpected files in directory
    index_dir = None
    return True


def list_unexpected_files(project_root: Path) -> list[str]:
    index_dir = index_dir_path(project_root)
    if not index_dir.is_dir():
        return []
    unexpected: list[str] = []
    for path in sorted(index_dir.rglob("*")):
        if path.is_dir():
            continue
        rel = path.relative_to(index_dir).as_posix()
        if rel not in MANAGED_FILES:
            unexpected.append(rel)
    return unexpected


def write_temp_index(project_root: Path, rendered: RenderedIndex) -> Path:
    """Write full snapshot into a sibling temp directory under 01_知识库/."""
    kb = project_root / "01_知识库"
    kb.mkdir(parents=True, exist_ok=True)
    unique = f"{os.getpid()}_{uuid.uuid4().hex[:8]}"
    temp_dir = kb / f"._索引_build_{unique}"
    if temp_dir.exists():
        shutil.rmtree(temp_dir)
    temp_dir.mkdir(parents=True, exist_ok=False)
    try:
        for name in MANAGED_FILES:
            text = rendered.files[name]
            target = temp_dir / name
            with target.open("w", encoding="utf-8", newline="\n") as fh:
                fh.write(text)
        # Verify
        for name in MANAGED_FILES:
            if not (temp_dir / name).is_file():
                raise PublishError(f"Temp index missing {name}", "KI-IO-001")
        import json

        payload = json.loads((temp_dir / "knowledge_index.json").read_text(encoding="utf-8"))
        if payload.get("index_version") != 1:
            raise PublishError("Temp JSON index_version != 1", "KI-RENDER-001")
        for kid, entry in payload.get("knowledge", {}).items():
            path = entry.get("path", "")
            if Path(path).is_absolute():
                raise PublishError(
                    f"Absolute path detected for {kid}: {path}", "KI-RENDER-001"
                )
        return temp_dir
    except Exception:
        if temp_dir.exists():
            shutil.rmtree(temp_dir, ignore_errors=True)
        raise


def publish_index(project_root: Path, rendered: RenderedIndex) -> None:
    """
    Transactional swap / rollback-safe publish:

    1. Write temp snapshot
    2. Rename current `_索引` -> backup (if exists)
    3. Rename temp -> `_索引`
    4. Remove backup
    On failure after step 2: restore backup.
    """
    index_dir = index_dir_path(project_root)
    kb = project_root / "01_知识库"
    backup: Path | None = None
    temp_dir: Path | None = None
    try:
        temp_dir = write_temp_index(project_root, rendered)
        if not index_dir.exists():
            os.replace(temp_dir, index_dir)
            temp_dir = None
            return

        backup = kb / f"._索引_backup_{os.getpid()}_{uuid.uuid4().hex[:8]}"
        os.replace(index_dir, backup)
        try:
            os.replace(temp_dir, index_dir)
            temp_dir = None
        except Exception as exc:
            # Rollback
            if backup.exists() and not index_dir.exists():
                os.replace(backup, index_dir)
                backup = None
            raise PublishError(f"Publish swap failed: {exc}", "KI-PUBLISH-001") from exc

        if backup is not None and backup.exists():
            shutil.rmtree(backup, ignore_errors=True)
            backup = None
    finally:
        if temp_dir is not None and temp_dir.exists():
            shutil.rmtree(temp_dir, ignore_errors=True)
        if backup is not None and backup.exists() and not index_dir.exists():
            try:
                os.replace(backup, index_dir)
            except OSError:
                pass
