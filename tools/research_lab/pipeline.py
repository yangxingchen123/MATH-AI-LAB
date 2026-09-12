"""Local sequential pipeline. Not Prefect/Temporal."""

from __future__ import annotations

from .cycle import run_cycle
from .funnel import run_funnel
from .journal import evaluate_journal


def run_pipeline(problem: dict, *, n: int = 5) -> dict:
    cycle = run_cycle(problem, n=n)
    funnel = run_funnel(problem, n=n, limit=8, stall_rounds=8)
    journal = evaluate_journal(problem)
    return {
        "ok": bool(cycle.get("ok")) and funnel.get("writes_source") is False,
        "scheduler": "local_sequential",
        "prefect": False,
        "cycle": {"ok": cycle.get("ok"), "usd": cycle.get("usd")},
        "funnel": {
            "ok": funnel.get("ok"),
            "attempts": funnel.get("attempts"),
            "clusters": funnel.get("clusters"),
        },
        "journal": {
            "paper_ready": journal.get("paper_ready"),
            "claims_四大": journal.get("claims_四大"),
        },
        "usd": 0.0,
        "writes_source": False,
        "core_impact": False,
    }
