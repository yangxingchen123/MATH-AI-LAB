"""Cost report over a ledger. Zero USD remains undefined for cost-adjusted success."""

from __future__ import annotations

from pathlib import Path

from .ledger import load_entries, spent


def cost_report(path: Path | None = None) -> dict:
    entries = load_entries(path) if path is not None else []
    usd, seconds = spent(entries)
    verified = sum(1 for item in entries if item.result_status == "ok")
    return {
        "n": len(entries),
        "usd": usd,
        "seconds": seconds,
        "verified_successes": verified,
        "cost_adjusted_success": None if usd <= 0 else verified / usd,
        "writes_source": False,
        "core_impact": False,
        "note": "cost_adjusted_success is undefined at 0 USD.",
    }
