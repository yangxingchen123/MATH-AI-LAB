"""Detect weakened or omitted-assumption formal statements."""

from __future__ import annotations

import re

FORALL_NL = re.compile(r"for all|forall|∀|任意", re.I)
STRICT_NL = re.compile(r"strictly greater|strict inequality|>\s*n|大于", re.I)
BINDER_RE = re.compile(r"theorem\s+(\w+)\s*(.*?)\s*:=")


def theorem_header(text: str, decl: str) -> str:
    match = re.search(rf"theorem\s+{re.escape(decl)}\s*(.*?)(?::=|$)", text, re.S)
    if not match:
        return ""
    return re.sub(r"\s+", " ", match.group(1)).strip()


def detect_weakening(entry: dict, lean_text: str) -> list[str]:
    issues: list[str] = []
    nl = str(entry.get("natural_language") or "")
    decl = str(entry.get("lean_decl") or "").rsplit(".", 1)[-1]
    header = theorem_header(lean_text, decl)
    if not header:
        return [f"declaration {decl} not found"]
    has_binder = bool(re.search(r"\([^)]*:", header))
    if FORALL_NL.search(nl) and not has_binder:
        issues.append("quantifier dropped")
    if STRICT_NL.search(nl) and re.search(r"≥|>=|Nat\.le\b", header) and not re.search(
        r">|Nat\.lt\b", header
    ):
        issues.append("strict inequality weakened to non-strict")
    expected = entry.get("assumptions") or []
    if isinstance(expected, list):
        hidden = [item for item in expected if isinstance(item, str) and item.startswith("hidden:")]
        issues.extend(f"hidden assumption: {item}" for item in hidden)
    return issues
