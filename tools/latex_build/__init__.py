"""Formal LaTeX build and artifact publishing for MATH-AI-LAB."""

from __future__ import annotations

from .cli import main, run
from .models import LatexBuildResult
from .service import build_latex_project, check_latex_project

__all__ = [
    "LatexBuildResult",
    "build_latex_project",
    "check_latex_project",
    "main",
    "run",
]
