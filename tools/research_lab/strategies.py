"""Lexical proof-strategy scan over Lean sources. Not a stored proof."""

from __future__ import annotations

import re
from pathlib import Path

import yaml

from .constants import CORRESPONDENCE_PATH, LEAN_ROOT

THEOREM_HEAD = re.compile(r"^(private\s+)?theorem\s+(\w+)\b", re.MULTILINE)
INDUCTION_RE = re.compile(r"\binduction\b")
ODDS_RE = re.compile(r"\bodds\b")


def scan_proof_strategies(path: Path | None = None, *, lean_root: Path | None = None) -> list[dict]:
    data = yaml.safe_load((path or CORRESPONDENCE_PATH).read_text(encoding="utf-8")) or {}
    theorems = [item for item in (data.get("theorems") or []) if isinstance(item, dict) and item.get("id")]
    blocks_by_file: dict[str, dict[str, str]] = {}
    induction: list[str] = []
    construction: list[str] = []
    root = lean_root or LEAN_ROOT
    for item in theorems:
        ident = str(item["id"])
        lean_file = str(item.get("lean_file") or "")
        decl = str(item.get("lean_decl") or "").rsplit(".", 1)[-1]
        if not lean_file or not decl:
            continue
        if lean_file not in blocks_by_file:
            abs_path = root / lean_file
            blocks_by_file[lean_file] = _public_theorem_blocks(abs_path) if abs_path.is_file() else {}
        body = blocks_by_file[lean_file].get(decl, "")
        if not body:
            continue
        if INDUCTION_RE.search(body):
            induction.append(ident)
        if ODDS_RE.search(body):
            construction.append(ident)
    rows: list[dict] = []
    if induction:
        rows.append(
            _strategy(
                "strategy:induction",
                "induction",
                induction,
                "Applies when a Nat/List statement is proved by recursion on the same inductive type.",
                "Lexical scan of `induction` in the public theorem body. Not a stored proof.",
            )
        )
    if construction:
        rows.append(
            _strategy(
                "strategy:algebraic_construction",
                "algebraic_construction",
                construction,
                "Applies when a named construction (here `odds`) is used inside the theorem body.",
                "Mentions of `odds` are not a uniqueness proof. Not Canonical.",
            )
        )
    return rows


def _strategy(ident: str, name: str, cases: list[str], conditions: str, limitations: str) -> dict:
    return {
        "id": ident,
        "strategy": name,
        "applicableConditions": [conditions],
        "successfulCases": cases,
        "failedCases": [],
        "limitations": [limitations],
        "not_a_proof": True,
        "not_a_theorem": True,
    }


def _public_theorem_blocks(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    matches = list(THEOREM_HEAD.finditer(text))
    blocks: dict[str, str] = {}
    for index, match in enumerate(matches):
        if match.group(1):
            continue
        name = match.group(2)
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        blocks[name] = text[match.start() : end]
    return blocks
