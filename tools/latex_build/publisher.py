"""Publish formal PDF artifacts to 08_成果输出."""

from __future__ import annotations

import os
import shutil
from pathlib import Path

from .models import PublishResult, PublishStatus


class PublishError(Exception):
    """Raised when publication fails."""


def publish_formal_pdf(
    *,
    built_pdf: Path,
    formal_pdf: Path,
    publish_allowed: bool,
) -> PublishResult:
    if not publish_allowed:
        return PublishResult(
            status=PublishStatus.BLOCKED,
            formal_pdf=formal_pdf,
            writes=0,
            message="Publication blocked by inspection",
        )

    if not built_pdf.is_file() or built_pdf.stat().st_size == 0:
        return PublishResult(
            status=PublishStatus.BLOCKED,
            formal_pdf=formal_pdf,
            writes=0,
            message="Built PDF invalid",
        )

    formal_pdf.parent.mkdir(parents=True, exist_ok=True)
    existed_before = formal_pdf.is_file()

    if existed_before and formal_pdf.read_bytes() == built_pdf.read_bytes():
        return PublishResult(
            status=PublishStatus.UP_TO_DATE,
            formal_pdf=formal_pdf,
            writes=0,
            message="Formal PDF already up to date",
        )

    temp_path = formal_pdf.with_suffix(formal_pdf.suffix + ".tmp")
    try:
        shutil.copy2(built_pdf, temp_path)
        if not temp_path.is_file() or temp_path.stat().st_size == 0:
            raise PublishError("Temporary publish file invalid")
        os.replace(temp_path, formal_pdf)
    except Exception:
        if temp_path.exists():
            temp_path.unlink(missing_ok=True)
        raise
    finally:
        if temp_path.exists():
            temp_path.unlink(missing_ok=True)

    status = PublishStatus.CREATED if not existed_before else PublishStatus.UPDATED
    return PublishResult(
        status=status,
        formal_pdf=formal_pdf,
        writes=1,
        message="Formal PDF published",
    )
