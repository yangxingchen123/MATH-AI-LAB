"""Constants for LaTeX build automation."""

from __future__ import annotations

from pathlib import Path

LATEX_ROOT = "04_LATEX"
OUTPUT_ROOT = "08_成果输出"
FORMAL_PDF_PREFIX = "PDF"
TEMPLATE_MAIN_TEX_NAME = "main.tex"
EXCLUDED_LATEX_PREFIXES: tuple[str, ...] = ("模板/",)

DEFAULT_TEMPLATE_REL = Path("04_LATEX") / "模板" / "数学讲义模板_v1"
PINNED_ELEGANTBOOK_TAG = "v4.7"
PINNED_ELEGANTBOOK_COMMIT = "0ff65a821726d945bc425b2ea560aea8227bf6c1"
PINNED_ELEGANTBOOK_DIR = Path("vendor") / "ElegantBook-v4.7"
# Official GitHub tag v4.7 archive still ships this ProvidesClass string (upstream labeling).
PINNED_ELEGANTBOOK_PROVIDES_CLASS = "2026/2/27 v4.6 ElegantBook document class"

MAX_XELATEX_PASSES = 2

XELATEX_ARGS: tuple[str, ...] = (
    "-interaction=nonstopmode",
    "-file-line-error",
    "-halt-on-error",
)

RERUN_SIGNALS: tuple[str, ...] = (
    "Rerun to get cross-references right",
    "Label(s) may have changed",
    "There were undefined references",
)
