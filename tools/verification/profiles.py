"""Static verification profiles — not a plugin registry."""

from __future__ import annotations

PROFILE_CORE = "core"
PROFILE_LATEX_SMOKE = "latex-smoke"
PROFILE_ALL = "all"

CORE_SOURCE_CHECKS: tuple[str, ...] = (
    "Knowledge Validator",
    "Problem Validator",
    "Attempt Validator",
    "Method Validator",
)

CORE_DERIVED_CHECKS: tuple[str, ...] = (
    "Workspace Indexer",
    "Workspace Check",
)

CORE_SOFTWARE_CHECKS: tuple[str, ...] = ("pytest",)

LATEX_CHECKS: tuple[str, ...] = ("LaTeX Smoke",)

CORE_CHECK_ORDER: tuple[str, ...] = (
    *CORE_SOURCE_CHECKS,
    *CORE_DERIVED_CHECKS,
    *CORE_SOFTWARE_CHECKS,
)

ALL_CHECK_ORDER: tuple[str, ...] = (*CORE_CHECK_ORDER, *LATEX_CHECKS)

PROFILES_REQUIRING_LATEX_PROJECT: frozenset[str] = frozenset(
    {PROFILE_LATEX_SMOKE, PROFILE_ALL}
)
