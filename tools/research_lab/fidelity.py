"""Statement-fidelity mutants for P001. No external model calls."""

from __future__ import annotations

from pathlib import Path

import yaml


def load_suite(path: Path) -> dict:
    data = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
    if not isinstance(data, dict):
        raise ValueError("fidelity suite must be a mapping")
    return data


def detect_mutants(statement: str) -> list[str]:
    text = statement.lower()
    hits: list[str] = []
    has_exp = "e^x" in text or "exp" in text
    has_quadratic = "x^2/2" in text or "x²/2" in text or "quadratic" in text
    if has_exp and "maximum" in text and "p > 0" not in text and "p>0" not in text:
        hits.append("max_for_sup_exp")
    if has_exp and "conjugat" in text and "p > 0" not in text and "p>0" not in text:
        if "p < 0" not in text and "p≤0" not in text and "p <= 0" not in text:
            hits.append("omit_exp_domain")
    if has_quadratic and ("p = 0" in text or "p=0" in text) and (
        "not attained" in text or "fails" in text or "infinite" in text
    ):
        hits.append("quadratic_missed_at_zero")
    if "inf" in text and "min" in text and "without" in text:
        hits.append("inf_min_swap")
    if "write inf for min" in text or "inf as min" in text:
        hits.append("inf_min_swap")
    if has_exp and ("coincide" in text or "sup = max" in text or "sup and max" in text):
        hits.append("exp_sup_max_collapse")
    if "reparameteriz" in text and ("same graph" in text or "same curve" in text):
        hits.append("legendre_always_reparam")
    return hits


def evaluate_suite(path: Path) -> dict:
    suite = load_suite(path)
    gold_hits = detect_mutants(str(suite.get("gold", "")))
    mutants = suite.get("mutants") or []
    caught = 0
    missed: list[str] = []
    for item in mutants:
        expected = str(item.get("defect"))
        found = detect_mutants(str(item.get("statement", "")))
        if expected in found:
            caught += 1
        else:
            missed.append(expected)
    equivalents = suite.get("equivalents") or []
    equiv_dirty = [text for text in equivalents if detect_mutants(str(text))]
    total = max(len(mutants), 1)
    return {
        "gold_clean": gold_hits == [],
        "equivalents_clean": equiv_dirty == [],
        "caught": caught,
        "total": len(mutants),
        "missed": missed,
        "rate": caught / total,
    }
