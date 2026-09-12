from pathlib import Path

from tools.lean_formalization.constants import LEAN_ROOT
from tools.lean_formalization.correspondence import load_table, undeclared_theorems, validate_table
from tools.lean_formalization.doctor import doctor
from tools.lean_formalization.gate import GATE_METRIC_NAMES, evaluate_gate
from tools.lean_formalization.manifest import validate_manifest_file
from tools.lean_formalization.scan import scan_lean_text, scan_lean_tree
from tools.lean_formalization.weakening import detect_weakening


def test_sorry_and_admit_are_detected():
    hits = scan_lean_text("example : True := by\n  sorry\n", path="x.lean")
    kinds = {hit.kind for hit in hits}
    assert "sorry" in kinds
    hits = scan_lean_text("example : True := by admit\n")
    assert any(hit.kind == "admit" for hit in hits)


def test_new_axiom_is_detected():
    hits = scan_lean_text("axiom fake_proof : 1 = 0\n")
    assert any(hit.kind == "axiom" for hit in hits)


def test_sorry_in_comments_is_ignored():
    hits = scan_lean_text("-- sorry\nexample : True := rfl\n")
    assert hits == []
    hits = scan_lean_text("/- admit -/\ntheorem t : True := rfl\n")
    assert hits == []


def test_fixture_tree_detects_sorry(tmp_path: Path):
    root = Path(__file__).parent / "fixtures"
    hits = scan_lean_tree(root)
    kinds = {hit.kind for hit in hits}
    assert "sorry" in kinds
    assert "axiom" in kinds


def test_production_lean_has_no_sorry():
    hits = scan_lean_tree(LEAN_ROOT)
    assert hits == []


def test_correspondence_covers_two_families():
    table = load_table(LEAN_ROOT / "correspondence.yaml")
    result = validate_table(table, LEAN_ROOT)
    assert result.ok is True
    assert set(result.families) >= {"algebra", "discrete", "analysis"}
    assert undeclared_theorems(LEAN_ROOT, table) == []
    assert any(item.get("id") == "ANL-001" for item in table)
    assert any(item.get("id") == "DISC-004" for item in table)
    assert any(item.get("id") == "DISC-006" for item in table)
    alg004 = next(item for item in table if item.get("id") == "ALG-004")
    assert set(alg004.get("depends_on") or []) == {"ALG-002", "ALG-003"}
    anl004 = next(item for item in table if item.get("id") == "ANL-004")
    assert anl004.get("depends_on") == ["ANL-001"]


def test_unknown_depends_on_is_rejected():
    table = [dict(item) for item in load_table(LEAN_ROOT / "correspondence.yaml")]
    table[0] = dict(table[0])
    table[0]["depends_on"] = ["NO-SUCH-ID"]
    result = validate_table(table, LEAN_ROOT)
    assert result.ok is False
    assert any("depends_on unknown id" in item for item in result.errors)


def test_weakening_fixture_is_detected():
    root = Path(__file__).parent / "fixtures" / "weakened"
    entry = load_table(root / "correspondence.yaml")[0]
    text = (root / "weaker.lean").read_text(encoding="utf-8")
    issues = detect_weakening(entry, text)
    assert any("quantifier" in item for item in issues)
    assert any("inequality" in item for item in issues)


def test_manifests_match_current_sources():
    for path in sorted((LEAN_ROOT / "manifests").glob("*.yaml")):
        result = validate_manifest_file(path, LEAN_ROOT)
        assert result.ok is True, (path.name, result.errors)


def test_stale_manifest_hash_is_rejected(tmp_path: Path):
    import yaml

    sample = next((LEAN_ROOT / "manifests").glob("*.yaml"))
    data = yaml.safe_load(sample.read_text(encoding="utf-8"))
    data["source_files"][0]["sha256"] = "0" * 64
    broken = tmp_path / "broken.yaml"
    broken.write_text(yaml.safe_dump(data), encoding="utf-8")
    result = validate_manifest_file(broken, LEAN_ROOT)
    assert result.ok is False
    assert any("stale sha256" in item for item in result.errors)


def test_gate_degrades_without_failing_core():
    report = evaluate_gate()
    names = [item["name"] for item in report["metrics"]]
    assert names == list(GATE_METRIC_NAMES)
    assert report["core_impact"] is False
    assert report["status"] in {"PASS", "DEGRADED"}
    assert all(item["status"] != "FAIL" for item in report["metrics"] if item["name"] != "lake_build_pass_rate")
    lake = next(item for item in report["metrics"] if item["name"] == "lake_build_pass_rate")
    assert lake["status"] in {"PASS", "DEGRADED"}


def test_elan_bin_is_home_elan():
    from tools.lean_formalization.build import elan_bin

    assert elan_bin() == Path.home() / ".elan" / "bin"


def test_lake_manifest_stays_lf_after_build():
    from tools.lean_formalization.build import lake_available, run_lake_build
    from tools.lean_formalization.constants import LEAN_ROOT

    manifest = LEAN_ROOT / "lake-manifest.json"
    if lake_available():
        run_lake_build(LEAN_ROOT)
    data = manifest.read_bytes()
    assert b"\r\n" not in data


def test_build_missing_lake_is_degraded():
    from tools.lean_formalization.build import lake_available, run_lake_build

    result = run_lake_build(LEAN_ROOT)
    if lake_available():
        assert result.status in {"SUCCEEDED", "FAILED", "CANCELLED", "DEGRADED"}
        assert result.core_impact is False
    else:
        assert result.status == "DEGRADED"
        assert result.core_impact is False


def test_doctor_never_blocks_core():
    report = doctor()
    assert report["core_impact"] is False
    assert report["status"] in {"PASS", "DEGRADED"}


def test_cli_doctor():
    from tools.lean_formalization.cli import main

    assert main(["doctor"]) == 0
    assert main(["scan", "--help"]) == 0
