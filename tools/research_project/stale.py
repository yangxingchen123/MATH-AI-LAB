"""Dossier freshness: Generated region vs expected canonical render."""

from __future__ import annotations

from pathlib import Path

from .constants import DOSSIER_BEGIN, DOSSIER_END
from .renderer import render_generated_dossier_for_project


class DamagedDossierMarkers(ValueError):
    """Generated marker pair is missing, duplicated, or mis-ordered."""


def split_dossier(text: str) -> tuple[str, str, str]:
    begin_count = text.count(DOSSIER_BEGIN)
    end_count = text.count(DOSSIER_END)
    if begin_count != 1 or end_count != 1:
        raise DamagedDossierMarkers("Generated dossier markers are damaged")
    begin_at = text.find(DOSSIER_BEGIN)
    end_at = text.find(DOSSIER_END)
    if begin_at < 0 or end_at < begin_at:
        raise DamagedDossierMarkers("Generated dossier markers are mis-ordered")
    human = text[:begin_at]
    generated = text[begin_at + len(DOSSIER_BEGIN) : end_at]
    tail = text[end_at + len(DOSSIER_END) :]
    return human, generated, tail


def expected_generated_region(project: Path) -> str:
    body = render_generated_dossier_for_project(project)
    return "\n" + body


def dossier_is_stale(project: Path) -> bool:
    path = Path(project) / "research_dossier.md"
    text = path.read_text(encoding="utf-8")
    try:
        _, current, _ = split_dossier(text)
    except DamagedDossierMarkers:
        return True
    expected = expected_generated_region(project)
    return current != expected
