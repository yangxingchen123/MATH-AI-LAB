from pathlib import Path

from tools.collaboration.gate import GATE_METRIC_NAMES, evaluate_gate
from tools.collaboration.orchestrator import defect_recall, run_task

FIXTURE = Path(__file__).resolve().parents[1] / "review" / "fixtures"


def test_multi_role_finds_more_than_solver():
    multi = run_task(FIXTURE, roles=None)
    single = run_task(FIXTURE, roles=("SOLVER",))
    assert defect_recall(multi) > defect_recall(single)
    assert all(item.candidate for item in multi.roles)
    assert multi.source_mutations == []
    assert multi.disagreements


def test_timeout_and_cancel_fallback():
    timed = run_task(FIXTURE, timeout_role="FORMALIZER")
    cancelled = run_task(FIXTURE, cancel=True)
    assert timed.final_status == "PARTIAL"
    assert timed.fallback == "SOLVER"
    assert cancelled.final_status == "CANCELLED"
    assert cancelled.fallback == "SOLVER"


def test_restricted_remote_is_blocked():
    audit = run_task(FIXTURE, data_level="RESTRICTED", remote=True)
    assert audit.restricted_remote_sends == 0
    assert audit.final_status == "FAILED"
    assert audit.fallback == "local-only"


def test_collaboration_gate():
    report = evaluate_gate()
    names = [item["name"] for item in report["metrics"]]
    assert names == list(GATE_METRIC_NAMES)
    assert report["status"] == "PASS"
    assert report["pilot"] is True


def test_cli_gate():
    from tools.collaboration.cli import main

    assert main(["gate"]) == 0
    assert main(["run", "--help"]) == 0
