"""Legal stage edges for the open-problem machine. Not Frozen Schema."""

from __future__ import annotations

from .journal import evaluate_journal
from .registry import STAGES, TERMINAL_STAGES, validate_record

FORWARD: dict[str, frozenset[str]] = {
    "INBOX": frozenset({"TRIAGED"}),
    "TRIAGED": frozenset({"PRIOR_ART_CHECKED"}),
    "PRIOR_ART_CHECKED": frozenset({"STATEMENT_REVIEWED"}),
    "STATEMENT_REVIEWED": frozenset({"FALSIFICATION"}),
    "FALSIFICATION": frozenset({"CANDIDATE_SURVIVED"}),
    "CANDIDATE_SURVIVED": frozenset({"PROOF_PLANNED"}),
    "PROOF_PLANNED": frozenset({"PROVED_INFORMAL"}),
    "PROVED_INFORMAL": frozenset({"PROVED_FORMAL"}),
    "PROVED_FORMAL": frozenset({"EXTERNAL_REVIEWED"}),
    "EXTERNAL_REVIEWED": frozenset({"PAPER_READY"}),
    "PAPER_READY": frozenset(),
}


def allowed_transition(current: str, nxt: str) -> bool:
    if current in TERMINAL_STAGES:
        return False
    if nxt in TERMINAL_STAGES:
        return current in STAGES
    return nxt in FORWARD.get(current, frozenset())


def advance(record: dict, new_stage: str) -> tuple[dict | None, list[str]]:
    current = str(record.get("stage") or "")
    if not allowed_transition(current, new_stage):
        return None, [f"illegal transition {current} -> {new_stage}"]
    updated = dict(record)
    updated["stage"] = new_stage
    errors = validate_record(updated)
    if errors:
        return None, errors
    if new_stage == "PAPER_READY":
        journal = evaluate_journal(updated)
        if not journal.get("paper_ready"):
            failed = [
                item["id"]
                for item in journal.get("gates") or []
                if item.get("status") != "PASS"
            ]
            return None, [f"journal_gates_incomplete:{','.join(failed)}"]
    return updated, []
