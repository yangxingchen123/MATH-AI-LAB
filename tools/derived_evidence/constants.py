"""Constants for Descriptive Evidence State v1 (Derived Contract)."""

from __future__ import annotations

OUTCOME_CATEGORIES: tuple[str, ...] = (
    "correct",
    "incorrect",
    "partial",
    "unsolved",
    "abandoned",
    "unassessed",
)

ASSISTANCE_CATEGORIES: tuple[str, ...] = (
    "independent",
    "assisted",
    "omitted",
)

DERIVED_CONTRACT_VERSION = "Descriptive Evidence State v1"
