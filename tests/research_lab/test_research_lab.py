from pathlib import Path

from tools.research_lab.constants import REPO_ROOT
from tools.research_lab.doctor import doctor
from tools.research_lab.evaluators.sum_free import (
    evaluate_candidate,
    is_sum_free,
    max_sum_free_size,
    odds_construction,
    upper_half_construction,
)
from tools.research_lab.failures import append_failure, load_failures
from tools.research_lab.fidelity import detect_mutants, evaluate_suite, load_suite
from tools.research_lab.gate import GATE_METRIC_NAMES, evaluate_gate
from tools.research_lab.inventory import scan_inventory
from tools.research_lab.ledger import Budget, BudgetExceeded, LedgerEntry, append_entry, load_entries, spent
from tools.research_lab.registry import validate_record
from tools.research_lab.search import greedy_sum_free


def test_inventory_sees_key_roots():
    report = scan_inventory(REPO_ROOT)
    assert report["key_roots_complete"] is True
    assert report["file_total"] > 0
    assert ".lean" in report["file_counts_by_suffix"]


def test_inventory_skips_missing_root(tmp_path: Path):
    report = scan_inventory(tmp_path)
    assert report["key_roots_complete"] is False
    assert "02_题目库" in report["missing"]


def test_ledger_blocks_over_budget(tmp_path: Path):
    path = tmp_path / "ledger.jsonl"
    budget = Budget(hard_limit_usd=1.0, hard_limit_seconds=5.0)
    first = LedgerEntry("t1", "C0", "none", 0.6, 1.0, "h1", "ok")
    assert append_entry(path, first, budget) == "recorded"
    over = LedgerEntry("t2", "C0", "none", 0.6, 1.0, "h2", "ok")
    try:
        append_entry(path, over, budget)
        raise AssertionError("expected BudgetExceeded")
    except BudgetExceeded:
        pass
    assert len(load_entries(path)) == 1
    usd, _seconds = spent(load_entries(path))
    assert usd == 0.6


def test_ledger_cache_does_not_double_charge(tmp_path: Path):
    path = tmp_path / "ledger.jsonl"
    budget = Budget(hard_limit_usd=10.0, hard_limit_seconds=50.0)
    entry = LedgerEntry("t1", "C0", "none", 2.0, 3.0, "same", "ok")
    assert append_entry(path, entry, budget) == "recorded"
    assert append_entry(path, entry, budget) == "cached"
    usd, seconds = spent(load_entries(path))
    assert usd == 2.0
    assert seconds == 3.0


def test_sum_free_reproduces_known_bound():
    for n in range(0, 16):
        upper = upper_half_construction(n)
        odds = odds_construction(n)
        assert is_sum_free(upper)
        assert is_sum_free(odds)
        assert len(upper) == max_sum_free_size(n)
        assert len(odds) == max_sum_free_size(n)
        assert evaluate_candidate(n, upper)["optimal"] is True
    assert evaluate_candidate(5, {1, 2, 3})["reason"] == "not_sum_free"
    assert evaluate_candidate(3, {4})["reason"] == "out_of_universe"


def test_fidelity_suite_catches_p001_mutants():
    suite = Path(__file__).parent / "fixtures" / "fidelity" / "p001_suite.yaml"
    report = evaluate_suite(suite)
    assert report["gold_clean"] is True
    assert report["equivalents_clean"] is True
    assert report["caught"] == report["total"]
    assert report["total"] >= 6
    assert report["missed"] == []
    assert len(load_suite(suite)["equivalents"]) >= 20
    assert detect_mutants("The maximum of p x - e^x is always attained.") == ["max_for_sup_exp"]
    assert "legendre_always_reparam" in detect_mutants(
        "Every Legendre transform is only a reparameterization of the same graph."
    )


def test_blind_search_recovers_known_bound_without_named_constructions():
    import tools.research_lab.search as search_mod

    source = Path(search_mod.__file__).read_text(encoding="utf-8")
    assert "max_sum_free_size" not in source
    assert "upper_half" not in source
    assert "odds_construction" not in source
    for n in range(0, 16):
        found = greedy_sum_free(n)
        report = evaluate_candidate(n, found)
        assert report["valid"] is True
        assert report["optimal"] is True
        assert report["size"] == max_sum_free_size(n)


def test_failure_journal_keeps_rejects(tmp_path: Path):
    path = tmp_path / "failures.jsonl"
    bad = evaluate_candidate(5, {1, 2, 3})
    append_failure(
        path,
        {
            "problem_id": "PROB-SF-001",
            "n": 5,
            "candidate": [1, 2, 3],
            "status": "REJECTED_FALSE",
            "reason": bad["reason"],
            "witness": bad["witness"],
        },
    )
    rows = load_failures(path)
    assert len(rows) == 1
    witness = rows[0]["witness"]
    assert witness[0] + witness[1] == witness[2]
    assert witness[2] in {1, 2, 3}


def test_explore_loads_failure_journal_and_search_is_lexical(tmp_path: Path):
    from tools.research_lab.cli import main
    from tools.research_lab.exploration import explore_briefing, search_failures
    from tools.research_lab.failures import as_memory_rows, lookup_failures

    path = tmp_path / "failures.jsonl"
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
    assert lookup_failures(rows, "not_sum_free")
    assert lookup_failures(rows, "compactness") == []
    memory = as_memory_rows(rows)
    assert memory[0]["not_a_theorem"] is True
    report = explore_briefing(failure_path=path)
    assert report["counts"]["journal"] == 1
    assert any(item["id"].startswith("journal:") for item in report["failures"])
    hits = search_failures("not_sum_free", failure_path=path)
    assert hits["embeddings"] is False
    assert hits["wrote_canonical"] is False
    assert hits["count"] >= 1
    assert main(["search-failure", "--query", "not_sum_free", "--failures", str(path)]) == 0
    assert main(["explore", "--failures", str(path)]) == 0


def test_exploration_index_is_read_only():
    from tools.qt_workbench.workspace import get_object, list_objects
    from tools.research_lab.exploration import exploration_index, lifecycle_state

    assert lifecycle_state("FALSIFICATION") == "challenged"
    assert lifecycle_state("CANDIDATE_SURVIVED") == "tested"
    assert lifecycle_state("REJECTED_FALSE") == "rejected"
    assert lifecycle_state("PAPER_READY") == "supported"
    rows = list_objects(REPO_ROOT, "exploration")
    assert rows[0]["id"] == "overview"
    assert any(str(row.get("group") or "").startswith("正在探索") for row in rows)
    overview = get_object(REPO_ROOT, "exploration", "overview")
    assert overview is not None
    assert "禁止自动 Promotion" in overview["body"]
    assert get_object(REPO_ROOT, "exploration", "../元数据规范.md") is None
    assert all("body" in row for row in exploration_index())
    assert get_object(REPO_ROOT, "exploration", "reasoning")["kind_label"] == "推理图"
    assert "proves_theorem: false" in get_object(REPO_ROOT, "exploration", "reasoning")["body"]


def test_reasoning_graph_excludes_file_order_and_does_not_prove(tmp_path: Path):
    from tools.research_lab.lemmas import lemma_graph, reasoning_graph

    path = tmp_path / "correspondence.yaml"
    path.write_text(
        "theorems:\n"
        "  - id: A\n"
        "    natural_language: length bound\n"
        "    lean_file: X.lean\n"
        "    depends_on: [B]\n"
        "  - id: B\n"
        "    natural_language: odds are sum-free\n"
        "    lean_file: X.lean\n",
        encoding="utf-8",
    )
    reasoning = reasoning_graph(path)
    assert reasoning["proves_theorem"] is False
    assert reasoning["file_order_excluded"] is True
    kinds = {row["id"]: row["kind"] for row in reasoning["nodes"]}
    assert kinds == {"A": "conclusion", "B": "premise"}
    assert reasoning["edges"] == [
        {"id": "requires:A:B", "type": "requires", "source": "A", "target": "B"}
    ]
    lab = lemma_graph(path)
    assert any(edge["from"] == "A" and edge["to"] == "B" for edge in lab["edges"])


def test_explore_id_lookup_is_read_only(capsys):
    from tools.research_lab.cli import main
    from tools.research_lab.exploration import lookup_index

    assert lookup_index("../元数据规范.md") is None
    item = lookup_index("reasoning")
    assert item is not None
    assert item["group"] == "推理图"
    assert "proves_theorem: false" in item["body"]
    assert main(["explore", "--id", "overview", "--format", "markdown"]) == 0
    out = capsys.readouterr().out
    assert "禁止自动 Promotion" in out
    assert main(["explore", "--id", "../secret"]) == 1


def test_lab_map_covers_registry_and_never_promotes():
    from tools.research_lab.lab_map import load_lab_map, lifecycle_state, maps_to_promotion, pipeline_stage
    from tools.research_lab.registry import STAGES, TERMINAL_STAGES

    data = load_lab_map()
    assert data["never_maps_to_promotion"] is True
    assert maps_to_promotion() is False
    for stage in (*STAGES, *TERMINAL_STAGES):
        assert stage in data["lifecycle"]
        assert stage in data["pipeline"]
        assert data["pipeline"][stage] != "promotion"
    assert lifecycle_state("FALSIFICATION") == "challenged"
    assert pipeline_stage("FALSIFICATION") == "experiment"
    assert pipeline_stage("CANDIDATE_SURVIVED") == "critique"
    assert pipeline_stage("PAPER_READY") == "verification"


def test_explore_markdown_format_is_read_only(capsys):
    from tools.research_lab.cli import main

    assert main(["explore", "--format", "markdown"]) == 0
    out = capsys.readouterr().out
    assert "## 五问" in out
    assert "pipeline=" in out or "pipeline=`" in out
    assert "写入 Canonical：否" in out
    assert "禁止自动 Promotion" in out
    assert "## 推理图" in out
    assert "proves_theorem=false" in out
    assert "## 模式" in out


def test_registered_sum_free_problem_is_known_not_first():
    from tools.research_lab.constants import PROBLEM_REGISTRY
    from tools.research_lab.registry import load_record

    record = load_record(PROBLEM_REGISTRY)
    assert validate_record(record) == []
    assert record["novelty_claim"] == "known"
    assert record["success_level"] == "S1"
    decls = record.get("lean_decls") or []
    assert "MathAILab.Research.odds_length" in decls
    assert "MathAILab.Research.sum_free_length_le" in decls


def test_registry_rejects_first_without_expert():
    errors = validate_record(
        {
            "id": "PROB-0001",
            "title": "sum-free subsets of [n]",
            "track": "A",
            "stage": "TRIAGED",
            "evaluator": "sum_free",
            "success_level": "S1",
            "novelty_claim": "first",
        }
    )
    assert any("expert_signoff" in item for item in errors)
    ok = validate_record(
        {
            "id": "PROB-0001",
            "title": "sum-free subsets of [n]",
            "track": "C",
            "stage": "FALSIFICATION",
            "evaluator": "sum_free",
            "success_level": "S1",
        }
    )
    assert ok == []


def test_gate_and_doctor():
    report = evaluate_gate()
    names = [item["name"] for item in report["metrics"]]
    assert names == list(GATE_METRIC_NAMES)
    assert report["status"] == "PASS"
    assert report["core_impact"] is False
    assert report["pilot"] is True
    doc = doctor()
    assert doc["status"] == "PASS"
    assert doc["core_impact"] is False
    assert doc["exploration_layer_ok"] is True


def test_cli():
    from tools.research_lab.cli import main

    assert main(["doctor"]) == 0
    assert main(["gate"]) == 0
    assert main(["inventory"]) == 0
    assert main(["evaluate-sum-free", "--n", "5", "--set", "3,4,5"]) == 0
    assert main(["evaluate-sum-free", "--n", "5", "--set", "1,2,3"]) == 1
    assert main(["search-sum-free", "--n", "10"]) == 0
    assert main(["check-problem"]) == 0
    assert main(["verify"]) == 0
    assert main(["operate"]) == 0
    assert main(["explore"]) == 0
    assert main(["protocol"]) == 0
    assert main(["route", "--kind", "infra"]) == 0
    assert main(["route", "--kind", "modeling"]) == 0
    session_ok = Path(__file__).parent / "fixtures" / "sessions" / "infra_ok.yaml"
    session_bad = Path(__file__).parent / "fixtures" / "sessions" / "infra_emits_instance.yaml"
    assert main(["check-session", "--file", str(session_ok)]) == 0
    assert main(["check-session", "--file", str(session_bad)]) == 1
    assert main(["list-problems"]) == 0
    assert main(["list-conjectures"]) == 0
    assert main(["cycle", "--n", "5"]) == 0
    from tools.research_lab.constants import PROBLEM_REGISTRY

    assert main(["advance", "--file", str(PROBLEM_REGISTRY), "--to", "PAPER_READY"]) == 1
    assert main(["advance", "--file", str(PROBLEM_REGISTRY), "--to", "CANDIDATE_SURVIVED"]) == 0


def test_enumerative_bound_small_n():
    from tools.research_lab.evaluators.sum_free import enumerative_bound_holds, enumerative_bound_range

    assert enumerative_bound_range(8) is True
    assert enumerative_bound_holds(0) is True
    oversized = evaluate_candidate(5, {1, 2, 3})
    assert oversized["valid"] is False


def test_verify_report_is_sidecar():
    from tools.research_lab.verify import REQUIRED_CORRESPONDENCE_IDS, verify

    report = verify()
    assert report["core_impact"] is False
    assert report["status"] in {"PASS", "DEGRADED"}
    names = [item["name"] for item in report["checks"]]
    assert names == [
        "problem_registry",
        "known_constructions",
        "exhaustive_bound",
        "correspondence",
        "lean_scan",
        "lake_build",
    ]
    by_name = {item["name"]: item for item in report["checks"]}
    assert by_name["problem_registry"]["status"] == "PASS"
    assert by_name["known_constructions"]["status"] == "PASS"
    assert by_name["exhaustive_bound"]["status"] == "PASS"
    assert by_name["correspondence"]["status"] == "PASS"
    assert by_name["lean_scan"]["status"] == "PASS"
    assert by_name["lake_build"]["status"] in {"PASS", "DEGRADED"}
    assert "DISC-006" in REQUIRED_CORRESPONDENCE_IDS


def _session(name: str) -> dict:
    import yaml

    path = Path(__file__).parent / "fixtures" / "sessions" / name
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def test_protocol_encodes_kinds_and_reconstruct_before_retrieve():
    from tools.research_lab.protocol import KIND_IDS, load_protocol, validate_protocol

    protocol = load_protocol()
    assert validate_protocol(protocol) == []
    assert set(KIND_IDS) == {
        "exercise",
        "research",
        "modeling",
        "experiment",
        "literature",
        "review",
        "infra",
    }
    step_ids = [item["id"] for item in protocol["proof_steps"]]
    assert step_ids.index("reconstruct") < step_ids.index("retrieve")
    assert protocol["kinds"]["infra"]["forbid_instance_work"] is True
    assert protocol["kinds"]["modeling"]["pipeline"] == "model_select"
    assert protocol["layers"] == ["canonical", "universe", "frontier", "exploration"]
    assert protocol["promotion"]["automatic"] is False
    assert protocol["promotion"]["exploration_cannot_write_canonical"] is True
    assert protocol["failure_memory"]["embeddings"] is False
    assert protocol["exploration"]["reasoning_proves_theorem"] is False
    assert protocol["exploration"]["pattern_is_not_theorem"] is True
    assert protocol["exploration"]["notebook_is_canonical"] is False
    assert protocol["exploration"]["strategy_is_proof"] is False
    assert protocol["exploration"]["evolution_proves_theorem"] is False
    assert protocol["exploration"]["catalog_search"] == "lexical"
    assert protocol["exploration"]["embeddings"] is False
    assert protocol["frontier"]["catalog"] == "erdosproblems"
    assert protocol["frontier"]["scope"] == "additive_combinatorics"
    assert protocol["frontier"]["vendor"] == "vendor/erdosproblems"
    assert protocol["frontier"]["pin"] == "5308c57c700559416b9f205df274b136784203e7"
    assert protocol["frontier"]["source"] == "vendor/erdosproblems/data/problems.yaml"
    assert protocol["frontier"]["full_tree"] is True
    assert protocol["frontier"]["writes_canonical"] is False
    assert protocol["frontier"]["not_a_theorem"] is True
    assert protocol["frontier"]["network"] is False
    assert protocol["promotion"]["pending_blocks_promotion"] is True
    assert protocol["discovery_pipeline"][-1] == "promotion"
    assert "promotion" not in protocol["discovery_pipeline"][:-1]
    assert "mutate_statement" in protocol["roles"]["prover"]["must_not"]


def test_route_and_session_checks():
    from tools.research_lab.protocol import evaluate_session, route

    infra = route("infra")
    assert infra["pipeline"] == "operating"
    assert infra["forbid_instance_work"] is True
    assert "P00" not in infra["drop"]
    modeling = route("modeling")
    assert modeling["pipeline"] == "model_select"
    assert evaluate_session(_session("research_ok.yaml"))["ok"] is True
    bad_retrieve = evaluate_session(_session("retrieve_before_reconstruct.yaml"))
    assert bad_retrieve["ok"] is False
    assert "retrieve_before_reconstruct" in bad_retrieve["errors"]
    bad_model = evaluate_session(_session("modeling_as_proof.yaml"))
    assert bad_model["ok"] is False
    assert "modeling_must_not_use_proof_pipeline" in bad_model["errors"]
    bad_infra = evaluate_session(_session("infra_emits_instance.yaml"))
    assert bad_infra["ok"] is False
    assert "infra_must_not_emit_instance_work" in bad_infra["errors"]
    assert evaluate_session(_session("infra_ok.yaml"))["ok"] is True


def test_operate_is_operating_layer_not_instance_work():
    from tools.research_lab import operate as operate_mod
    from tools.research_lab.operate import operate

    source = Path(operate_mod.__file__).read_text(encoding="utf-8")
    assert "sum_free" not in source
    assert "QuadraticConjugate" not in source
    assert "PROB-SF" not in source
    report = operate()
    assert report["core_impact"] is False
    assert report["status"] in {"PASS", "DEGRADED"}
    assert report["instance_calibration_required"] is False
    assert report["writes_source"] is False
    assert "new_problem_on_infra_task" in report["forbidden"]
    names = [item["name"] for item in report["checks"]]
    assert "protocol" in names
    assert "inventory" in names
    assert "frozen_schema_present" in names
    assert "lean_sidecar" in names
    assert "exploration_layer" in names
    by_name = {item["name"]: item for item in report["checks"]}
    assert by_name["protocol"]["status"] == "PASS"
    assert by_name["inventory"]["status"] == "PASS"
    assert by_name["lean_sidecar"]["status"] in {"READY", "DEGRADED"}
    assert by_name["lean_sidecar"]["status"] != "FAIL"
    assert by_name["lockfile_present"]["status"] == "PASS"
    assert by_name["exploration_layer"]["status"] == "PASS"
    assert "json_sync=true" in by_name["exploration_layer"]["detail"]
    assert "5308c57" in by_name["exploration_layer"]["detail"]
    assert "yaml=1217" in by_name["exploration_layer"]["detail"]


def test_explore_briefing_does_not_write_canonical():
    from tools.research_lab.exploration import briefing_markdown, explore_briefing, layer_health
    from tools.research_lab.protocol import evaluate_session

    health = layer_health()
    assert health["ok"] is True
    assert health["writes_source"] is False
    report = explore_briefing()
    assert report["wrote_canonical"] is False
    assert report["promotion_authorized"] is False
    assert report["layer"] == "exploration"
    assert all(item.get("not_a_theorem") is True for item in report["exploring"])
    assert "what_we_know" in report["answers"]
    markdown = briefing_markdown(report)
    assert "禁止自动 Promotion" in markdown
    assert "## 失败记忆" in markdown
    by_id = {item["id"]: item for item in report["exploring"]}
    assert by_id["PROB-SF-001"]["state"] == "challenged"
    assert by_id["PROB-SF-001"]["pipeline"] == "experiment"
    assert by_id["CONJ-SF-001"]["state"] == "tested"
    assert by_id["CONJ-SF-001"]["pipeline"] == "critique"
    assert report["known"]["lemma_graph"]["not_a_theorem"] is True
    assert report["reasoning"]["proves_theorem"] is False
    assert report["reasoning"]["file_order_excluded"] is True
    assert report["counts"]["reasoning_edges"] >= 3
    assert {edge["id"] for edge in report["reasoning"]["edges"]} >= {
        "requires:ALG-004:ALG-002",
        "requires:ALG-004:ALG-003",
        "requires:ANL-004:ANL-001",
    }
    assert report["counts"]["patterns"] >= 3
    assert all(item.get("not_a_theorem") is True for item in report["patterns"])
    blocked = evaluate_session(_session("explore_writes_canonical.yaml"))
    assert blocked["ok"] is False
    assert "exploration_cannot_write_canonical" in blocked["errors"]
    ai_promote = evaluate_session(_session("explore_ai_promote.yaml"))
    assert ai_promote["ok"] is False
    assert "ai_cannot_promote" in ai_promote["errors"]


def test_stage_machine_and_funnel_and_cycle(tmp_path: Path):
    from tools.research_lab.conjecture import load_all_conjectures, validate_conjecture
    from tools.research_lab.constants import PROBLEM_REGISTRY
    from tools.research_lab.cycle import run_cycle
    from tools.research_lab.inventory import write_inventory
    from tools.research_lab.ledger import BudgetExceeded, FUNNEL_CAPS_USD, LedgerEntry, append_entry, budget_for_layer
    from tools.research_lab.registry import load_record
    from tools.research_lab.transitions import advance, allowed_transition

    assert allowed_transition("INBOX", "TRIAGED") is True
    assert allowed_transition("INBOX", "PAPER_READY") is False
    assert allowed_transition("FALSIFICATION", "REJECTED_KNOWN") is True
    record = load_record(PROBLEM_REGISTRY)
    updated, errors = advance(record, "PAPER_READY")
    assert updated is None
    assert errors
    next_ok, next_errors = advance(record, "CANDIDATE_SURVIVED")
    assert next_ok is not None
    assert next_errors == []
    assert "C0" in FUNNEL_CAPS_USD
    try:
        append_entry(
            tmp_path / "ledger.jsonl",
            LedgerEntry("t", "C0", "none", 9.0, 1.0, "x", "ok"),
            budget_for_layer("C0"),
        )
        raise AssertionError("expected BudgetExceeded")
    except BudgetExceeded:
        pass
    conjectures = load_all_conjectures()
    assert conjectures
    assert all(validate_conjecture(item) == [] for item in conjectures)
    first = validate_conjecture(
        {
            "id": "CONJ-X",
            "problem_id": "PROB-SF-001",
            "statement": "first",
            "status": "INBOX",
            "novelty_claim": "first",
        }
    )
    assert any("expert_signoff" in item for item in first)
    assert any("prior_art" in item for item in first)
    try:
        write_inventory({"ok": True}, tmp_path / "项目进度.md")
        raise AssertionError("expected refuse")
    except ValueError:
        pass
    out = tmp_path / "inventory.json"
    write_inventory({"ok": True, "file_total": 1}, out)
    assert out.is_file()
    cycle = run_cycle(record, n=5, ledger_path=tmp_path / "c.jsonl", budget=budget_for_layer("C0"))
    assert cycle["ok"] is True
    assert cycle["usd"] == 0.0
    assert cycle["writes_source"] is False
    rejected = run_cycle(record, n=5, values={1, 2, 3}, failure_path=tmp_path / "f.jsonl")
    assert rejected["ok"] is False
    from tools.research_lab.failures import load_failures

    assert load_failures(tmp_path / "f.jsonl")


def test_prover_cannot_mutate_statement():
    from tools.research_lab.protocol import evaluate_session, load_protocol

    protocol = load_protocol()
    assert "mutate_statement" in protocol["roles"]["prover"]["must_not"]
    report = evaluate_session(_session("prover_mutates_statement.yaml"))
    assert report["ok"] is False
    assert "role_prover_must_not_mutate_statement" in report["errors"]


def test_stop_contract_and_literature_role():
    from tools.research_lab.protocol import evaluate_session, load_protocol, validate_protocol

    protocol = load_protocol()
    assert validate_protocol(protocol) == []
    assert protocol.get("require_obstacle_when_stuck") is True
    assert "unknown" in (protocol.get("stop_when") or [])
    stuck = evaluate_session(_session("stuck_without_obstacle.yaml"))
    assert stuck["ok"] is False
    assert "stuck_without_obstacle" in stuck["errors"]
    proved_stuck = evaluate_session(_session("claimed_proved_while_stuck.yaml"))
    assert proved_stuck["ok"] is False
    assert "claimed_proved_while_stuck" in proved_stuck["errors"]
    literature = evaluate_session(_session("literature_declares_first.yaml"))
    assert literature["ok"] is False
    assert "role_literature_must_not_declare_first_from_abstract" in literature["errors"]


def test_known_problem_requires_prior_art():
    from tools.research_lab.constants import PROBLEM_REGISTRY
    from tools.research_lab.registry import load_record, validate_record

    record = load_record(PROBLEM_REGISTRY)
    assert record["novelty_claim"] == "known"
    assert record.get("prior_art")
    assert validate_record(record) == []
    missing = dict(record)
    missing.pop("prior_art", None)
    errors = validate_record(missing)
    assert any("prior_art" in item for item in errors)


def test_evidence_chain_reproduces_and_refuses_progress_page(tmp_path):
    from tools.research_lab.cli import main
    from tools.research_lab.constants import PROBLEM_REGISTRY
    from tools.research_lab.cycle import run_cycle
    from tools.research_lab.evidence import append_chain, load_chain, reproduce, seal_run, statement_hash
    from tools.research_lab.registry import load_record

    record = load_record(PROBLEM_REGISTRY)
    first = run_cycle(record, n=5)
    assert first["ok"] is True
    assert first["usd"] == 0.0
    assert first["n"] == 5
    sealed = first.get("chain") or seal_run(record, first)
    assert sealed["statement_hash"] == statement_hash(record)
    assert sealed["writes_source"] is False
    assert sealed["usd"] == 0.0
    replay = reproduce(record, sealed)
    assert replay["ok"] is True
    assert replay["sealed"]["run_fingerprint"] == sealed["run_fingerprint"]
    mutated = dict(record)
    mutated["title"] = "a different statement"
    broken = reproduce(mutated, sealed)
    assert broken["ok"] is False
    chain_path = tmp_path / "chain.jsonl"
    append_chain(chain_path, sealed)
    rows = load_chain(chain_path)
    assert len(rows) == 1
    try:
        append_chain(tmp_path / "项目进度.md", sealed)
        raise AssertionError("expected refuse")
    except ValueError:
        pass
    assert main(["reproduce", "--file", str(chain_path), "--problem", str(PROBLEM_REGISTRY)]) == 0


def test_journal_gates_block_paper_ready_without_human_pi():
    from tools.research_lab.constants import PROBLEM_REGISTRY
    from tools.research_lab.journal import JOURNAL_GATES, evaluate_journal
    from tools.research_lab.registry import load_record
    from tools.research_lab.transitions import advance

    record = load_record(PROBLEM_REGISTRY)
    report = evaluate_journal(record)
    assert report["claims_四大"] is False
    assert report["paper_ready"] is False
    assert report["writes_source"] is False
    names = [item["id"] for item in report["gates"]]
    assert names == list(JOURNAL_GATES)
    by_id = {item["id"]: item for item in report["gates"]}
    assert by_id["G0"]["status"] == "FAIL"
    assert by_id["G1"]["status"] == "FAIL"
    assert by_id["G5"]["status"] == "FAIL"
    proven = dict(record)
    proven["stage"] = "PROVED_FORMAL"
    proven["success_level"] = "S3"
    updated, errors = advance(proven, "EXTERNAL_REVIEWED")
    assert updated is None
    assert any("human_pi" in item for item in errors)
    proven["human_pi_signoff"] = True
    proven["importance_rationale"] = "demo only"
    moved, moved_errors = advance(proven, "EXTERNAL_REVIEWED")
    assert moved is not None
    assert moved_errors == []
    paper, paper_errors = advance(moved, "PAPER_READY")
    assert paper is None
    assert paper_errors


def test_prior_art_matrix_and_funnel_and_tool_first():
    from tools.research_lab.cli import main
    from tools.research_lab.constants import PROBLEM_REGISTRY
    from tools.research_lab.funnel import run_funnel
    from tools.research_lab.prior_art import build_matrix
    from tools.research_lab.protocol import evaluate_session, load_protocol, validate_protocol
    from tools.research_lab.registry import load_record

    protocol = load_protocol()
    assert validate_protocol(protocol) == []
    assert "evaluator" in (protocol.get("tool_first") or [])
    assert protocol.get("forbid_expensive_model_when_tool_succeeds") is True
    assert "outsource_final_judgment" in protocol["roles"]["human_pi"]["must_not"]
    pi = evaluate_session(_session("pi_outsources.yaml"))
    assert pi["ok"] is False
    assert "role_human_pi_must_not_outsource_final_judgment" in pi["errors"]
    model = evaluate_session(_session("model_after_tool.yaml"))
    assert model["ok"] is False
    assert "model_after_tool_success" in model["errors"]
    matrix = build_matrix()
    assert matrix["ok"] is True
    assert matrix["writes_source"] is False
    assert matrix["counts"]["same"] >= 1
    record = load_record(PROBLEM_REGISTRY)
    funnel = run_funnel(record, n=5, limit=8, stall_rounds=8)
    assert funnel["usd"] == 0.0
    assert funnel["writes_source"] is False
    assert funnel["layer"] == "C0"
    assert funnel["attempts"] >= 2
    assert "not_sum_free" in funnel["clusters"]
    assert funnel["verified_successes"] >= 1
    assert funnel["cost_adjusted_success"] is None
    assert main(["journal"]) == 1
    assert main(["prior-art-matrix"]) == 0
    assert main(["funnel", "--n", "5", "--limit", "6"]) == 0


def test_original_backlog_closeout(tmp_path: Path):
    from tools.research_lab.adapters import invoke, may_expand_budget
    from tools.research_lab.backlog import ITEMS, c5_blocked_without_pi, evaluate_backlog
    from tools.research_lab.cli import main
    from tools.research_lab.closeout import paper_checklists, write_sidecar
    from tools.research_lab.constants import PROBLEM_REGISTRY
    from tools.research_lab.evaluators.sum_free import evaluate_candidate, max_sum_free_size
    from tools.research_lab.funnel import cheap_candidates
    from tools.research_lab.pipeline import run_pipeline
    from tools.research_lab.premises import retrieve_premises
    from tools.research_lab.protocol import load_protocol, validate_protocol
    from tools.research_lab.registry import load_record
    from tools.research_lab.search import greedy_sum_free
    from tools.research_lab.tactics import cache_proof_state, load_proof_cache, tactic_baseline

    protocol = load_protocol()
    assert validate_protocol(protocol) == []
    assert protocol["domain"] == "additive_combinatorics"
    assert protocol["forbid_unscoped_mathematics"] is True
    report = evaluate_backlog()
    assert report["count"] == 40
    assert len(ITEMS) == 40
    assert report["ok"] is True
    assert report["failed"] == []
    assert report["claims_四大"] is False
    assert all(item["resolution"] != "missing" for item in report["items"])
    assert len(cheap_candidates(8, limit=100)) >= 100
    papers = paper_checklists()
    assert papers["ok"] is True
    assert papers["filled"] is False
    assert papers["claims_四大"] is False
    assert tactic_baseline()["model"] is None
    cache_path = tmp_path / "proof.jsonl"
    assert cache_proof_state(cache_path, "abc", {"goal": "n"}) == "recorded"
    assert cache_proof_state(cache_path, "abc", {"goal": "n"}) == "cached"
    assert len(load_proof_cache(cache_path)) == 1
    premises = retrieve_premises("sum-free list")
    assert premises["candidate"] is True
    assert premises["is_answer"] is False
    assert invoke("frontier_llm")["called"] is False
    assert invoke("sat_smt")["status"] == "UNPLUGGED"
    assert may_expand_budget("C5", {}) is False
    assert c5_blocked_without_pi() is True
    for n in (18, 21):
        found = greedy_sum_free(n)
        hold = evaluate_candidate(n, found)
        assert hold["optimal"] is True
        assert hold["size"] == max_sum_free_size(n)
    sidecar = tmp_path / "inventory_progress.md"
    write_sidecar(sidecar, {"root": "x", "file_total": 1, "present": ["tools"], "missing": []})
    body = sidecar.read_text(encoding="utf-8")
    assert "derived inventory sidecar" in body.lower()
    assert "does not record project judgment" in body.lower()
    try:
        write_sidecar(tmp_path / "项目进度.md", {"root": "x", "file_total": 0, "present": [], "missing": []})
        raise AssertionError("expected refuse")
    except ValueError:
        pass
    pipe = run_pipeline(load_record(PROBLEM_REGISTRY), n=5)
    assert pipe["prefect"] is False
    assert pipe["scheduler"] == "local_sequential"
    assert pipe["writes_source"] is False
    assert pipe["journal"]["claims_四大"] is False
    source = Path(__file__).resolve().parents[2] / "tools" / "research_lab" / "adapters.py"
    text = source.read_text(encoding="utf-8")
    assert "http" not in text.lower()
    assert "openai" not in text.lower()
    assert main(["backlog"]) == 0
    assert main(["review-statements"]) == 0
    assert main(["recipe"]) == 0
    assert main(["adapters"]) == 0
    assert main(["pipeline", "--n", "5"]) == 0
    assert main(["retrieve", "--query", "sum-free list"]) == 0


def test_lab_kernel_task_lemmas_repair_and_risks(tmp_path: Path):
    from tools.research_lab.cli import main
    from tools.research_lab.constants import PROBLEM_REGISTRY
    from tools.research_lab.cost_report import cost_report
    from tools.research_lab.lemmas import lemma_graph
    from tools.research_lab.ledger import Budget, LedgerEntry, append_entry
    from tools.research_lab.protocol import load_protocol, validate_protocol
    from tools.research_lab.registry import load_record
    from tools.research_lab.repair import local_repair
    from tools.research_lab.risks import evaluate_risks
    from tools.research_lab.task import load_task, validate_task
    from tools.research_lab.constants import TASK_REGISTRY

    protocol = load_protocol()
    assert validate_protocol(protocol) == []
    assert protocol["forbid_retry_unrepairable"] is True
    assert "treat_fluency_as_correctness" in protocol["roles"]["strategy"]["must_not"]
    assert validate_task(load_task(TASK_REGISTRY)) == []
    graph = lemma_graph()
    assert graph["ok"] is True
    assert graph["acyclic"] is True
    assert graph["blueprint_site"] is False
    assert "DISC-006" in graph["nodes"]
    record = load_record(PROBLEM_REGISTRY)
    blocked = local_repair(record, n=5, failed_reason="out_of_universe")
    assert blocked["ok"] is False
    assert "unrepairable_no_retry" in blocked["errors"]
    assert blocked["mutated_statement"] is False
    fixed = local_repair(record, n=5, failed_reason="not_sum_free")
    assert fixed["ok"] is True
    assert fixed["mutated_statement"] is False
    assert fixed["usd"] == 0.0
    risks = evaluate_risks(record)
    assert risks["ok"] is True
    assert risks["claims_四大"] is False
    ledger = tmp_path / "ledger.jsonl"
    append_entry(
        ledger,
        LedgerEntry("t", "C0", "none", 0.0, 1.0, "k1", "ok"),
        Budget(1.0, 10.0),
    )
    summary = cost_report(ledger)
    assert summary["usd"] == 0.0
    assert summary["cost_adjusted_success"] is None
    assert summary["verified_successes"] == 1
    assert main(["check-task"]) == 0
    assert main(["lemma-graph"]) == 0
    assert main(["repair", "--reason", "out_of_universe"]) == 1
    assert main(["repair", "--reason", "not_sum_free", "--n", "5"]) == 0
    assert main(["risks"]) == 0
    assert main(["cost-report"]) == 0


