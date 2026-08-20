"""Static profile composition tests."""

from __future__ import annotations

from tools.verification.profiles import ALL_CHECK_ORDER, CORE_CHECK_ORDER, LATEX_CHECKS


def test_core_order_is_source_derived_software() -> None:
    assert CORE_CHECK_ORDER == (
        "Knowledge Validator",
        "Problem Validator",
        "Attempt Validator",
        "Method Validator",
        "Workspace Indexer",
        "Workspace Check",
        "pytest",
    )


def test_all_is_core_plus_latex() -> None:
    assert ALL_CHECK_ORDER == CORE_CHECK_ORDER + LATEX_CHECKS
