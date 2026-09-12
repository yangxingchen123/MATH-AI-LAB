"""Append-only model-call ledger with hard USD and wall-clock caps."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path


class BudgetExceeded(Exception):
    def __init__(self, message: str, spent_usd: float, spent_seconds: float) -> None:
        super().__init__(message)
        self.spent_usd = spent_usd
        self.spent_seconds = spent_seconds


@dataclass(frozen=True)
class Budget:
    hard_limit_usd: float
    hard_limit_seconds: float


@dataclass(frozen=True)
class LedgerEntry:
    task_id: str
    stage: str
    model: str
    usd: float
    seconds: float
    input_hash: str
    result_status: str


FUNNEL_CAPS_USD: dict[str, float] = {
    "C0": 1.0,
    "C1": 10.0,
    "C2": 100.0,
    "C3": 1000.0,
    "C4": 10000.0,
    "C5": 100000.0,
}


def budget_for_layer(layer: str, *, hard_limit_seconds: float = 1800.0) -> Budget:
    if layer not in FUNNEL_CAPS_USD:
        raise ValueError(f"unknown funnel layer: {layer}")
    return Budget(hard_limit_usd=FUNNEL_CAPS_USD[layer], hard_limit_seconds=hard_limit_seconds)



def load_entries(path: Path) -> list[LedgerEntry]:
    if not path.is_file():
        return []
    out: list[LedgerEntry] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        data = json.loads(line)
        out.append(
            LedgerEntry(
                task_id=str(data["task_id"]),
                stage=str(data["stage"]),
                model=str(data["model"]),
                usd=float(data["usd"]),
                seconds=float(data["seconds"]),
                input_hash=str(data["input_hash"]),
                result_status=str(data["result_status"]),
            )
        )
    return out


def spent(entries: list[LedgerEntry]) -> tuple[float, float]:
    return (sum(item.usd for item in entries), sum(item.seconds for item in entries))


def append_entry(path: Path, entry: LedgerEntry, budget: Budget) -> str:
    existing = load_entries(path)
    if any(item.input_hash == entry.input_hash for item in existing):
        return "cached"
    usd, seconds = spent(existing)
    if usd + entry.usd > budget.hard_limit_usd:
        raise BudgetExceeded(
            f"USD cap {budget.hard_limit_usd} exceeded",
            spent_usd=usd,
            spent_seconds=seconds,
        )
    if seconds + entry.seconds > budget.hard_limit_seconds:
        raise BudgetExceeded(
            f"seconds cap {budget.hard_limit_seconds} exceeded",
            spent_usd=usd,
            spent_seconds=seconds,
        )
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(asdict(entry), sort_keys=True) + "\n")
    return "recorded"
