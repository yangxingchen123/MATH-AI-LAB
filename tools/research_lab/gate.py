"""Read-only v2.2-lab gate. Missing Lean never fails Core."""

from __future__ import annotations

from tempfile import TemporaryDirectory
from pathlib import Path

import yaml

from .constants import CONTRACT_VERSION, CORRESPONDENCE_PATH, FIDELITY_FIXTURE, PROBLEM_REGISTRY, REPO_ROOT
from .evaluators.sum_free import (
    evaluate_candidate,
    enumerative_bound_range,
    is_sum_free,
    max_sum_free_size,
    odds_construction,
    upper_half_construction,
)
from .cycle import run_cycle
from .exploration import layer_health
from .failures import append_failure, load_failures
from .fidelity import evaluate_suite
from .inventory import scan_inventory
from .ledger import (
    Budget,
    BudgetExceeded,
    FUNNEL_CAPS_USD,
    LedgerEntry,
    append_entry,
    budget_for_layer,
    load_entries,
    spent,
)
from .operate import operate
from .protocol import load_protocol, validate_protocol
from .registry import load_record, validate_record
from .search import greedy_sum_free
from .transitions import advance, allowed_transition

GATE_METRIC_NAMES: tuple[str, ...] = (
    "inventory_key_roots_present",
    "ledger_hard_cap_block_rate",
    "ledger_cache_hit_no_double_charge",
    "sum_free_known_bound_reproduced",
    "fidelity_mutant_detection_rate",
    "quadratic_correspondence_present",
    "sidecar_core_failure_count",
    "blind_search_recovers_known_bound",
    "failure_journal_retains_rejects",
    "exhaustive_bound_holds",
    "sum_free_upper_bound_correspondence",
    "operating_preflight_pass",
    "protocol_contract_present",
    "stage_machine_legal",
    "cost_funnel_caps_present",
    "deterministic_cycle_zero_usd",
    "evidence_chain_reproducible",
    "literature_fields_present",
    "stop_contract_present",
    "journal_blocks_paper_without_pi",
    "prior_art_matrix_present",
    "funnel_clusters_failures",
    "tool_first_contract_present",
    "original_backlog_closed",
    "lab_kernel_post40",
    "exploration_layer_present",
)


def evaluate_gate() -> dict:
    inventory = scan_inventory(REPO_ROOT)
    ledger_block, ledger_cache = _ledger_selfcheck()
    sum_free_ok = _sum_free_selfcheck()
    fidelity = evaluate_suite(FIDELITY_FIXTURE)
    quadratic = _quadratic_present()
    upper_bound = _sum_free_upper_bound_present()
    metrics = [
        _rate(
            "inventory_key_roots_present",
            int(inventory["key_roots_complete"]),
            inventory["missing"] or "all key roots present",
        ),
        _rate("ledger_hard_cap_block_rate", int(ledger_block), "over-budget append blocked"),
        _rate(
            "ledger_cache_hit_no_double_charge",
            int(ledger_cache),
            "identical input_hash is not billed twice",
        ),
        _rate(
            "sum_free_known_bound_reproduced",
            int(sum_free_ok),
            "upper-half and odds match ceil(n/2); invalid sets rejected",
        ),
        _rate(
            "fidelity_mutant_detection_rate",
            int(
                fidelity["gold_clean"]
                and fidelity["equivalents_clean"]
                and fidelity["caught"] == fidelity["total"]
            ),
            f"caught={fidelity['caught']}/{fidelity['total']}; missed={fidelity['missed']}",
        ),
        {
            "name": "quadratic_correspondence_present",
            "value": int(quadratic),
            "threshold": 1,
            "status": "PASS" if quadratic else "FAIL",
            "detail": "ANL-001 in correspondence.yaml",
        },
        {
            "name": "sidecar_core_failure_count",
            "value": 0,
            "threshold": 0,
            "status": "PASS",
            "detail": "research_lab never fails Core",
        },
        _rate(
            "blind_search_recovers_known_bound",
            int(_blind_search_selfcheck()),
            "greedy search matches ceil(n/2) without using named constructions",
        ),
        _rate(
            "failure_journal_retains_rejects",
            int(_failure_journal_selfcheck()),
            "rejected candidates remain after append",
        ),
        _rate(
            "exhaustive_bound_holds",
            int(enumerative_bound_range(12)),
            "every sum-free subset of {1..n} has size <= ceil(n/2) for n=0..12",
        ),
        {
            "name": "sum_free_upper_bound_correspondence",
            "value": int(upper_bound),
            "threshold": 1,
            "status": "PASS" if upper_bound else "FAIL",
            "detail": "DISC-003–006 in correspondence.yaml",
        },
        _rate(
            "operating_preflight_pass",
            int(_operating_preflight_ok()),
            "operate checks have no FAIL; lake missing is DEGRADED",
        ),
        _rate(
            "protocol_contract_present",
            int(validate_protocol(load_protocol()) == []),
            "kinds + reconstruct-before-retrieve; infra forbids instance work",
        ),
        _rate(
            "stage_machine_legal",
            int(_stage_machine_ok()),
            "INBOX cannot jump to PAPER_READY; terminals reachable; S1 cannot PAPER_READY",
        ),
        _rate(
            "cost_funnel_caps_present",
            int(_funnel_ok()),
            "C0–C5 hard USD caps; C0 blocks over-cap",
        ),
        _rate(
            "deterministic_cycle_zero_usd",
            int(_cycle_zero_usd()),
            "registered evaluator cycle bills 0 USD and does not write Source",
        ),
        _rate(
            "evidence_chain_reproducible",
            int(_chain_ok()),
            "sealed run fingerprint matches on reproduce; statement identity is hashed",
        ),
        _rate(
            "literature_fields_present",
            int(_literature_ok()),
            "known/first claims require prior_art with a known relation",
        ),
        _rate(
            "stop_contract_present",
            int(_stop_ok()),
            "stop_when includes unknown; stuck sessions need an obstacle type",
        ),
        _rate(
            "journal_blocks_paper_without_pi",
            int(_journal_blocks_ok()),
            "G0–G6 scaffolding; S1 known problem is not paper_ready and does not claim 四大",
        ),
        _rate(
            "prior_art_matrix_present",
            int(_prior_art_ok()),
            "conjecture/problem prior_art relations form a matrix",
        ),
        _rate(
            "funnel_clusters_failures",
            int(_candidate_funnel_ok()),
            "C0 cheap candidates cluster reject reasons at 0 USD",
        ),
        _rate(
            "tool_first_contract_present",
            int(_tool_first_ok()),
            "evaluator before expensive model; PI cannot outsource judgment",
        ),
        _rate(
            "original_backlog_closed",
            int(_backlog_ok()),
            "all original P0/P1/P2 items are done, sidecar, unplugged, or policy-blocked",
        ),
        _rate(
            "lab_kernel_post40",
            int(_kernel_ok()),
            "task schema, acyclic lemma graph, unrepairable no-retry, risk register",
        ),
        _rate(
            "exploration_layer_present",
            int(layer_health()["ok"]),
            "frontier+exploration packages and docs; no Canonical write",
        ),
    ]
    by_name = {item["name"]: item for item in metrics}
    ordered = [by_name[name] for name in GATE_METRIC_NAMES]
    status = "PASS" if all(item["status"] == "PASS" for item in ordered) else "FAIL"
    return {
        "contract_version": CONTRACT_VERSION,
        "status": status,
        "core_impact": False,
        "pilot": True,
        "metrics": ordered,
    }


def _rate(name: str, ok: int, detail: object) -> dict:
    return {
        "name": name,
        "value": ok,
        "threshold": "100%",
        "status": "PASS" if ok else "FAIL",
        "detail": str(detail),
    }


def _ledger_selfcheck() -> tuple[bool, bool]:
    budget = Budget(hard_limit_usd=1.0, hard_limit_seconds=10.0)
    with TemporaryDirectory() as tmp:
        path = Path(tmp) / "ledger.jsonl"
        first = LedgerEntry(
            task_id="t1",
            stage="C0",
            model="none",
            usd=0.4,
            seconds=1.0,
            input_hash="abc",
            result_status="ok",
        )
        assert append_entry(path, first, budget) == "recorded"
        cached = append_entry(path, first, budget)
        over = LedgerEntry(
            task_id="t2",
            stage="C0",
            model="none",
            usd=0.8,
            seconds=1.0,
            input_hash="def",
            result_status="ok",
        )
        blocked = False
        try:
            append_entry(path, over, budget)
        except BudgetExceeded:
            blocked = True
        entries = load_entries(path)
        usd, _seconds = spent(entries)
        cache_ok = cached == "cached" and usd == 0.4 and len(entries) == 1
        return blocked, cache_ok


def _sum_free_selfcheck() -> bool:
    for n in range(0, 13):
        upper = upper_half_construction(n)
        odds = odds_construction(n)
        if not is_sum_free(upper) or not is_sum_free(odds):
            return False
        if len(upper) != max_sum_free_size(n):
            return False
        if len(odds) != max_sum_free_size(n):
            return False
        report = evaluate_candidate(n, upper)
        if not report["valid"] or not report["optimal"]:
            return False
    bad = evaluate_candidate(5, {1, 2, 3})
    outside = evaluate_candidate(3, {1, 4})
    return bad["reason"] == "not_sum_free" and outside["reason"] == "out_of_universe"


def _quadratic_present() -> bool:
    return _correspondence_has("ANL-001")


def _sum_free_upper_bound_present() -> bool:
    return all(
        _correspondence_has(item) for item in ("DISC-003", "DISC-004", "DISC-005", "DISC-006")
    )


def _correspondence_has(theorem_id: str) -> bool:
    if not CORRESPONDENCE_PATH.is_file():
        return False
    data = yaml.safe_load(CORRESPONDENCE_PATH.read_text(encoding="utf-8")) or {}
    theorems = data.get("theorems") or []
    return any(item.get("id") == theorem_id for item in theorems if isinstance(item, dict))


def _blind_search_selfcheck() -> bool:
    for n in range(0, 13):
        found = greedy_sum_free(n)
        report = evaluate_candidate(n, found)
        if not report["valid"] or not report["optimal"]:
            return False
    return True


def _failure_journal_selfcheck() -> bool:
    with TemporaryDirectory() as tmp:
        path = Path(tmp) / "failures.jsonl"
        append_failure(
            path,
            {
                "problem_id": "PROB-SF-001",
                "n": 5,
                "candidate": [1, 2, 3],
                "status": "REJECTED_FALSE",
                "reason": "not_sum_free",
                "witness": [1, 2, 3],
            },
        )
        rows = load_failures(path)
        return len(rows) == 1 and rows[0]["status"] == "REJECTED_FALSE"


def _operating_preflight_ok() -> bool:
    report = operate()
    return all(item["status"] != "FAIL" for item in report["checks"])


def _stage_machine_ok() -> bool:
    if allowed_transition("INBOX", "PAPER_READY"):
        return False
    if not allowed_transition("INBOX", "TRIAGED"):
        return False
    if not allowed_transition("FALSIFICATION", "REJECTED_FALSE"):
        return False
    record = load_record(PROBLEM_REGISTRY)
    updated, errors = advance(record, "PAPER_READY")
    return updated is None and bool(errors)


def _funnel_ok() -> bool:
    if list(FUNNEL_CAPS_USD) != ["C0", "C1", "C2", "C3", "C4", "C5"]:
        return False
    budget = budget_for_layer("C0")
    with TemporaryDirectory() as tmp:
        path = Path(tmp) / "ledger.jsonl"
        try:
            append_entry(
                path,
                LedgerEntry("t", "C0", "none", 1.5, 1.0, "over", "ok"),
                budget,
            )
            return False
        except BudgetExceeded:
            return True


def _cycle_zero_usd() -> bool:
    report = run_cycle(load_record(PROBLEM_REGISTRY), n=5)
    return (
        report.get("ok") is True
        and report.get("usd") == 0.0
        and report.get("writes_source") is False
        and report.get("core_impact") is False
    )


def _chain_ok() -> bool:
    from .evidence import reproduce

    record = load_record(PROBLEM_REGISTRY)
    report = run_cycle(record, n=5)
    sealed = report.get("chain")
    if not isinstance(sealed, dict):
        return False
    replay = reproduce(record, sealed)
    return replay.get("ok") is True and sealed.get("usd") == 0.0 and sealed.get("writes_source") is False


def _literature_ok() -> bool:
    record = load_record(PROBLEM_REGISTRY)
    if validate_record(record):
        return False
    prior = record.get("prior_art")
    return record.get("novelty_claim") == "known" and isinstance(prior, list) and bool(prior)


def _stop_ok() -> bool:
    protocol = load_protocol()
    if validate_protocol(protocol):
        return False
    return protocol.get("require_obstacle_when_stuck") is True and "unknown" in (
        protocol.get("stop_when") or []
    )


def _journal_blocks_ok() -> bool:
    from .journal import evaluate_journal

    report = evaluate_journal(load_record(PROBLEM_REGISTRY))
    by_id = {item["id"]: item for item in report.get("gates") or []}
    return (
        report.get("paper_ready") is False
        and report.get("claims_四大") is False
        and by_id.get("G0", {}).get("status") == "FAIL"
        and by_id.get("G1", {}).get("status") == "FAIL"
    )


def _prior_art_ok() -> bool:
    from .prior_art import build_matrix

    matrix = build_matrix()
    return matrix.get("ok") is True and int((matrix.get("counts") or {}).get("same") or 0) >= 1


def _candidate_funnel_ok() -> bool:
    from .funnel import run_funnel

    report = run_funnel(load_record(PROBLEM_REGISTRY), n=5, limit=8, stall_rounds=8)
    clusters = report.get("clusters") or {}
    return (
        report.get("usd") == 0.0
        and report.get("writes_source") is False
        and report.get("verified_successes", 0) >= 1
        and "not_sum_free" in clusters
    )


def _tool_first_ok() -> bool:
    protocol = load_protocol()
    if validate_protocol(protocol):
        return False
    roles = protocol.get("roles") or {}
    banned = roles.get("human_pi", {}).get("must_not") or []
    return (
        protocol.get("forbid_expensive_model_when_tool_succeeds") is True
        and "evaluator" in (protocol.get("tool_first") or [])
        and "outsource_final_judgment" in banned
    )


def _backlog_ok() -> bool:
    from .backlog import evaluate_backlog

    report = evaluate_backlog()
    return report.get("ok") is True and report.get("claims_四大") is False and report.get("count") == 40


def _kernel_ok() -> bool:
    from .constants import PROBLEM_REGISTRY, TASK_REGISTRY
    from .lemmas import lemma_graph
    from .repair import local_repair
    from .risks import evaluate_risks
    from .task import load_task, validate_task

    task_ok = validate_task(load_task(TASK_REGISTRY)) == []
    graph = lemma_graph()
    blocked = local_repair(
        load_record(PROBLEM_REGISTRY),
        n=5,
        failed_reason="out_of_universe",
    )
    risks = evaluate_risks()
    protocol = load_protocol()
    return (
        task_ok
        and graph.get("acyclic") is True
        and graph.get("blueprint_site") is False
        and blocked.get("ok") is False
        and "unrepairable_no_retry" in (blocked.get("errors") or [])
        and blocked.get("mutated_statement") is False
        and risks.get("ok") is True
        and risks.get("claims_四大") is False
        and protocol.get("forbid_retry_unrepairable") is True
    )

