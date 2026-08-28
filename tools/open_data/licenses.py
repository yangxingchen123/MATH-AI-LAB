"""License classifier for open-data discovery. Not Frozen Schema."""

from __future__ import annotations

_OPEN_TOKENS = (
    "cc0",
    "cc-zero",
    "cc-by-sa",
    "cc-by-",
    "cc-by ",
    "cc_by",
    "odc-by",
    "odc-odbl",
    "odc-pddl",
    "pddl",
    "public-domain",
    "public domain",
    "us-government",
    "government-work",
    "government works",
)
_REJECT_TOKENS = (
    "cc-by-nc",
    "cc-by-nd",
    "cc_by_nc",
    "cc_by_nd",
    "all-rights-reserved",
    "copyright",
    "proprietary",
)


def classify_license(raw: str | None) -> str:
    text = " ".join(str(raw or "").strip().lower().replace("_", "-").split())
    if not text:
        return "NEEDS_REVIEW"
    compact = text.replace(" ", "-")
    if any(token in compact or token in text for token in _REJECT_TOKENS):
        return "REJECTED"
    if compact in {"cc-by", "ccby"} or compact.startswith("cc-by-"):
        if "nc" in compact.split("-") or "nd" in compact.split("-"):
            return "REJECTED"
        return "OPEN"
    if any(token in compact or token in text for token in _OPEN_TOKENS):
        return "OPEN"
    return "NEEDS_REVIEW"
