"""Publication journal gates G0–G6. Scaffolding only; never claims 四大."""

from __future__ import annotations

JOURNAL_GATES: tuple[str, ...] = ("G0", "G1", "G2", "G3", "G4", "G5", "G6")

S3_PLUS: frozenset[str] = frozenset({"S3", "S4", "S5"})


def evaluate_journal(problem: dict) -> dict:
    gates = [
        _gate(
            "G0",
            bool(problem.get("human_pi_signoff")) and bool(problem.get("importance_rationale")),
            "human PI signoff and importance rationale",
        ),
        _gate(
            "G1",
            problem.get("novelty_claim") == "first"
            and bool(problem.get("expert_signoff"))
            and bool(problem.get("prior_art")),
            "first-claim needs expert_signoff and prior_art; known is not G1",
        ),
        _gate(
            "G2",
            bool(problem.get("evaluator")),
            "falsifiable evaluator registered",
        ),
        _gate(
            "G3",
            problem.get("human_proof") is True,
            "complete human proof marked",
        ),
        _gate(
            "G4",
            bool(problem.get("lean_decls")),
            "machine-checkable Lean declarations listed",
        ),
        _gate(
            "G5",
            bool(problem.get("human_pi_signoff"))
            and str(problem.get("success_level") or "") in S3_PLUS,
            "importance: PI signoff and success_level S3+",
        ),
        _gate(
            "G6",
            problem.get("paper_checklist") is True,
            "paper quality checklist signed",
        ),
    ]
    paper_ready = all(item["status"] == "PASS" for item in gates)
    return {
        "ok": paper_ready,
        "paper_ready": paper_ready,
        "claims_四大": False,
        "writes_source": False,
        "core_impact": False,
        "problem_id": problem.get("id"),
        "gates": gates,
        "note": "Journal gates are scaffolding. Passing them still does not claim 四大.",
    }


def _gate(gate_id: str, ok: bool, detail: str) -> dict:
    return {
        "id": gate_id,
        "status": "PASS" if ok else "FAIL",
        "detail": detail,
    }
