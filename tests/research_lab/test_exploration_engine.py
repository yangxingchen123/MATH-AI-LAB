from pathlib import Path

from tools.research_lab.cli import main
from tools.research_lab.exploration import (
    explore_briefing,
    list_index,
    lookup_index,
    search_explore,
)
from tools.research_lab.strategies import scan_proof_strategies
from tools.research_lab.theory_map import theory_modules


def test_explore_list_and_lexical_catalog_search(capsys):
    rows = list_index()
    ids = {row["id"] for row in rows}
    assert "overview" in ids
    assert "notebook:projected" in ids
    assert "session:projected" in ids
    assert "strategy:induction" in ids
    assert "evolution" in ids
    assert "frontier" in ids
    assert "erdos:3" in ids
    assert main(["explore", "--list", "--format", "markdown"]) == 0
    listed = capsys.readouterr().out
    assert "| id | group | title |" in listed
    assert "`strategy:induction`" in listed
    hits = search_explore("ALG-004")
    assert hits["embeddings"] is False
    assert hits["status"] == "candidate"
    assert hits["wrote_canonical"] is False
    assert hits["count"] >= 1
    assert all(item["status"] == "candidate" for item in hits["hits"])
    induction = search_explore("induction")
    assert any(item["id"] == "strategy:induction" for item in induction["hits"])
    assert search_explore("   ")["count"] == 0
    assert main(["search-explore", "--query", "induction"]) == 0
    compact = lookup_index("notebook:projected")
    assert compact is not None
    assert "Not Canonical" in compact["body"]
    assert lookup_index("session:projected")["group"] == "会话"


def test_proof_strategy_scan_is_lexical_and_not_a_proof(tmp_path: Path):
    (tmp_path / "M.lean").write_text(
        "private theorem hidden : True := by\n"
        "  induction n with\n"
        "  | zero => trivial\n"
        "\n"
        "theorem shown : True := by\n"
        "  induction n with\n"
        "  | zero => trivial\n"
        "\n"
        "theorem built (n : Nat) : True := by\n"
        "  intro\n"
        "  exact True.intro\n"
        "  -- uses odds as a named construction\n"
        "  have := odds n\n",
        encoding="utf-8",
    )
    corr = tmp_path / "c.yaml"
    corr.write_text(
        "theorems:\n"
        "  - id: A\n"
        "    lean_decl: shown\n"
        "    lean_file: M.lean\n"
        "  - id: B\n"
        "    lean_decl: hidden\n"
        "    lean_file: M.lean\n"
        "  - id: C\n"
        "    lean_decl: built\n"
        "    lean_file: M.lean\n",
        encoding="utf-8",
    )
    rows = {item["id"]: item for item in scan_proof_strategies(corr, lean_root=tmp_path)}
    assert "strategy:induction" in rows
    assert rows["strategy:induction"]["successfulCases"] == ["A"]
    assert rows["strategy:induction"]["not_a_proof"] is True
    assert "B" not in rows["strategy:induction"]["successfulCases"]
    assert rows["strategy:algebraic_construction"]["successfulCases"] == ["C"]
    assert "compactness" not in {item["strategy"] for item in rows.values()}
    lab = explore_briefing()
    names = {item["strategy"] for item in lab["strategies"]}
    assert "induction" in names
    assert "compactness" not in names
    by_id = {item["id"]: item for item in lab["strategies"]}
    assert "ALG-004" in by_id["strategy:induction"]["successfulCases"]
    assert "DISC-003" in by_id["strategy:algebraic_construction"]["successfulCases"]
    assert lab["notebook"]["canonical"] is False
    assert lab["session"]["conclusion_is_theorem"] is False


def test_theory_modules_claim_no_evolution_edges(tmp_path: Path):
    path = tmp_path / "c.yaml"
    path.write_text(
        "theorems:\n"
        "  - id: A\n"
        "    lean_file: Foo.lean\n"
        "  - id: B\n"
        "    lean_file: Foo.lean\n"
        "  - id: C\n"
        "    lean_file: Bar.lean\n",
        encoding="utf-8",
    )
    graph = theory_modules(path)
    assert graph["claims_evolution"] is False
    assert graph["edges"] == []
    assert graph["not_a_theorem"] is True
    assert [node["id"] for node in graph["nodes"]] == ["theory:Bar.lean", "theory:Foo.lean"]
    lab = explore_briefing()
    assert lab["evolution"]["edges"] == []
    assert lab["evolution"]["claims_evolution"] is False
    assert lab["counts"]["evolution_nodes"] >= 4
    item = lookup_index("evolution")
    assert item is not None
    assert "proves_theorem: false" in item["body"]
    assert "No extends/simplifies/unifies/specializes is claimed" in item["body"]


def test_erdos_frontier_is_open_pointer_not_a_theorem():
    from tools.research_lab.frontier_catalog import (
        ERDOS_PIN,
        ERDOS_VENDOR,
        ERDOS_YAML,
        UPSTREAM_TRACKED_FILES,
        erdos_index_in_sync,
        erdos_vendor_ok,
        load_erdos_index,
        load_erdos_index_json,
        load_vendor_problems,
        read_upstream_pin,
    )

    assert erdos_vendor_ok() is True
    assert erdos_index_in_sync() is True
    assert ERDOS_YAML == ERDOS_VENDOR / "data" / "problems.yaml"
    assert ERDOS_YAML.is_file()
    assert len(UPSTREAM_TRACKED_FILES) == 30
    assert all((ERDOS_VENDOR / rel).is_file() for rel in UPSTREAM_TRACKED_FILES)
    assert read_upstream_pin() == ERDOS_PIN
    assert not (ERDOS_VENDOR / "data" / "additive_combinatorics.yaml").exists()
    assert len(load_vendor_problems()) == 1217
    data = load_erdos_index()
    assert data["writes_canonical"] is False
    assert data["network"] is False
    assert data["not_a_theorem"] is True
    assert data["source"] == "vendor/erdosproblems/data/problems.yaml"
    assert data["scope_tag"] == "additive combinatorics"
    assert data["pin"] == ERDOS_PIN
    assert data["counts"]["vendor_records"] == 1217
    assert data["counts"]["additive_records"] == 103
    assert data["counts"]["open_questions"] == 49
    assert data["counts"]["audit_records"] == 54
    questions = data["questions"]
    audit = data["audit"]
    assert all(item.get("not_a_theorem") is True for item in questions)
    assert all(item.get("not_a_theorem") is True for item in audit)
    assert all(item.get("not_an_open_question") is True for item in audit)
    assert all("statement" not in item for item in questions + audit)
    assert {item["id"] for item in questions} >= {"erdos:3"}
    assert {item["id"] for item in audit} >= {"erdos:1"}
    assert "erdos:1" not in {item["id"] for item in questions}
    mirrored = load_erdos_index_json()
    assert mirrored["questions"] == questions
    assert mirrored["audit"] == audit
    assert mirrored["counts"] == data["counts"]
    assert mirrored["source"] == data["source"]
    assert mirrored["pin"] == ERDOS_PIN
    report = explore_briefing()
    assert report["frontier"]["not_a_theorem"] is True
    assert report["counts"]["frontier_open"] == 49
    assert lookup_index("erdos:3")["group"] == "前沿"
    assert "Not a theorem" in lookup_index("erdos:3")["body"]
    assert "erdosproblems.com/3" in lookup_index("erdos:3")["body"]
    assert lookup_index("erdos:1")["group"] == "前沿备查"
    assert "not_an_open_question" in lookup_index("erdos:1")["body"]
    assert lookup_index("frontier-audit")["group"] == "前沿备查"
    hits = search_explore("erdos:3")
    assert hits["embeddings"] is False
    assert any(item["id"] == "erdos:3" and item["status"] == "candidate" for item in hits["hits"])
    nick_hits = search_explore("sum-product")
    assert any(item["id"] == "erdos:52" for item in nick_hits["hits"])

