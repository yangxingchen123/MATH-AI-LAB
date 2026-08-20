"""Fixtures for latex_build tests."""

from __future__ import annotations

from pathlib import Path

import pytest

from tests.problem_validator.conftest import write_project


@pytest.fixture
def repo_root(tmp_path: Path) -> Path:
    root = write_project(tmp_path)
    (root / "04_LATEX").mkdir(exist_ok=True)
    (root / "08_成果输出").mkdir(exist_ok=True)
    return root


def install_pinned_vendor(
    repo: Path,
    *,
    main_text: str = "% template\n",
    cls_text: str | None = None,
) -> Path:
    """Install a fixture vendor tree (does not copy production vendor docs unless asked)."""
    tpl = repo / "04_LATEX" / "模板" / "数学讲义模板_v1"
    vendor = tpl / "vendor" / "ElegantBook-v4.7"
    vendor.mkdir(parents=True, exist_ok=True)
    tpl.mkdir(parents=True, exist_ok=True)
    (tpl / "main.tex").write_text(main_text, encoding="utf-8")
    if cls_text is None:
        cls_text = (
            "\\ProvidesClass{elegantbook}[2026/2/27 v4.6 ElegantBook document class]\n"
            + ("%x" * 80)
            + "\n"
        )
    (vendor / "elegantbook.cls").write_text(cls_text, encoding="utf-8")
    return vendor


def write_latex_project(
    repo: Path,
    relative: str,
    *,
    with_entry: bool = True,
    legacy_main_only: bool = False,
    body: str = r"\documentclass{article}\begin{document}Hi\end{document}",
) -> Path:
    project = repo / "04_LATEX" / relative
    project.mkdir(parents=True, exist_ok=True)
    topic_name = project.name
    if with_entry:
        (project / f"{topic_name}.tex").write_text(body, encoding="utf-8")
    if legacy_main_only:
        (project / "main.tex").write_text(body, encoding="utf-8")
    return project
