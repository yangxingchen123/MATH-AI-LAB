"""Sealed run records. Generated artifacts only; not formal Source."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

FORBIDDEN_WRITE_NAMES: frozenset[str] = frozenset(
    {"项目进度.md", "元数据规范.md", "AGENTS.md", "项目规则.md"}
)


def canonical_json(data: object) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def statement_hash(record: dict) -> str:
    payload = {
        "id": record.get("id"),
        "title": record.get("title"),
        "evaluator": record.get("evaluator"),
        "success_level": record.get("success_level"),
        "novelty_claim": record.get("novelty_claim"),
    }
    return hashlib.sha256(canonical_json(payload).encode("utf-8")).hexdigest()


def seal_run(problem: dict, cycle_report: dict) -> dict:
    report = cycle_report.get("evaluator_report") or {}
    body = {
        "problem_id": problem.get("id"),
        "statement_hash": statement_hash(problem),
        "n": cycle_report.get("n"),
        "candidate": report.get("candidate"),
        "ok": bool(cycle_report.get("ok")),
        "usd": float(cycle_report.get("usd") or 0.0),
        "evidence_layer": cycle_report.get("evidence_layer"),
        "writes_source": False,
        "core_impact": False,
    }
    body["run_fingerprint"] = hashlib.sha256(
        canonical_json(
            {
                "statement_hash": body["statement_hash"],
                "n": body["n"],
                "candidate": body["candidate"],
                "ok": body["ok"],
                "usd": body["usd"],
            }
        ).encode("utf-8")
    ).hexdigest()
    return body


def append_chain(path: Path, sealed: dict) -> None:
    target = Path(path)
    if target.name in FORBIDDEN_WRITE_NAMES:
        raise ValueError(f"refusing to write {target.name}")
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(canonical_json(sealed) + "\n")


def load_chain(path: Path) -> list[dict]:
    if not path.is_file():
        return []
    rows: list[dict] = []
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        rows.append(json.loads(line))
    return rows


def reproduce(problem: dict, sealed: dict) -> dict:
    from .cycle import run_cycle

    n = int(sealed.get("n") or 0)
    raw = sealed.get("candidate")
    values = set(raw) if isinstance(raw, list) else None
    again = run_cycle(problem, n=n, values=values)
    new_sealed = seal_run(problem, again)
    errors: list[str] = []
    if new_sealed["statement_hash"] != sealed.get("statement_hash"):
        errors.append("statement_hash_mismatch")
    if new_sealed["run_fingerprint"] != sealed.get("run_fingerprint"):
        errors.append("fingerprint_mismatch")
    if new_sealed["usd"] != 0.0:
        errors.append("nonzero_usd")
    if new_sealed["writes_source"] is not False:
        errors.append("writes_source")
    return {
        "ok": errors == [],
        "sealed": new_sealed,
        "errors": errors,
        "writes_source": False,
        "core_impact": False,
    }
